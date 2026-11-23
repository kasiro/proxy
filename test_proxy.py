from sys import exit
import re
import json
import os
from types import NoneType
from urllib.parse import urlparse
from sseclient import SSEClient # type: ignore
from pprint import pprint
import requests as rq
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from fastapi import FastAPI, Request, Response # type: ignore
from fastapi.responses import StreamingResponse, JSONResponse # type: ignore
import threading
import asyncio
from accaunts import ACCOUNTS
from utils import curl_to_python, extract_account_ids_from_accounts

# Debug mode: включать логи запросов на консоль
DEBUG_MODE = os.environ.get("PROXY_DEBUG", "0") == "1"

# Импорт клиента статистики
try:
    from stats_client import record_request, record_request_async, init_db, init_accounts, is_account_available, check_daily_reset
    STATS_ENABLED = True
except ImportError:
    STATS_ENABLED = False
    print("[stats] Модуль stats_client не найден, статистика отключена")

class BanDetectedException(Exception):
    """Исключение для сигнала о бане аккаунта."""
    pass


def check_account_ban(final_response: dict) -> bool:
    """Проверяет бан по message в final_response."""
    choices = final_response.get('choices') or []
    if not choices:
        return False
    message = choices[0].get('message', '')
    if isinstance(message, str) and 'заблокирован' in message:
        print(f"[ban_check] Account blocked: message='{message[:100]}'")
        raise BanDetectedException(f"Account '{get_current_account_id()}' is banned")
    return False


# добавить tools, mcp, skills

app = FastAPI()

current_acc_index = 0  # индекс текущего аккаунта в списке ACCOUNTS

# Список моделей для эндпоинта /v1/models
MODELS_LIST = [
    {"id": "free-minimax-m2.7", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "free-gemini-2.5-pro", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "free-claude-haiku-4-5-20251001", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "free-gemini-2.5-flash", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "free-qwen3.5-plus", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "free-qwen3.5-flash", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "free-minimax-m2.5", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "free-gemini-2.5-flash-lite", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "free-gemini-3-flash-preview", "object": "model", "created": 1788893105, "owned_by": "opencode"},
]


def strip_think_tags(text: str) -> str:
    """Удаляет блоки <think>...</think>

 из текста."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)


def safe_print_payload(payload: dict, hide_tools: bool = True) -> None:
    """Безопасный вывод payload — исключает tools и системные промпты."""
    safe_copy = payload.copy()
    
    # Удаляем tools если есть
    if 'tools' in safe_copy and hide_tools:
        safe_copy['tools'] = '<REDACTED>'
    
    # Фильтруем messages, убирая сообщения с role='system'
    if 'messages' in safe_copy:
        safe_copy['messages'] = [
            msg for msg in safe_copy['messages']
            if msg.get('role') != 'system'
        ]
    
    print(json.dumps(safe_copy, indent=2, ensure_ascii=False))


@app.get("/v1/models")
async def models_list():
    """Вернуть список моделей в формате OpenAI."""
    return {"object": "list", "data": MODELS_LIST}

def strip_think_from_sse_line(line: str) -> str:
    """Парсит SSE data строку и удаляет <think> теги из content delta."""
    if not line.startswith('data: '):
        return line
    payload = line[6:]
    if payload.strip() == '[DONE]':
        return line
    try:
        data = json.loads(payload)
        for choice in data.get('choices', []):
            delta = choice.get('delta', {})
            content = delta.get('content')
            if isinstance(content, str) and content:
                cleaned = strip_think_tags(content)
                if cleaned != content:
                    delta['content'] = cleaned
                    return 'data: ' + json.dumps(data, ensure_ascii=False)
    except (json.JSONDecodeError, ValueError):
        pass
    return line

def stream_generator(line_iter, first_line, resp, account_id, model, input_tokens, current_account_id):
    """
    Прямая потоковая отдача SSE без накопления в память.

    Первый чанк (first_line) уже был peek'нут в handler'е — отдаём его первым.
    Каждый чанк проверяется на JSON с "заблокирован":
      - если бан найден mid-stream (headers уже отправлены, аккаунт не переключить)
        → отдаём SSE-ошибку и завершаем поток.
    """
    output_tokens = 0
    try:
        # 1. Отдать peek'нутый первый чанк
        if first_line is not None:
            line_str = first_line.decode() if isinstance(first_line, bytes) else first_line
            if line_str.strip():
                if line_str.strip() == 'data: [DONE]':
                    yield f'data: {json.dumps({"done": True})}\n\n'
                    return
                if line_str.startswith('data: '):
                    line_str = strip_think_from_sse_line(line_str)
                yield line_str + '\n\n'

        # 2. Стримить остаток напрямую (без list/append)
        for line in line_iter:
            if not line:
                continue

            line_str = line.decode() if isinstance(line, bytes) else line

            # Non-SSE JSON — проверка на бан
            if not line_str.startswith('data:') and line_str.strip():
                try:
                    json_data = json.loads(line_str)
                    msg = json_data.get('message', '')
                    if isinstance(msg, str) and 'заблокирован' in msg:
                        print(f"[banned] Бан в mid-stream (JSON): {msg}")
                        yield f'data: {json.dumps({"error": "Account is banned"}, ensure_ascii=False)}\n\n'
                        yield 'data: [DONE]\n\n'
                        return
                except json.JSONDecodeError:
                    pass

            if line_str.strip() == 'data: [DONE]':
                yield f'data: {json.dumps({"done": True})}\n\n'
                return

            # SSE чанк — фильтр think-тегов + проверка на бан в content + usage
            if line_str.startswith('data: '):
                line_str = strip_think_from_sse_line(line_str)
                try:
                    payload_str = line_str[6:]
                    if payload_str.strip() != '[DONE]':
                        data = json.loads(payload_str)

                        # Проверка бана в message.content
                        for choice in data.get('choices', []):
                            msg = choice.get('message', {})
                            content = msg.get('content')
                            if isinstance(content, str) and 'заблокирован' in content:
                                print(f"[banned] Бан в SSE чанке: {content}")
                                yield f'data: {json.dumps({"error": "Account is banned"}, ensure_ascii=False)}\n\n'
                                yield 'data: [DONE]\n\n'
                                return

                        # Попытка достать usage (если upstream прислал)
                        usage = data.get('usage') or {}
                        if usage:
                            output_tokens = (
                                usage.get('completion_tokens')
                                or usage.get('output_tokens')
                                or output_tokens
                            )
                except (json.JSONDecodeError, ValueError):
                    pass

            yield line_str + '\n\n'
    finally:
        # Закрыть upstream-соединение
        try:
            resp.close()
        except Exception:
            pass
        # Записать статистику
        if STATS_ENABLED:
            threading.Thread(
                target=record_request,
                args=(account_id, 200, model, input_tokens, output_tokens),
                daemon=True,
            ).start()

# Извлечение account_id из всех аккаунтов при старте
ACCOUNT_IDS = extract_account_ids_from_accounts(ACCOUNTS)

def get_current_account_id() -> str:
    """Получить ID текущего аккаунта из предзагруженного списка."""
    return ACCOUNT_IDS[current_acc_index]


all_ = curl_to_python(ACCOUNTS[current_acc_index])
TARGET_URL = all_['url']
session = rq.Session()
session.headers.update(all_['headers'])
session.cookies.update(all_['cookies'])
session.trust_env = False  # Игнорировать HTTP_PROXY/HTTPS_PROXY и системные настройки
session.proxies.clear()  # Явно очистить любые прокси

# Retry-политика для транспортных сбоев (502/503/504 и обрывы соединения)
_adapter = HTTPAdapter(max_retries=Retry(total=2, backoff_factor=0.5, status_forcelist=[502, 503, 504]))
session.mount('http://', _adapter)
session.mount('https://', _adapter)

# Инициализация БД статистики при старте
if STATS_ENABLED:
    init_db()  # type: ignore
    # Инициализируем БД реальными аккаунтами (добавит отсутствующие с request_count=0)
    init_accounts(ACCOUNT_IDS)  # type: ignore
    check_daily_reset()  # type: ignore
    print(f"[stats] БД статистики инициализирована: {len(ACCOUNT_IDS)} аккаунтов")

    # Найти первый доступный аккаунт
    for i, acc_id in enumerate(ACCOUNT_IDS):
        if is_account_available(acc_id):  # type: ignore
            current_acc_index = i
            print(f"[stats] Начинаем с аккаунта {i+1} (account_{acc_id})")
            break
    else:
        print("[stats] Все аккаунты исчерпаны, начинаем с первого")

    # Обновить session для выбранного аккаунта
    parsed = curl_to_python(ACCOUNTS[current_acc_index])
    TARGET_URL = parsed['url']
    session.headers.clear()
    session.cookies.clear()
    session.headers.update(parsed['headers'])
    session.cookies.update(parsed['cookies'])


def switch_account():
    """Переключает на следующий доступный аккаунт (пропускает исчерпанные)."""
    global current_acc_index
    start = current_acc_index

    for _ in range(len(ACCOUNTS)):
        current_acc_index = (current_acc_index + 1) % len(ACCOUNTS)
        acc_id = ACCOUNT_IDS[current_acc_index]

        # if STATS_ENABLED:
        #     if not is_account_available(acc_id):  # type: ignore
        #         continue  # Пропускать исчерпанный

        # Нашли доступный — обновляем session
        parsed = curl_to_python(ACCOUNTS[current_acc_index])
        session.headers.clear()
        session.cookies.clear()
        session.headers.update(parsed['headers'])
        session.cookies.update(parsed['cookies'])
        print(f"[retry] Переключён на аккаунт {current_acc_index + 1}/{len(ACCOUNTS)} (account_{acc_id})", flush=True)
        return

    # Все исчерпаны
    print("[retry] Все аккаунты исчерпаны", flush=True)


def format_tools_for_prompt(tools: list) -> str:
    """Преобразует массив tools (OpenAI-формат) в человекочитаемый список."""
    if not tools:
        return "_Нет доступных инструментов._"

    lines = ["### available_tools:"]
    for tool in tools:
        func = tool.get("function", {})
        name = func.get("name", "unknown")
        desc = func.get("description", "нет описания")
        params = func.get("parameters", {})
        props = params.get("properties", {})
        required = params.get("required", [])

        lines.append(f"- `{name}` — {desc}")
        if props:
            lines.append("  Параметры:")
            for pname, pschema in props.items():
                ptype = pschema.get("type", "string")
                pdesc = pschema.get("description", "")
                req_tag = "required" if pname in required else "optional"
                # Если enum — показать варианты
                enum_vals = pschema.get("enum")
                if enum_vals:
                    pdesc += f" (варианты: {', '.join(str(v) for v in enum_vals)})"
                lines.append(f"  - `{pname}` ({ptype}, {req_tag}): {pdesc}" if pdesc else f"  - `{pname}` ({ptype}, {req_tag})")

    return "\n".join(lines)


def build_tool_format_spec() -> str:
    """Инструкция по формату JSON tool calls."""
    return """## Формат tool calls — JSON

Для вызова инструментов используй JSON формат:

{
  "tool_calls": [
    {
      "id": "call_xxx",
      "type": "function",
      "function": {
        "name": "имя_инструмента",
        "arguments": "{\\"параметр\\": \\"значение\\"}"
      }
    }
  ]
}

Правила:
- id должен быть уникальным (например: call_abc123)
- arguments - ВСЕГДА JSON строка (даже если пустой объект {})
- Несколько инструментов - несколько объектов в массиве tool_calls

Примеры:

**memory_set:**
{"tool_calls": [{"id": "call_abc123","type": "function","function": {"name": "memory_set","arguments": "{\\"label\\": \\"lessons\\", \\"value\\": \\"- [2026-08-31] запись урока\\", \\"scope\\": \\"global\\"}"}}]}

**sequential-thinking:**
{"tool_calls": [{"id": "call_def456","type": "function","function": {"name": "sequential-thinking_sequentialthinking","arguments": "{\\"thought\\": \\"Анализирую задачу...\\", \\"nextThoughtNeeded\\": true, \\"thoughtNumber\\": 1, \\"totalThoughts\\": 3}"}}]}

**skill:**
{"tool_calls": [{"id": "call_ghi789","type": "function","function": {"name": "skill","arguments": "{\\"name\\": \\"system-reports\\"}"}}]}

**task:**
{"tool_calls": [{"id": "call_jkl012","type": "function","function": {"name": "task", "arguments": "{\\"description\\": \\"Краткое описание\\", \\"prompt\\": \\"Подробный промпт\\", \\"subagent_type\\": \\"general\\"}"}}]}"""


def build_system_prompt(tools: list, client_data: dict) -> str:
    """Генерирует system prompt с описанием инструментов и формата JSON."""
    tools_text = format_tools_for_prompt(tools)
    tool_spec = build_tool_format_spec()

    prompt = f"""Ты — AI-ассистент, работающий через OpenCode. Ты ОБЯЗАН генерировать вызовы инструментов через tool calls в формате JSON (см. ниже), когда это необходимо.

## Доступные инструменты

{tools_text}

{tool_spec}

## Важные правила

1. ВСЕГДА используй JSON формат для вызова инструментов. НЕ вызывай инструменты описанием текстом.
2. Для инструментов с параметрами — ВСЕГДА передавай все обязательные параметры.
3. Если параметр — объект/массив, передавай его как JSON в поле arguments.
4. Для числовых параметров (thoughtNumber, totalThoughts и т.д.) — передавай как есть в JSON (без кавычек для чисел/булевых).
5. Можно вызывать НЕСКОЛЬКО инструментов в одном tool_calls массиве.
6. Не генерируй tool_calls если пользователь просто здоровается или задаёт простой вопрос без необходимости в инструментах.
7. Отвечай на русском языке, если не попросят иное."""

    return prompt

def not_is_None(obj) -> bool:
    return not obj is None and not obj is NoneType

@app.post('/v1/chat/completions')
async def proxy(request: Request):
    global current_acc_index, TARGET_URL
    # start:
    client_data = await request.json()
    
    # --- Поддержка выбора аккаунта по заголовку X-Test-Account-ID ---
    account_id_from_header = request.headers.get('x-test-account-id')
    is_test_request = bool(account_id_from_header)
    if account_id_from_header:
        if account_id_from_header in ACCOUNT_IDS:
            target_index = ACCOUNT_IDS.index(account_id_from_header)
            current_acc_index = target_index
            print(f"[proxy] Выбран аккаунт по заголовку: {account_id_from_header} (index {current_acc_index + 1}/{len(ACCOUNT_IDS)})")
            # Обновить session для выбранного аккаунта
            parsed = curl_to_python(ACCOUNTS[current_acc_index])
            TARGET_URL = parsed['url']
            session.headers.clear()
            session.cookies.clear()
            session.headers.update(parsed['headers'])
            session.cookies.update(parsed['cookies'])
        else:
            print(f"[proxy] Валидный заголовок X-Test-Account-ID: '{account_id_from_header}' не найден в ACCOUNT_IDS")
    
    # Можно принимать от клиента messages, остальное подставляем
    payload = {
        "group": client_data.get("group", "default"),
        "messages": client_data["messages"],
        "model": client_data.get("model", "free-minimax-m2.7"),
        "stream": client_data.get("stream", True)
    }

    # Пробросить tools в payload для совместимости с upstream API
    tools = client_data.get('tools', []) if client_data else []
    if tools:
        # добавить фильтрацию tools при надобности
        payload['tools'] = tools

    # Построить system prompt с инструментами
    if tools and payload["model"] != 'free-qwen3.5-plus':
        system_prompt = build_system_prompt(tools, client_data)
    else:
        system_prompt = 'Ты — AI-ассистент. Отвечай на русском языке.'

    # Добавить/заменить system message
    if payload['messages'][0]['role'] == 'system':
        payload['messages'][0]['content'] = system_prompt + '\n\n' + payload['messages'][0]['content']
    else:
        payload['messages'].insert(0, {'role': 'system', 'content': system_prompt})

    if DEBUG_MODE:
        safe_print_payload(client_data)
        # safe_print_payload(payload)

    # --- Retry при 429: перебираем ВСЕ аккаунты по кругу ---
    resp = None
    # Извлекаем модель и токены (до цикла retry)
    model = client_data.get("model", "unknown")
    input_tokens = 0
    for msg in client_data.get("messages", []):
        if not_is_None(msg):
            content = msg.get('content', '')
            if not_is_None(content):
                input_tokens += len(content)

    output_tokens = 0  # Будет посчитано из ответа
    account_id = get_current_account_id()
    current_account_id = 'account_' + ACCOUNT_IDS[current_acc_index]

    for attempt in range(len(ACCOUNTS)):
        resp = session.post(TARGET_URL, json=payload, stream=payload.get('stream', True), timeout=180)
        
        if resp.status_code != 200:
            json_ = resp.json()
            mess = json_.get('message', 'None')
            if mess == 'None':
                mess = json_.get('error', 'None')
            
            # Обработка [429, 401] как "аккаунт исчерпан/требует реавторизации"
            if resp.status_code in [429, 401]:
                code_name = "429 Too Many Requests" if resp.status_code == 429 else "401 Unauthorized"
                print(f"[retry] Аккаунт {current_account_id} ({current_acc_index + 1}) вернул {resp.status_code} ({code_name}) (попытка {attempt + 1}/{len(ACCOUNTS)})")
                if DEBUG_MODE:
                    print(f"[proxy] Response: {resp.status_code} (аккаунт {current_acc_index + 1})", flush=True)
                # Запись 429/401 в статистику
                if STATS_ENABLED:
                    await record_request_async(account_id, resp.status_code, model, input_tokens, output_tokens)  # type: ignore
                
                if attempt < len(ACCOUNTS) - 1 and not is_test_request:
                    switch_account()
                    current_account_id = 'account_' + ACCOUNT_IDS[current_acc_index]
                    continue
                else:
                    print(f"[retry] Все аккаунты исчерпаны / тестовый режим, возвращаем {resp.status_code} клиенту")
                    if DEBUG_MODE:
                        print(f"[proxy] Response: {resp.status_code} (все аккаунты исчерпаны / тестовый режим)", flush=True)
                    return Response(
                        content=json.dumps({"error": "rate_limit_exceeded" if resp.status_code == 429 else "unauthorized", "detail": f"Все аккаунты вернули {resp.status_code}"}),
                        status_code=resp.status_code
                    )
            
            # Остальные ошибки (не 429/401) — просто выводим и прекращаем попытки
            print(f"[retry] Аккаунт {current_account_id} ({current_acc_index + 1}) вернул {resp.status_code} ({mess}) (попытка {attempt + 1}/{len(ACCOUNTS)})")
            if DEBUG_MODE:
                print(f"[proxy] Response: {resp.status_code} (аккаунт {current_acc_index + 1})", flush=True)
            if STATS_ENABLED:
                await record_request_async(account_id, resp.status_code, model, input_tokens, output_tokens)  # type: ignore
            
            print(f"[retry] Прерываю цикл из-за статуса {resp.status_code} (не 429/401)")
            break
        if resp.status_code == 200:
            if payload.get('stream') == False:
                try:
                    json_ = json.loads(resp.content.decode())
                except (json.JSONDecodeError, ValueError):
                    print(f"[proxy] Не-JSON тело upstream ({resp.status_code})")
                    return Response(content=resp.content, status_code=resp.status_code)
                mess = json_.get('message', 'None')
                if mess != 'None':
                    if 'заблокирован' in mess:
                        print(f"[banned] Аккаунт {current_account_id} ({current_acc_index + 1}) забанен. ({mess}) (попытка {attempt + 1}/{len(ACCOUNTS)})")
                        if attempt < len(ACCOUNTS) - 1 and not is_test_request:
                            switch_account()
                            current_account_id = 'account_' + ACCOUNT_IDS[current_acc_index]
                            continue
                        else:
                            print(f"[retry] Бан найден в тестовом режиме / все аккаунты исчерпаны, возвращаем {resp.status_code} клиенту")
                            if DEBUG_MODE:
                                print(f"[proxy] Response: {resp.status_code} (все аккаунты исчерпаны)", flush=True)
                            return Response(
                                content=json.dumps({"error": "Account is banned", "detail": f"Аккаунт забанен"}, ensure_ascii=False),
                                status_code=403
                            )
            if DEBUG_MODE:
                print(f"[proxy] Response: 200 OK (аккаунт {current_acc_index + 1})", flush=True)
            break  # Нормальный ответ — выходим из цикла

        if resp.status_code not in [200]:
            # Запись других ошибок
            if STATS_ENABLED:
                await record_request_async(account_id, resp.status_code, model, input_tokens, output_tokens)  # type: ignore
            if DEBUG_MODE:
                print(f"[proxy] Response: {resp.status_code} (аккаунт {current_acc_index + 1})", flush=True)
            return Response(
                content=resp.content,
                status_code=resp.status_code
            )


    # Обработка ошибок в stream режиме — если 401 или 429, это бан
    if resp.status_code in [429, 401]: # type: ignore
        code_name = "rate_limit_exceeded" if resp.status_code == 429 else "unauthorized"
        print(f"[retry] Стрим: Аккаунт {current_account_id} вернул {resp.status_code} ({code_name})")
        raise BanDetectedException(f"Account '{get_current_account_id()}' returned {resp.status_code}") # type: ignore
    elif resp.status_code != 200: # type: ignore
        # Ошибка другого типа — возвращаем клиенту
        return Response(content=resp.text, status_code=resp.status_code) # type: ignore
    # print(f"Status: {resp.status_code}")
    if payload.get('stream', True):
        # --- Stream handling with retry loop for ban detection ---
        # Не накапливаем чанки в память. Делаем только peek первого чанка,
        # чтобы отловить бан-JSON (upstream при бане отдаёт HTTP 200 + обычный
        # JSON {"message": "Пользователь заблокирован", ...} даже при stream=true).
        max_attempts = len(ACCOUNTS)

        for attempt in range(max_attempts):
            if attempt > 0:
                print(f"[retry] Stream retry #{attempt}/{max_attempts} после бана")
                try:
                    resp.close()
                except Exception:
                    pass
                resp = session.post(TARGET_URL, json=payload, stream=True, timeout=180)

                if resp.status_code != 200:
                    print(f"[retry] Аккаунт {current_account_id} вернул {resp.status_code}, пробуем следующий")
                    switch_account()
                    account_id = get_current_account_id()
                    current_account_id = 'account_' + ACCOUNT_IDS[current_acc_index]
                    continue

            # --- Peek первого чанка: ловим бан-JSON ---
            line_iter = resp.iter_lines(decode_unicode=False)
            first_line = next(line_iter, None)
            ban_found = False

            if first_line:
                first_str = first_line.decode() if isinstance(first_line, bytes) else first_line
                if not first_str.startswith('data:') and first_str.strip():
                    try:
                        json_data = json.loads(first_str)
                        msg = json_data.get('message', '')
                        if isinstance(msg, str) and 'заблокирован' in msg:
                            print(f"[banned] Запрещённый ответ от upstream (JSON): {msg}")
                            ban_found = True
                    except json.JSONDecodeError:
                        pass

            if ban_found:
                try:
                    resp.close()
                except Exception:
                    pass

                if is_test_request:
                    print(f"[retry] Бан детектирован (тестовый режим), аккаунт не переключается")
                    err_body = (
                        'data: ' + json.dumps({"error": "Account is banned"}, ensure_ascii=False) + '\n\n'
                        + 'data: [DONE]\n\n'
                    )
                    return Response(
                        content=err_body,
                        status_code=403,
                        media_type='text/event-stream',
                    )

                print(f"[retry] Бан детектирован. Переключаем аккаунт...")
                switch_account()
                account_id = get_current_account_id()
                current_account_id = 'account_' + ACCOUNT_IDS[current_acc_index]
                continue

            # --- Бана нет: стримим напрямую, без накопления ---
            return StreamingResponse(
                stream_generator(
                    line_iter=line_iter,
                    first_line=first_line,
                    resp=resp,
                    account_id=account_id,
                    model=model,
                    input_tokens=input_tokens,
                    current_account_id=current_account_id,
                ),
                status_code=resp.status_code,
                media_type='text/event-stream',
            )

        # Все попытки исчерпаны
        print("[retry] Все аккаунты исчерпаны после банов")
        err_body = (
            'data: ' + json.dumps({"error": "All accounts are banned"}, ensure_ascii=False) + '\n\n'
            + 'data: [DONE]\n\n'
        )
        return Response(
            content=err_body,
            status_code=403,
            media_type='text/event-stream',
        )


    else:
        # Если стриминг выключен – возвращаем обычный JSON, но преобразуем
        raw_response = resp.text # type: ignore
        data = None
        try:
            data = json.loads(raw_response)
            # Извлекаем токены из non-stream ответа
            usage = data.get('usage', {})
            output_tokens = usage.get('completion_tokens', 0) or usage.get('output_tokens', 0)
            input_tokens = usage.get('prompt_tokens', input_tokens) or usage.get('input_tokens', input_tokens)
        except json.JSONDecodeError:
            pass

        # Запись статистики ВНЕ try/except — вызывается ВСЕГДА
        if STATS_ENABLED:
            await record_request_async(account_id, 200, model, input_tokens, output_tokens)  # type: ignore

        if data and 'choices' in data and data['choices']:
            message = data['choices'][0].get('message', {})
            if 'tool_calls' in message:
                # Уже в нужном формате, просто возвращаем
                return Response(content=raw_response, status_code=resp.status_code) # type: ignore
            # Иначе, возможно, модель вернула текст с вызовом в виде тегов
            content = message.get('content', '')
            content = strip_think_tags(content)
            message['content'] = content
            # Попробуем найти JSON внутри текста (например, {"tool_calls": ...})
            match = re.search(r'(\{"tool_calls":\s*\[.*\]\})', content, re.DOTALL)
            if match:
                tool_call_json = match.group(1)
                # Заменяем content на этот JSON и добавляем tool_calls в message
                new_message = message.copy()
                new_message['content'] = None  # или убираем
                try:
                    new_message['tool_calls'] = json.loads(tool_call_json)['tool_calls']
                except (json.JSONDecodeError, ValueError):
                    # Неполный захват JSON — возвращаем исходный ответ без преобразования
                    return Response(content=raw_response, status_code=resp.status_code) # type: ignore
                data['choices'][0]['message'] = new_message
                return Response(content=json.dumps(data), status_code=resp.status_code) # type: ignore
        # Если ничего не нашли, возвращаем как есть
        return Response(content=raw_response, status_code=resp.status_code) # type: ignore
