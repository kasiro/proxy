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
    message = final_response.get('choices', [{}])[0].get('message', '')
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
    # {"id": "free-gpt-5.4-mini", "object": "model", "created": 1788893105, "owned_by": "opencode"},
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
                json_ = json.loads(resp.content.decode())
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
        stop_flag = threading.Event()

        async def check_disconnect():
            while not stop_flag.is_set():
                if await request.is_disconnected():
                    stop_flag.set()
                    break
                await asyncio.sleep(0.5)

        # Запускаем задачу проверки
        asyncio.create_task(check_disconnect())

        # Контейнер для сбора токенов из SSE
        usage_data = {'input_tokens': input_tokens, 'output_tokens': 0}

        def collect_and_check_stream():
            """Собирает весь SSE поток, проверяет на бан, возвращает накопленный результат."""
            accumulator = {'choices': [], 'usage': None}
            
            for line in resp.iter_lines(decode_unicode=False): # type: ignore
                if line:
                    line = line.decode()
                    
                    # ПРОВЕРКА НА JSON С БАНOM (до проверки [DONE])
                    if not line.startswith('data:') and line.strip():
                        try:
                            json_data = json.loads(line)
                            msg = json_data.get('message', '')
                            if isinstance(msg, str) and 'заблокирован' in msg:
                                print(f"[banned] Запрещённый ответ от upstream (JSON): {msg}")
                                raise BanDetectedException(f"Account '{get_current_account_id()}' is banned")
                        except json.JSONDecodeError:
                            pass
                    
                    if line.strip() == 'data: [DONE]':
                        # Проверяем аккаунт на бан после завершения потока
                        if check_account_ban(accumulator):
                            raise BanDetectedException(f"Account '{get_current_account_id()}' is banned after full response")
                        
                        yield f'data: {json.dumps({"done": True})}\n\n'
                        break
                    
                    # Извлечение usage и accumulation choices из SSE
                    if line.startswith('data: '):
                        # Фильтрация <think> тегов
                        line_content = strip_think_from_sse_line(line)
                        # Парсинг
                        try:
                            payload_str = line[6:]  # убираем 'data: '
                            if payload_str.strip() != '[DONE]':
                                data = json.loads(payload_str)
                                
                                # Проверка бана в КАЖДОМ choice текущего чанка
                                for choice in data.get('choices', []):
                                    msg = choice.get('message', {})
                                    content = msg.get('content')
                                    if isinstance(content, str) and 'заблокирован' in content:
                                        print(f"[banned] Найдено 'заблокирован' в SSE чанке: {content}")
                                        raise BanDetectedException(f"Account '{account_id}' is banned in chunk")
                                
                                # Накопление choices
                                if 'choices' in data and data['choices']:
                                    accumulator['choices'].extend(data['choices'])
                                
                                # Сохраняем usage
                                usage = data.get('usage', {})
                                if usage:
                                    accumulator['usage'] = usage
                                    usage_data['output_tokens'] = usage.get('completion_tokens', 0) or usage.get('output_tokens', 0)
                                    usage_data['input_tokens'] = usage.get('prompt_tokens', usage_data['input_tokens']) or usage.get('input_tokens', usage_data['input_tokens'])
                                    
                        except (json.JSONDecodeError, ValueError):
                            pass
                    
                    yield line + '\n\n' # type: ignore
            
            # Запись статистики
            if STATS_ENABLED:
                threading.Thread(
                    target=record_request,
                    args=(account_id, 200, model, usage_data['input_tokens'], usage_data['output_tokens']),
                    daemon=True
                ).start()

        def collect_and_check_stream_with_usage(resp_obj, usage_dict):
            """Аналогично collect_and_check_stream, но принимает usage_dict как параметр."""
            accumulator = {'choices': [], 'usage': None}
            
            for line in resp_obj.iter_lines(decode_unicode=False): # type: ignore
                if line:
                    line = line.decode()
                    
                    # ПРОВЕРКА НА JSON С БАНOM (до проверки [DONE])
                    if not line.startswith('data:') and line.strip():
                        try:
                            json_data = json.loads(line)
                            msg = json_data.get('message', '')
                            if isinstance(msg, str) and 'заблокирован' in msg:
                                print(f"[banned] Запрещённый ответ от upstream (JSON): {msg}")
                                raise BanDetectedException(f"Account '{get_current_account_id()}' is banned")
                        except json.JSONDecodeError:
                            pass
                    
                    if line.strip() == 'data: [DONE]':
                        # Проверяем аккаунт на бан после завершения потока
                        if check_account_ban(accumulator):
                            raise BanDetectedException(f"Account '{get_current_account_id()}' is banned after full response")
                        
                        yield f'data: {json.dumps({"done": True})}\n\n'
                        break
                    
                    # Извлечение usage и accumulation choices из SSE
                    if line.startswith('data: '):
                        # Фильтрация <think> тегов
                        line_content = strip_think_from_sse_line(line)
                        # Парсинг
                        try:
                            payload_str = line[6:]  # убираем 'data: '
                            if payload_str.strip() != '[DONE]':
                                data = json.loads(payload_str)
                                
                                # Проверка бана в КАЖДОМ choice текущего чанка
                                for choice in data.get('choices', []):
                                    msg = choice.get('message', {})
                                    content = msg.get('content')
                                    if isinstance(content, str) and 'заблокирован' in content:
                                        print(f"[banned] Найдено 'заблокирован' в SSE чанке: {content}")
                                        raise BanDetectedException(f"Account '{account_id}' is banned in chunk")
                                
                                # Накопление choices
                                if 'choices' in data and data['choices']:
                                    accumulator['choices'].extend(data['choices'])
                                
                                # Сохраняем usage
                                usage = data.get('usage', {})
                                if usage:
                                    accumulator['usage'] = usage
                                    usage_dict['output_tokens'] = usage.get('completion_tokens', 0) or usage.get('output_tokens', 0)
                                    usage_dict['input_tokens'] = usage.get('prompt_tokens', usage_dict['input_tokens']) or usage.get('input_tokens', usage_dict['input_tokens'])
                                    
                        except (json.JSONDecodeError, ValueError):
                            pass
                    
                    yield line + '\n\n' # type: ignore
            
            # Запись статистики
            if STATS_ENABLED:
                threading.Thread(
                    target=record_request,
                    args=(account_id, 200, model, usage_dict['input_tokens'], usage_dict['output_tokens']),
                    daemon=True
                ).start()

        # Сборка ВСЕХ чанков ПЕРЕД возвратом StreamingResponse
        chunks = []
        try:
            # Сначала полностью собираем поток в память
            for chunk in collect_and_check_stream():
                chunks.append(chunk)
            
            # Если дошли сюда — бана не было, отдаём накопленное как iterator
            return StreamingResponse(
                iter(chunks),
                status_code=resp.status_code, # type: ignore
                media_type='text/event-stream'
            )
        except BanDetectedException as e:
            if is_test_request:
                print(f"[retry] Бан детектирован (тестовый режим), аккаунт не переключается: {e}")
            else:
                print(f"[retry] Бан детектирован: {e}. Переключаем аккаунт...")
                switch_account()
                current_account_id = 'account_' + ACCOUNT_IDS[current_acc_index]
                
                # Retry loop для stream-ответов
                for retry_attempt in range(len(ACCOUNTS) - 1):
                    print(f"[retry] Retry #{retry_attempt + 1}/{len(ACCOUNTS) - 1} после бана")
                    
                    resp_retry = session.post(TARGET_URL, json=payload, stream=payload.get('stream', True), timeout=180)
                    
                    if resp_retry.status_code != 200:
                        print(f"[retry] Аккаунт {current_account_id} вернул {resp_retry.status_code}, пробуем следующий")
                        if retry_attempt < len(ACCOUNTS) - 2:
                            switch_account()
                            current_account_id = 'account_' + ACCOUNT_IDS[current_acc_index]
                            continue
                        else:
                            print("[retry] Все аккаунты исчерпаны после бана")
                            break
                    
                    # Второй проход сборки потока
                    try:
                        usage_data_retry = {'input_tokens': input_tokens, 'output_tokens': 0}
                        chunks_retry = []
                        
                        # Сначала полностью собираем поток в память
                        for chunk in collect_and_check_stream_with_usage(resp_retry, usage_data_retry):
                            chunks_retry.append(chunk)
                        
                        return StreamingResponse(
                            iter(chunks_retry),
                            status_code=resp_retry.status_code,
                            media_type='text/event-stream'
                        )
                    except BanDetectedException as e2:
                        print(f"[retry] Бан снова в аккаунте {current_account_id}: {e2}")
                        if retry_attempt < len(ACCOUNTS) - 2:
                            switch_account()
                            continue
                        else:
                            print("[retry] Все аккаунты забанены")
                
            # Возвращаем ошибку клиенту если все аккаунты исчерпаны / тестовый режим
            if payload.get('stream', True):
                err_body = (
                    'data: ' + json.dumps(
                        {"error": "All accounts are banned", "detail": str(e)},
                        ensure_ascii=False
                    ) + '\n\n' + 'data: [DONE]\n\n'
                )
                return Response(
                    content=err_body,
                    status_code=403,
                    media_type='text/event-stream'
                )
            else:
                return JSONResponse(
                    {"error": "All accounts are banned", "detail": str(e)},
                    status_code=403
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
            match = re.search(r'(\{"tool_calls":\s*\[.*?\])', content, re.DOTALL)
            if match:
                tool_call_json = match.group(1)
                # Заменяем content на этот JSON и добавляем tool_calls в message
                new_message = message.copy()
                new_message['content'] = None  # или убираем
                new_message['tool_calls'] = json.loads(tool_call_json)['tool_calls']
                data['choices'][0]['message'] = new_message
                return Response(content=json.dumps(data), status_code=resp.status_code) # type: ignore
        # Если ничего не нашли, возвращаем как есть
        return Response(content=raw_response, status_code=resp.status_code) # type: ignore

# from sys import exit
# import re
# import json
# from urllib.parse import urlparse
# from sseclient import SSEClient # type: ignore
# from pprint import pprint
# import requests as rq
# from fastapi import FastAPI, Request, Response # type: ignore
# from fastapi.responses import StreamingResponse # type: ignore
# import threading
# import asyncio
# from accaunts import ACCOUNTS
#
# # добавить tools, mcp, skills
#
# app = FastAPI()
#
# current_acc_index = 0  # индекс текущего аккаунта в списке ACCOUNTS
#
# def curl_to_python(curl_text: str):
#     # Убираем обратные слэши и лишние пробелы
#     curl_text = re.sub(r'\\\s*\n', ' ', curl_text).strip()
#     
#     # Извлекаем URL
#     url_match = re.search(r"curl\s+(?:--url\s+)?'([^']+)'", curl_text)
#     if not url_match:
#         url_match = re.search(r'curl\s+(?:--url\s+)"([^"]+)"', curl_text)
#     url = url_match.group(1) if url_match else None
#
#     # Извлекаем все -H заголовки (включая значения с кавычками)
#     headers = {}
#     for match in re.finditer(r"-H\s+'([^:]+):\s*([^']+)'", curl_text):
#         key, value = match.group(1).strip(), match.group(2).strip()
#         headers[key] = value
#     for match in re.finditer(r'-H\s+"([^:]+):\s*([^"]+)"', curl_text):
#         key, value = match.group(1).strip(), match.group(2).strip()
#         headers[key] = value
#
#     # Извлекаем куки (-b)
#     cookies = {}
#     cookie_match = re.search(r"-b\s+'([^']+)'", curl_text) or re.search(r'-b\s+"([^"]+)"', curl_text)
#     if cookie_match:
#         cookie_str = cookie_match.group(1)
#         # Можно разобрать как строку cookie (key=value; key2=value2)
#         for part in cookie_str.split(';'):
#             if '=' in part:
#                 k, v = part.strip().split('=', 1)
#                 cookies[k] = v
#
#     # Извлекаем данные --data-raw
#     data = None
#     data_match = re.search(r"--data-raw\s+'([^']+)'", curl_text) or re.search(r'--data-raw\s+"([^"]+)"', curl_text)
#     if data_match:
#         raw = data_match.group(1)
#         try:
#             data = json.loads(raw)   # если JSON
#         except:
#             data = raw               # если просто строка
#
#     # Метод (по умолчанию GET, но если есть --data – POST)
#     method = 'POST' if data else 'GET'
#     if re.search(r'-X\s+(\w+)', curl_text):
#         method = re.search(r'-X\s+(\w+)', curl_text).group(1) # type: ignore
#
#     return {
#         'url': url,
#         'method': method,
#         'headers': headers,
#         'cookies': cookies,
#         'data': data,
#     }
#
# def strip_think_tags(text: str) -> str:
#     """Удаляет блоки <think>...</think> из текста."""
#     return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
#
#
# def strip_think_from_sse_line(line: str) -> str:
#     """Парсит SSE data строку и удаляет <think> теги из content delta."""
#     if not line.startswith('data: '):
#         return line
#     payload = line[6:]
#     if payload.strip() == '[DONE]':
#         return line
#     try:
#         data = json.loads(payload)
#         for choice in data.get('choices', []):
#             delta = choice.get('delta', {})
#             content = delta.get('content')
#             if isinstance(content, str) and content:
#                 cleaned = strip_think_tags(content)
#                 if cleaned != content:
#                     delta['content'] = cleaned
#                     return 'data: ' + json.dumps(data, ensure_ascii=False)
#     except (json.JSONDecodeError, ValueError):
#         pass
#     return line
#
#
# all_ = curl_to_python(ACCOUNTS[current_acc_index])
# TARGET_URL = all_['url']
# session = rq.Session()
# session.headers.update(all_['headers'])
# session.cookies.update(all_['cookies'])
#
#
# def switch_account():
#     """Циклически переключает аккаунт, обновляет session.headers и session.cookies."""
#     global current_acc_index
#     current_acc_index = (current_acc_index + 1) % len(ACCOUNTS)
#     parsed = curl_to_python(ACCOUNTS[current_acc_index])
#     session.headers.clear()
#     session.cookies.clear()
#     session.headers.update(parsed['headers'])
#     session.cookies.update(parsed['cookies'])
#     print(f"[retry] Переключён на аккаунт {current_acc_index + 1}/{len(ACCOUNTS)}")
#
#
# def format_tools_for_prompt(tools: list) -> str:
#     """Преобразует массив tools (OpenAI-формат) в человекочитаемый список."""
#     if not tools:
#         return "_Нет доступных инструментов._"
#
#     lines = ["### available_tools:"]
#     for tool in tools:
#         func = tool.get("function", {})
#         name = func.get("name", "unknown")
#         desc = func.get("description", "нет описания")
#         params = func.get("parameters", {})
#         props = params.get("properties", {})
#         required = params.get("required", [])
#
#         lines.append(f"- `{name}` — {desc}")
#         if props:
#             lines.append("  Параметры:")
#             for pname, pschema in props.items():
#                 ptype = pschema.get("type", "string")
#                 pdesc = pschema.get("description", "")
#                 req_tag = "required" if pname in required else "optional"
#                 # Если enum — показать варианты
#                 enum_vals = pschema.get("enum")
#                 if enum_vals:
#                     pdesc += f" (варианты: {', '.join(str(v) for v in enum_vals)})"
#                 lines.append(f"  - `{pname}` ({ptype}, {req_tag}): {pdesc}" if pdesc else f"  - `{pname}` ({ptype}, {req_tag})")
#
#     return "\n".join(lines)
#
#
# # def build_tool_format_spec() -> str:
# #     """Инструкция по формату XML tool calls."""
# #     return """## Формат tool calls — XML
# #
# # Для вызова инструментов ГЕНЕРИРУЙ блоки в XML формате (внутри своего текста):
# #
# # <tool_call>
# # <name>имя_инструмента</name>
# # <parameters>{"параметр": "значение"}</parameters>
# # </tool_call>
# #
# # Правила:
# # - Все параметры — JSON объект в теге `<parameters>`.
# # - Несколько инструментов — несколько блоков `<tool_call>`.
# # - Не оборачивай в ```xml``` — пиши как обычный текст.
# #
# # Примеры:
# #
# # **memory_set:**
# # <tool_call>
# # <name>memory_set</name>
# # <parameters>{"label": "lessons", "value": "- [2026-08-31] запись урока", "scope": "global"}</parameters>
# # </tool_call>
# #
# # **sequential-thinking:**
# # <tool_call>
# # <name>sequential-thinking_sequentialthinking</name>
# # <parameters>{"thought": "Анализирую задачу...", "nextThoughtNeeded": true, "thoughtNumber": 1, "totalThoughts": 3}</parameters>
# # </tool_call>
# #
# # **skill:**
# # <tool_call>
# # <name>skill</name>
# # <parameters>{"name": "system-reports"}</parameters>
# # </tool_call>
# #
# # **task:**
# # <tool_call>
# # <name>task</name>
# # <parameters>{"description": "Краткое описание", "prompt": "Подробный промпт", "subagent_type": "general"}</parameters>
# # </tool_call>"""
# #
# #
# # def build_system_prompt(tools: list, client_data: dict) -> str:
# #     """Генерирует system prompt с описанием инструментов и формата XML."""
# #     tools_text = format_tools_for_prompt(tools)
# #     tool_spec = build_tool_format_spec()
# #
# #     prompt = f"""Ты — AI-ассистент, работающий через OpenCode. Ты ОБЯЗАН генерировать вызовы инструментов через tool calls в формате XML (см. ниже), когда это необходимо.
# #
# # ## Доступные инструменты
# #
# # {tools_text}
# #
# # {tool_spec}
# #
# # ## Важные правила
# #
# # 1. ВСЕГДА используй XML формат для вызова инструментов. НЕ вызывай инструменты описанием текстом.
# # 2. Для инструментов с параметрами — ВСЕГДА передавай все обязательные параметры.
# # 3. Если параметр — объект/массив, передавай его как JSON объект в теге <parameters>.
# # 4. Для числовых параметров (thoughtNumber, totalThoughts и т.д.) — передавай как есть в JSON (без кавычек для чисел/布尔).
# # 5. Можно вызывать НЕСКОЛЬКО инструментов в одном tool_calls блоке (несколько invoke).
# # 6. Не генерируй tool_calls если пользователь просто здоровается или задаёт простой вопрос без необходимости в инструментах.
# # 7. Отвечай на русском языке, если не попросят иное."""
# #
# #     return prompt
# #
#
# @app.post('/v1/chat/completions')
# async def proxy(request: Request):
#     # start:
#     client_data = await request.json()
#     # Можно принимать от клиента messages, остальное подставляем
#     payload = {
#         "group": client_data.get("group", "default"),
#         "messages": client_data["messages"],
#         "model": client_data.get("model", "free-minimax-m2.7"),
#         "stream": client_data.get("stream", True)
#     }
#
#     # Пробросить tools в payload для совместимости с upstream API
#     tools = client_data.get('tools', []) if client_data else []
#     if tools:
#         payload['tools'] = tools
#
#     # Построить system prompt с инструментами
#     # if tools:
#     #     system_prompt = build_system_prompt(tools, client_data)
#     # else:
#     #     system_prompt = 'Ты — AI-ассистент. Отвечай на русском языке.'
#     system_prompt = 'Ты — AI-ассистент. Отвечай на русском языке.'
#
#     # Добавить/заменить system message
#     if payload['messages'][0]['role'] == 'system':
#         payload['messages'][0]['content'] = system_prompt + '\n\n' + payload['messages'][0]['content']
#     else:
#         payload['messages'].insert(0, {'role': 'system', 'content': system_prompt})
#
#     print(json.dumps(payload, indent=2, ensure_ascii=False))
#
#     # --- Retry при 429: перебираем ВСЕ аккаунты по кругу ---
#     resp = None
#     for attempt in range(len(ACCOUNTS)):
#         resp = session.post(TARGET_URL, json=payload, stream=True)
#         if resp.status_code == 429:
#             print(f"[retry] Аккаунт {current_acc_index + 1} вернул 429 (попытка {attempt + 1}/{len(ACCOUNTS)})")
#             if attempt < len(ACCOUNTS) - 1:
#                 switch_account()
#                 continue
#             else:
#                 print("[retry] Все аккаунты исчерпаны, возвращаем 429 клиенту")
#                 return Response(
#                     content=json.dumps({"error": "rate_limit_exceeded", "detail": "Все аккаунты вернули 429"}),
#                     status_code=429
#                 )
#         if resp.status_code == 200:
#             break  # Нормальный ответ — выходим из цикла
#
#         if resp.status_code not in [200, 429]:
#             return Response(
#                 content=resp.content,
#                 status_code=resp.status_code
#             )
#
#
#     if resp.status_code != 200: # type: ignore
#         # Вернуть ошибку как JSON или SSE
#         return Response(content=resp.text, status_code=resp.status_code) # type: ignore
#     # print(f"Status: {resp.status_code}")
#     if payload.get('stream', True):
#         stop_flag = threading.Event()
#
#         async def check_disconnect():
#             while not stop_flag.is_set():
#                 if await request.is_disconnected():
#                     stop_flag.set()
#                     break
#                 await asyncio.sleep(0.5)
#
#         # Запускаем задачу проверки
#         asyncio.create_task(check_disconnect())
#
#         def stream_generator():
#             for line in resp.iter_lines(decode_unicode=False): # type: ignore
#                 if line:
#                     # Если пришёл признак конца потока – выходим
#                     line = line.decode()
#                     if line.strip() == 'data: [DONE]':
#                         yield line + '\n\n' # type: ignore
#                         break
#                     # Фильтрация <think> тегов из content delta
#                     if line.startswith('data: '):
#                         line = strip_think_from_sse_line(line)
#                     yield line + '\n\n' # type: ignore
#         return StreamingResponse(
#             stream_generator(),
#             status_code=resp.status_code, # type: ignore
#             media_type='text/event-stream'
#         )
#     else:
#         # Если стриминг выключен – возвращаем обычный JSON, но преобразуем
#         raw_response = resp.text # type: ignore
#         try:
#             data = json.loads(raw_response)
#             # Проверяем, есть ли в ответе поле tool_calls (в формате OpenAI)
#             if 'choices' in data and data['choices']:
#                 message = data['choices'][0].get('message', {})
#                 if 'tool_calls' in message:
#                     # Уже в нужном формате, просто возвращаем
#                     return Response(content=raw_response, status_code=resp.status_code) # type: ignore
#                 # Иначе, возможно, модель вернула текст с вызовом в виде тегов
#                 content = message.get('content', '')
#                 content = strip_think_tags(content)
#                 message['content'] = content
#                 # Попробуем найти JSON внутри текста (например, {"tool_calls": ...})
#                 # Можно использовать регулярное выражение
#                 match = re.search(r'(\{"tool_calls":\s*\[.*?\])', content, re.DOTALL)
#                 if match:
#                     tool_call_json = match.group(1)
#                     # Заменяем content на этот JSON и добавляем tool_calls в message
#                     new_message = message.copy()
#                     new_message['content'] = None  # или убираем
#                     new_message['tool_calls'] = json.loads(tool_call_json)['tool_calls']
#                     data['choices'][0]['message'] = new_message
#                     return Response(content=json.dumps(data), status_code=resp.status_code) # type: ignore
#         except json.JSONDecodeError:
#             pass
#         # Если ничего не нашли, возвращаем как есть
#         return Response(content=raw_response, status_code=resp.status_code) # type: ignore
