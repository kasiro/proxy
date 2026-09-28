from sys import exit
import os
import re
import json
import secrets
from urllib.parse import urlparse
from sseclient import SSEClient # type: ignore
from pprint import pprint
import requests as rq
from fastapi import FastAPI, Request, Response # type: ignore
from fastapi.responses import StreamingResponse # type: ignore
import threading
import asyncio
from accaunts import ACCOUNTS

# добавить tools, mcp, skills

app = FastAPI()

current_acc_index = 0  # индекс текущего аккаунта в списке ACCOUNTS

# Список моделей для эндпоинта /v1/models
# owned_by: odirouter → free-* ; opencode → muse-spark-*/mimo-*/ling-*/nemotron-*/union-alpha
MODELS_LIST = [
    {"id": "free-minimax-m2.7", "object": "model", "created": 1788893105, "owned_by": "odirouter"},
    {"id": "free-gemini-2.5-pro", "object": "model", "created": 1788893105, "owned_by": "odirouter"},
    {"id": "free-claude-haiku-4-5-20251001", "object": "model", "created": 1788893105, "owned_by": "odirouter"},
    {"id": "free-gemini-2.5-flash", "object": "model", "created": 1788893105, "owned_by": "odirouter"},
    {"id": "free-gpt-5.4-mini", "object": "model", "created": 1788893105, "owned_by": "odirouter"},
    {"id": "free-qwen3.5-plus", "object": "model", "created": 1788893105, "owned_by": "odirouter"},
    {"id": "free-qwen3.5-flash", "object": "model", "created": 1788893105, "owned_by": "odirouter"},
    {"id": "free-minimax-m2.5", "object": "model", "created": 1788893105, "owned_by": "odirouter"},
    {"id": "free-gemini-2.5-flash-lite", "object": "model", "created": 1788893105, "owned_by": "odirouter"},
    {"id": "free-gemini-3-flash-preview", "object": "model", "created": 1788893105, "owned_by": "odirouter"},
    {"id": "muse-spark-1.3-contributor-free", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "muse-spark-1.2-contributor-free", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "mimo-v2.5-free", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "mimo-v2.6-flash-free", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "jev-1.13-free", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "ling-3.0-flash-fin-free", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "nemotron-3-ultra-free", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "nemotron-3.5-lightning-free", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "union-alpha", "object": "model", "created": 1788893105, "owned_by": "opencode"},
    {"id": "big-pickle", "object": "model", "created": 1788893105, "owned_by": "opencode"},
]

def curl_to_python(curl_text: str):
    # Убираем обратные слэши и лишние пробелы
    curl_text = re.sub(r'\\\s*\n', ' ', curl_text).strip()
    
    # Извлекаем URL
    url_match = re.search(r"curl\s+(?:--url\s+)?'([^']+)'", curl_text)
    if not url_match:
        url_match = re.search(r'curl\s+(?:--url\s+)"([^"]+)"', curl_text)
    url = url_match.group(1) if url_match else None

    # Извлекаем все -H заголовки (включая значения с кавычками)
    headers = {}
    for match in re.finditer(r"-H\s+'([^:]+):\s*([^']+)'", curl_text):
        key, value = match.group(1).strip(), match.group(2).strip()
        headers[key] = value
    for match in re.finditer(r'-H\s+"([^:]+):\s*([^"]+)"', curl_text):
        key, value = match.group(1).strip(), match.group(2).strip()
        headers[key] = value

    # Извлекаем куки (-b)
    cookies = {}
    cookie_match = re.search(r"-b\s+'([^']+)'", curl_text) or re.search(r'-b\s+"([^"]+)"', curl_text)
    if cookie_match:
        cookie_str = cookie_match.group(1)
        # Можно разобрать как строку cookie (key=value; key2=value2)
        for part in cookie_str.split(';'):
            if '=' in part:
                k, v = part.strip().split('=', 1)
                cookies[k] = v

    # Извлекаем данные --data-raw
    data = None
    data_match = re.search(r"--data-raw\s+'([^']+)'", curl_text) or re.search(r'--data-raw\s+"([^"]+)"', curl_text)
    if data_match:
        raw = data_match.group(1)
        try:
            data = json.loads(raw)   # если JSON
        except:
            data = raw               # если просто строка

    # Метод (по умолчанию GET, но если есть --data – POST)
    method = 'POST' if data else 'GET'
    if re.search(r'-X\s+(\w+)', curl_text):
        method = re.search(r'-X\s+(\w+)', curl_text).group(1) # type: ignore

    return {
        'url': url,
        'method': method,
        'headers': headers,
        'cookies': cookies,
        'data': data,
    }
def strip_think_tags(text: str) -> str:
    """Удаляет блоки <think>...</think>

 из текста."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)


def safe_print_payload(payload: dict) -> None:
    """Безопасный вывод payload — исключает tools и системные промпты."""
    safe_copy = payload.copy()
    
    # Удаляем tools если есть
    if 'tools' in safe_copy:
        safe_copy['tools'] = '<REDACTED>'
    
    # Фильтруем messages, убирая сообщения с role='system'
    if 'messages' in safe_copy:
        safe_copy['messages'] = [
            msg for msg in safe_copy['messages']
            if msg.get('role') != 'system'
        ]
    
    print(json.dumps(safe_copy, indent=2, ensure_ascii=False))


@app.get("/v1/models")
@app.get("/models")
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


all_ = curl_to_python(ACCOUNTS[current_acc_index])
TARGET_URL = all_['url']
session = rq.Session()
session.headers.update(all_['headers'])
session.cookies.update(all_['cookies'])


# --- Bypass заголовки (без них 403, с ними 200) ---
# Только добавляют/перезаписывают UA + x-opencode-*, auth/cookie из ACCOUNTS не трогают.
BYPASS_UA = "opencode/1.18.31 ai-sdk/provider-utils/4.0.23 runtime/bun/1.3.13"

def fresh_bypass_headers() -> dict:
    """Генерирует свежие bypass-заголовки с новыми ses_/msg_ идентификаторами."""
    return {
        "user-agent": BYPASS_UA,
        "x-opencode-client": "cli",
        "x-opencode-project": "global",
        "x-opencode-session": "ses_" + secrets.token_hex(13),  # 26 hex-символов
        "x-opencode-request": "msg_" + secrets.token_hex(9),   # 18 hex-символов
    }

def apply_bypass_headers() -> None:
    """Обновляет bypass-заголовки в session (auth/cookie из ACCOUNTS не трогает)."""
    session.headers.update(fresh_bypass_headers())

apply_bypass_headers()  # стартовые bypass-заголовки поверх ACCOUNTS[0]


# --- Opencode Zen (модели с owned_by==opencode) ---
OPENCODE_ZEN_URL = "https://opencode.ai/zen/v1/chat/completions"
OPENCODE_RESPONSES_URL = "https://opencode.ai/zen/v1/responses"

def _load_zen_key() -> str:
    """Ключ OPENCODE_ZEN_API_KEY из env (профиль jarvis). Значение не логировать."""
    key = os.environ.get("OPENCODE_ZEN_API_KEY", "") or os.environ.get("OPENCODE_API_KEY", "") or 'oc_sk_9aa7c04a4742_gb7ovR4G1T6SOw4KEvMUNER0G7oPxu2P'
    if key:
        return key
    # Фолбэк: .env профиля jarvis (только чтение значения в память, без логов)
    try:
        jarvis_env = os.path.expanduser("~/.hermes/profiles/jarvis/.env")
        with open(jarvis_env, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENCODE_ZEN_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return ""

OPENCODE_ZEN_API_KEY = _load_zen_key()


def switch_account():
    """Циклически переключает аккаунт, обновляет session.headers и session.cookies."""
    global current_acc_index
    current_acc_index = (current_acc_index + 1) % len(ACCOUNTS)
    parsed = curl_to_python(ACCOUNTS[current_acc_index])
    session.headers.clear()
    session.cookies.clear()
    session.headers.update(parsed['headers'])
    session.cookies.update(parsed['cookies'])
    apply_bypass_headers()  # свежие ses_/msg_ поверх нового аккаунта (auth/cookie целы)
    print(f"[retry] Переключён на аккаунт {current_acc_index + 1}/{len(ACCOUNTS)}")


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


# --- Responses API для muse-spark-* (образец: FishBottle7/opencode2dsh PR#8) ---
# Эмпирика: muse-spark-* через /chat всегда 500, через /responses 200;
# big-pickle наоборот. Роутинг по префиксу, как isResponsesModel() в PR#8.

def is_responses_model(model_id: str) -> bool:
    """Responses-only модели Zen: префикс muse-spark (case-insensitive)."""
    return str(model_id or "").lower().startswith("muse-spark")


def _messages_to_responses_input(messages: list) -> list:
    """Маппит chat messages в input для /responses (списком items, порядок сохранён).

    - user/system/developer → {"role": ..., "content": текст}
    - assistant с tool_calls → текстовый item (если есть content) + function_call items
      {type:function_call, call_id, name, arguments(строка JSON)}
    - role:tool → {type:function_call_output, call_id, output}
      чтобы multi-turn видел результаты инструментов.
    """
    out: list = []
    for msg in messages or []:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            # content может быть списком блоков {type, text} — вытащить текст
            texts = []
            for block in content:
                if isinstance(block, dict):
                    texts.append(str(block.get("text", "")))
                else:
                    texts.append(str(block))
            content = "".join(texts)
        if content is None:
            content = ""
        if not isinstance(content, str):
            content = str(content)
        if role == "tool":
            call_id = msg.get("tool_call_id") or msg.get("id") or ""
            out.append({
                "type": "function_call_output",
                "call_id": str(call_id),
                "output": content,
            })
            continue
        tool_calls = msg.get("tool_calls") or []
        if role == "assistant" and tool_calls:
            if content.strip():
                out.append({"role": "assistant", "content": content})
            for tc in tool_calls:
                if not isinstance(tc, dict):
                    continue
                fn = tc.get("function", {}) if isinstance(tc.get("function"), dict) else {}
                args = fn.get("arguments", "")
                if isinstance(args, dict):
                    args = json.dumps(args, ensure_ascii=False)
                elif args is None:
                    args = ""
                else:
                    args = str(args)
                out.append({
                    "type": "function_call",
                    "call_id": str(tc.get("id", "")),
                    "name": str(fn.get("name", "")),
                    "arguments": args,
                })
            continue
        out.append({"role": role, "content": content})
    return out


def _chat_tools_to_responses(tools: list) -> list:
    """Конвертирует chat tools в формат Responses API (плоский function)."""
    converted = []
    for tool in tools or []:
        if not isinstance(tool, dict):
            continue
        func = tool.get("function")
        if isinstance(func, dict):
            entry: dict = {"type": "function", "name": func.get("name", "unknown")}
            if func.get("description"):
                entry["description"] = func["description"]
            if func.get("parameters"):
                entry["parameters"] = func["parameters"]
            converted.append(entry)
        else:
            # Уже плоский формат (или неизвестный) — проброс как есть
            converted.append(tool)
    return converted


def _extract_responses_text(data: dict) -> str:
    """Достаёт итоговый текст из JSON ответа /responses (не-стрим)."""
    # Прямое поле (некоторые гейты отдают output_text сверху)
    if isinstance(data.get("output_text"), str) and data["output_text"]:
        return data["output_text"]
    texts = []
    for item in data.get("output", []) or []:
        if not isinstance(item, dict):
            continue
        for block in item.get("content", []) or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") in ("output_text", "text") and isinstance(block.get("text"), str):
                texts.append(block["text"])
    if texts:
        return "".join(texts)
    return ""


def _extract_responses_tool_calls(data: dict) -> list:
    """Достаёт function_call items из JSON /responses → chat tool_calls.

    Формат Zen: output[] item {type:function_call, call_id, name, arguments(строка JSON)}.
    Возвращает [{id:call_id, type:function, function:{name, arguments}}].
    """
    calls = []
    for item in (data.get("output") or []) or []:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "function_call":
            continue
        args = item.get("arguments", "")
        if isinstance(args, dict):
            args = json.dumps(args, ensure_ascii=False)
        elif args is None:
            args = ""
        else:
            args = str(args)
        calls.append({
            "id": str(item.get("call_id") or item.get("id") or ""),
            "type": "function",
            "function": {
                "name": str(item.get("name", "")),
                "arguments": args,
            },
        })
    return calls


def _responses_delta_text(event: dict) -> "str | None":
    """Достаёт текстовую дельту из одного SSE-события /responses; None — пропустить."""
    etype = str(event.get("type", ""))
    # Reasoning-события и служебные (created/in_progress/completed) текстом не отдаём.
    # Куски function_call_arguments НЕ отдаём как content — они идут в delta.tool_calls.
    # response.output_text.done / content_part.* несут ПОЛНЫЙ (уже отданный дельтами)
    # текст — их отдача как дельты даёт дословный дубль ("Ищу статью...Ищу статью...").
    if (
        "reasoning" in etype
        or "function_call" in etype
        or "arguments" in etype
        or "content_part" in etype
        or etype in (
            "response.created", "response.in_progress", "response.queued",
            "response.completed", "response.complete",
            "response.output_item.added", "response.output_item.done",
            "response.output_text.done",
        )
    ):
        return None
    for key in ("delta", "text_delta", "text"):
        val = event.get(key)
        if isinstance(val, str) and val:
            return val
    # Вложенные варианты: {"delta": {"text": ...}}
    delta = event.get("delta")
    if isinstance(delta, dict):
        for key in ("text", "output_text"):
            val = delta.get(key)
            if isinstance(val, str) and val:
                return val
    return None


def _chat_sse_chunk(model_id: str, content: "str | None" = "", finish: "str | None" = None, tool_calls: "list | None" = None) -> str:
    """Один SSE-чанк в формате /v1/chat/completions (поддерживает delta.tool_calls)."""
    delta: dict = {}
    if content:
        delta["content"] = content
    if tool_calls is not None:
        delta["tool_calls"] = tool_calls
    chunk = {
        "id": "chatcmpl-" + secrets.token_hex(12),
        "object": "chat.completion.chunk",
        "created": 1788893105,
        "model": model_id,
        "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
    }
    return "data: " + json.dumps(chunk, ensure_ascii=False)


def _chat_sse_tool_chunk(model_id: str, index: int, call_id: "str | None" = None, name: "str | None" = None, args_delta: "str | None" = None) -> str:
    """Один SSE-чанк delta.tool_calls (header с id/name или дельта arguments)."""
    fn: dict = {}
    if name is not None:
        fn["name"] = name
    if args_delta is not None:
        fn["arguments"] = args_delta
    entry: dict = {"index": index, "function": fn}
    if call_id is not None:
        entry["id"] = call_id
        entry["type"] = "function"
    return _chat_sse_chunk(model_id, "", None, [entry])


def _chat_sse_finish_chunk(model_id: str, finish: str) -> str:
    """Финальный SSE-чанк с пустой дельтой и finish_reason."""
    chunk = {
        "id": "chatcmpl-" + secrets.token_hex(12),
        "object": "chat.completion.chunk",
        "created": 1788893105,
        "model": model_id,
        "choices": [{"index": 0, "delta": {}, "finish_reason": finish}],
    }
    return "data: " + json.dumps(chunk, ensure_ascii=False)


def _responses_sse_to_chat_completion(model_id: str, raw_text: str, status_code: int = 200) -> "Response | None":
    """Фолбэк: Zen отдал SSE вместо JSON (проигнорировал stream:false) —
    склеить output_text.delta + function_call из response.completed в chat-completion.
    Возвращает Response или None (текста/вызовов нет — отдать raw как есть).
    """
    texts: list = []
    completed_texts: list = []
    calls: list = []
    for line in (raw_text or "").splitlines():
        s = line.strip()
        if not s.startswith("data:"):
            continue
        payload = s[5:].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            event = json.loads(payload)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "response.completed":
            completed = event.get("response", event)
            if isinstance(completed, dict):
                t = strip_think_tags(_extract_responses_text(completed))
                if t:
                    completed_texts.append(t)
                calls.extend(_extract_responses_tool_calls(completed))
            continue
        d = _responses_delta_text(event)
        if d:
            texts.append(d)
    # Полный текст из completed авторитетнее склейки дельт: иначе дельты +
    # полный текст дадут дословный дубль ("Ищу статью...Ищу статью...").
    text = "".join(completed_texts) if completed_texts else strip_think_tags("".join(texts))
    if not text and not calls:
        return None
    if calls:
        message: dict = {"role": "assistant", "content": text or None, "tool_calls": calls}
        finish = "tool_calls"
    else:
        message = {"role": "assistant", "content": text}
        finish = "stop"
    body = {
        "id": "chatcmpl-" + secrets.token_hex(12),
        "object": "chat.completion",
        "created": 1788893105,
        "model": model_id,
        "choices": [{"index": 0, "message": message, "finish_reason": finish}],
    }
    return Response(content=json.dumps(body, ensure_ascii=False), status_code=status_code, media_type="application/json")


def _responses_to_chat_completion(model_id: str, data: dict, status_code: int = 200) -> Response:
    """Оборачивает JSON /responses в формат /v1/chat/completions (не-стрим)."""
    text = strip_think_tags(_extract_responses_text(data))
    tool_calls = _extract_responses_tool_calls(data)
    if tool_calls:
        message: dict = {"role": "assistant", "content": text or None, "tool_calls": tool_calls}
        finish = "tool_calls"
    else:
        message = {"role": "assistant", "content": text}
        finish = "stop"
    body = {
        "id": "chatcmpl-" + secrets.token_hex(12),
        "object": "chat.completion",
        "created": 1788893105,
        "model": model_id,
        "choices": [{"index": 0, "message": message, "finish_reason": finish}],
    }
    return Response(content=json.dumps(body, ensure_ascii=False), status_code=status_code, media_type="application/json")


# def build_tool_format_spec() -> str:
#     """Инструкция по формату JSON tool calls."""
#     return """## Формат tool calls — JSON
#
# Для вызова инструментов используй JSON формат:
#
# {
#   "tool_calls": [
#     {
#       "id": "call_xxx",
#       "type": "function",
#       "function": {
#         "name": "имя_инструмента",
#         "arguments": "{\\"параметр\\": \\"значение\\"}"
#       }
#     }
#   ]
# }
#
# Правила:
# - id должен быть уникальным (например: call_abc123)
# - arguments - ВСЕГДА JSON строка (даже если пустой объект {})
# - Несколько инструментов - несколько объектов в массиве tool_calls
#
# Примеры:
#
# **memory_set:**
# {"tool_calls": [{"id": "call_abc123","type": "function","function": {"name": "memory_set","arguments": "{\\"label\\": \\"lessons\\", \\"value\\": \\"- [2026-08-31] запись урока\\", \\"scope\\": \\"global\\"}"}}]}
#
# **sequential-thinking:**
# {"tool_calls": [{"id": "call_def456","type": "function","function": {"name": "sequential-thinking_sequentialthinking","arguments": "{\\"thought\\": \\"Анализирую задачу...\\", \\"nextThoughtNeeded\\": true, \\"thoughtNumber\\": 1, \\"totalThoughts\\": 3}"}}]}
#
# **skill:**
# {"tool_calls": [{"id": "call_ghi789","type": "function","function": {"name": "skill","arguments": "{\\"name\\": \\"system-reports\\"}"}}]}
#
# **task:**
# {"tool_calls": [{"id": "call_jkl012","type": "function","function": {"name": "task", "arguments": "{\\"description\\": \\"Краткое описание\\", \\"prompt\\": \\"Подробный промпт\\", \\"subagent_type\\": \\"general\\"}"}}]}"""
#
#
# def build_system_prompt(tools: list, client_data: dict) -> str:
#     """Генерирует system prompt с описанием инструментов и формата JSON."""
#     tools_text = format_tools_for_prompt(tools)
#     tool_spec = build_tool_format_spec()
#
#     prompt = f"""Ты — AI-ассистент, работающий через OpenCode. Ты ОБЯЗАН генерировать вызовы инструментов через tool calls в формате JSON (см. ниже), когда это необходимо.
#
# ## Доступные инструменты
#
# {tools_text}
#
# {tool_spec}
#
# ## Важные правила
#
# 1. ВСЕГДА используй JSON формат для вызова инструментов. НЕ вызывай инструменты описанием текстом.
# 2. Для инструментов с параметрами — ВСЕГДА передавай все обязательные параметры.
# 3. Если параметр — объект/массив, передавай его как JSON в поле arguments.
# 4. Для числовых параметров (thoughtNumber, totalThoughts и т.д.) — передавай как есть в JSON (без кавычек для чисел/булевых).
# 5. Можно вызывать НЕСКОЛЬКО инструментов в одном tool_calls массиве.
# 6. Не генерируй tool_calls если пользователь просто здоровается или задаёт простой вопрос без необходимости в инструментах.
# 7. Отвечай на русском языке, если не попросят иное."""
#
#     return prompt
#

@app.post('/v1/chat/completions')
async def proxy(request: Request):
    # start:
    client_data = await request.json()
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
        payload['tools'] = tools

    # TODO(odirouter/muse-spark): TARGET_URL сейчас odirouter (ACCOUNTS[0] → odirouter.ai),
    # поэтому роут /responses НЕ добавляем — логику не меняем. Если модель muse-spark-*
    # через /v1/chat/completions начнёт отдавать 500 — проверить роут /responses
    # (на zen чат для muse-spark даёт 500, а /responses 200).
    # Добавить/заменить system message
    # if payload['messages'][0]['role'] == 'system':
    #     payload['messages'][0]['content'] = system_prompt + '\n\n' + payload['messages'][0]['content']
    # else:
    #     payload['messages'].insert(0, {'role': 'system', 'content': system_prompt})

    safe_print_payload(payload)

    # --- Ветвление по владельцу модели (MODELS_LIST.owned_by) ---
    model_id = payload.get("model", "free-minimax-m2.7")
    model_entry = next((m for m in MODELS_LIST if m.get("id") == model_id), None)
    if model_entry is None:
        return Response(
            content=json.dumps(
                {
                    "error": "unknown_model",
                    "detail": f"Модель '{model_id}' неизвестна. Доступные модели: "
                    + ", ".join(m["id"] for m in MODELS_LIST),
                },
                ensure_ascii=False,
            ),
            status_code=400,
            media_type="application/json",
        )

    resp = None
    use_responses = False  # muse-spark-* → /responses, остальные opencode → /chat
    # TODO(odirouter/muse-spark): muse-spark-* сейчас идут через /v1/chat/completions
    # на Zen (owned_by==opencode) — логику /chat не ломать. Если muse-spark-* через
    # /v1/chat/completions начнёт отдавать 500 — проверить роут /responses
    # (на zen чат для muse-spark даёт 500, а /responses 200).
    if model_entry.get("owned_by") == "opencode":
        # --- Opencode Zen: один POST без retry по ACCOUNTS ---
        # Сессию odirouter (session с cookie/auth ACCOUNTS) не используем,
        # чтобы не светить чужие куки. Отдельный rq.post с bypass + Bearer.
        if not OPENCODE_ZEN_API_KEY:
            return Response(
                content=json.dumps(
                    {"error": "missing_key", "detail": "OPENCODE_ZEN_API_KEY пуст (env профиля jarvis)"},
                    ensure_ascii=False,
                ),
                status_code=500,
                media_type="application/json",
            )
        zen_payload = {
            "messages": payload["messages"],
            "model": model_id,
            "stream": payload.get("stream", True),
        }
        if tools:
            zen_payload["tools"] = tools
        zen_headers = fresh_bypass_headers()
        zen_headers.update(
            {
                "authorization": f"Bearer {OPENCODE_ZEN_API_KEY}",
                "content-type": "application/json",
                # Zen решает формат ответа и по Accept: non-stream клиенту нужен JSON,
                # иначе апстрим отдаёт SSE-поток, который non-stream не переваривает.
                "accept": "application/json" if not payload.get("stream", True) else "text/event-stream",
            }
        )
        # muse-spark-* — Responses-only на Zen (chat даёт 500): model + input + stream.
        # Ключ и bypass-заголовки те же, messages не теряем (input текстом), tools — пробросом.
        use_responses = is_responses_model(model_id)
        if use_responses:
            responses_payload: dict = {
                "model": model_id,
                "input": _messages_to_responses_input(payload["messages"]),
                "stream": payload.get("stream", True),
            }
            if tools:
                responses_payload["tools"] = _chat_tools_to_responses(tools)
            resp = rq.post(OPENCODE_RESPONSES_URL, json=responses_payload, headers=zen_headers, stream=True)
        else:
            resp = rq.post(OPENCODE_ZEN_URL, json=zen_payload, headers=zen_headers, stream=True)
        if resp.status_code != 200:
            return Response(
                content=resp.content,
                status_code=resp.status_code,
            )
    else:
        # --- Odirouter (owned_by==odirouter): как раньше, retry по ACCOUNTS ---
        # --- Retry при 429: перебираем ВСЕ аккаунты по кругу ---
        for attempt in range(len(ACCOUNTS)):
            apply_bypass_headers()  # свежие ses_/msg_ перед каждым POST
            resp = session.post(TARGET_URL, json=payload, stream=True)
            if resp.status_code == 429:
                print(f"[retry] Аккаунт {current_acc_index + 1} вернул 429 (попытка {attempt + 1}/{len(ACCOUNTS)})")
                if attempt < len(ACCOUNTS) - 1:
                    switch_account()
                    continue
                else:
                    print("[retry] Все аккаунты исчерпаны, возвращаем 429 клиенту")
                    return Response(
                        content=json.dumps({"error": "rate_limit_exceeded", "detail": "Все аккаунты вернули 429"}),
                        status_code=429
                    )
            if resp.status_code == 200:
                break  # Нормальный ответ — выходим из цикла

            if resp.status_code not in [200, 429]:
                return Response(
                    content=resp.content,
                    status_code=resp.status_code
                )


    if resp.status_code != 200: # type: ignore
        # Вернуть ошибку как JSON или SSE
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

        def stream_generator():
            if use_responses:
                # Конверсия SSE /responses → /v1/chat/completions:
                # дельты response.output_text.delta → choices.delta.content,
                # function_call_arguments.delta → choices.delta.tool_calls, в конце [DONE].
                # Служебное (event:, keep-alive, reasoning/created/completed) не пробрасываем.
                sent_any = False
                # Аккумулятор function_call по item_id → {index, id, name, args}
                tool_acc: dict = {}
                tool_order: list = []

                def _tool_index(item_id: str) -> int:
                    if item_id not in tool_acc:
                        tool_acc[item_id] = {"index": len(tool_order), "id": "", "name": "", "args": ""}
                        tool_order.append(item_id)
                    return tool_acc[item_id]["index"]

                for line in resp.iter_lines(decode_unicode=False): # type: ignore
                    if not line:
                        continue
                    line = line.decode()
                    if line.startswith(":") or line.startswith("event:"):
                        continue
                    if line.strip() == "data: [DONE]":
                        break
                    if not line.startswith("data: "):
                        continue
                    try:
                        event = json.loads(line[6:])
                    except (json.JSONDecodeError, ValueError):
                        continue
                    if not isinstance(event, dict):
                        continue
                    etype = str(event.get("type", ""))
                    # --- function_call: header при added ---
                    if etype == "response.output_item.added":
                        item = event.get("item", {}) if isinstance(event.get("item"), dict) else {}
                        if item.get("type") == "function_call":
                            item_id = str(event.get("item_id") or item.get("id") or item.get("call_id") or "")
                            call_id = str(item.get("call_id") or item.get("id") or item_id)
                            name = str(item.get("name", ""))
                            idx = _tool_index(item_id)
                            tool_acc[item_id]["id"] = call_id
                            tool_acc[item_id]["name"] = name
                            yield _chat_sse_tool_chunk(model_id, idx, call_id, name, "") + "\n\n" # type: ignore
                            sent_any = True
                        continue
                    # --- function_call: дельты arguments ---
                    if etype == "response.function_call_arguments.delta":
                        item_id = str(event.get("item_id", ""))
                        d = event.get("delta", "")
                        if not isinstance(d, str):
                            d = str(d)
                        if d:
                            idx = _tool_index(item_id)
                            tool_acc[item_id]["args"] += d
                            yield _chat_sse_tool_chunk(model_id, idx, None, None, d) + "\n\n" # type: ignore
                            sent_any = True
                        continue
                    # --- function_call: финал item done (добор arguments, если дельт не было) ---
                    if etype == "response.output_item.done":
                        item = event.get("item", {}) if isinstance(event.get("item"), dict) else {}
                        if item.get("type") == "function_call":
                            item_id = str(event.get("item_id") or item.get("id") or item.get("call_id") or "")
                            call_id = str(item.get("call_id") or item.get("id") or item_id)
                            name = str(item.get("name", ""))
                            args = item.get("arguments", "")
                            if isinstance(args, dict):
                                args = json.dumps(args, ensure_ascii=False)
                            elif args is None:
                                args = ""
                            else:
                                args = str(args)
                            idx = _tool_index(item_id)
                            if not tool_acc[item_id]["id"]:
                                tool_acc[item_id]["id"] = call_id
                            if not tool_acc[item_id]["name"]:
                                tool_acc[item_id]["name"] = name
                            # Дельт не было, а полный arguments есть — отдать одним чанком
                            if args and not tool_acc[item_id]["args"]:
                                tool_acc[item_id]["args"] = args
                                # header мог не отправиться (без added) — отправить header + args
                                yield _chat_sse_tool_chunk(model_id, idx, tool_acc[item_id]["id"] or call_id, tool_acc[item_id]["name"] or name, "") + "\n\n" # type: ignore
                                yield _chat_sse_tool_chunk(model_id, idx, None, None, args) + "\n\n" # type: ignore
                                sent_any = True
                        continue
                    if etype == "response.output_text.done":
                        # done несёт ПОЛНЫЙ текст части — дельты уже отданы выше.
                        # Отдаём только если дельт не было вообще (нестандартный апстрим).
                        if not sent_any:
                            full = event.get("text", "")
                            if isinstance(full, str) and full:
                                cleaned = strip_think_tags(full)
                                if cleaned:
                                    yield _chat_sse_chunk(model_id, cleaned) + "\n\n" # type: ignore
                                    sent_any = True
                        continue
                    if event.get("type") == "response.completed":
                        # Дельты уже отданы — дубль полным текстом не нужен.
                        # Если дельт не было вообще — отдать итог одним чанком
                        # (текст + function_call из response.output).
                        if not sent_any:
                            completed = event.get("response", event)
                            if isinstance(completed, dict):
                                full = strip_think_tags(_extract_responses_text(completed))
                                if full:
                                    yield _chat_sse_chunk(model_id, full) + "\n\n" # type: ignore
                                    sent_any = True
                                for tc in _extract_responses_tool_calls(completed):
                                    fn = tc.get("function", {})
                                    idx = len(tool_order)
                                    tool_order.append(tc.get("id", ""))
                                    tool_acc[tc.get("id", "")] = {"index": idx, "id": tc.get("id", ""), "name": fn.get("name", ""), "args": fn.get("arguments", "")}
                                    yield _chat_sse_tool_chunk(model_id, idx, tc.get("id", ""), fn.get("name", ""), "") + "\n\n" # type: ignore
                                    if fn.get("arguments"):
                                        yield _chat_sse_tool_chunk(model_id, idx, None, None, fn.get("arguments", "")) + "\n\n" # type: ignore
                                    sent_any = True
                        continue
                    delta = _responses_delta_text(event)
                    if delta:
                        cleaned = strip_think_tags(delta)
                        if cleaned:
                            yield _chat_sse_chunk(model_id, cleaned) + "\n\n" # type: ignore
                            sent_any = True
                # Финал: при tool_calls — finish tool_calls, иначе просто [DONE]
                if tool_order:
                    yield _chat_sse_finish_chunk(model_id, "tool_calls") + "\n\n" # type: ignore
                yield "data: [DONE]\n\n" # type: ignore
                return
            for line in resp.iter_lines(decode_unicode=False): # type: ignore
                if line:
                    # Если пришёл признак конца потока – выходим
                    line = line.decode()
                    if line.strip() == 'data: [DONE]':
                        yield line + '\n\n' # type: ignore
                        break
                    # Фильтрация <think> тегов из content delta
                    if line.startswith('data: '):
                        line = strip_think_from_sse_line(line)
                    yield line + '\n\n' # type: ignore
        return StreamingResponse(
            stream_generator(),
            status_code=resp.status_code, # type: ignore
            media_type='text/event-stream'
        )
    else:
        # Если стриминг выключен – возвращаем обычный JSON, но преобразуем
        raw_response = resp.text # type: ignore
        if use_responses:
            # JSON /responses → /v1/chat/completions: choices[0].message.content
            try:
                return _responses_to_chat_completion(model_id, json.loads(raw_response), resp.status_code) # type: ignore
            except json.JSONDecodeError:
                # Zen иногда отдаёт SSE несмотря на stream:false — склеить в chat-completion,
                # иначе non-stream клиент получит не-JSON тело. Пусто — отдать raw как есть.
                wrapped = _responses_sse_to_chat_completion(model_id, raw_response, resp.status_code) # type: ignore
                if wrapped is not None:
                    return wrapped
                return Response(content=raw_response, status_code=resp.status_code) # type: ignore
        try:
            data = json.loads(raw_response)
            # Проверяем, есть ли в ответе поле tool_calls (в формате OpenAI)
            if 'choices' in data and data['choices']:
                message = data['choices'][0].get('message', {})
                if 'tool_calls' in message:
                    # Уже в нужном формате, просто возвращаем
                    return Response(content=raw_response, status_code=resp.status_code) # type: ignore
                # Иначе, возможно, модель вернула текст с вызовом в виде тегов
                content = message.get('content', '')
                content = strip_think_tags(content)
                message['content'] = content
                # Попробуем найти JSON внутри текста (например, {"tool_calls": ...})
                # Можно использовать регулярное выражение
                match = re.search(r'(\{"tool_calls":\s*\[.*?\])', content, re.DOTALL)
                if match:
                    tool_call_json = match.group(1)
                    # Заменяем content на этот JSON и добавляем tool_calls в message
                    new_message = message.copy()
                    new_message['content'] = None  # или убираем
                    new_message['tool_calls'] = json.loads(tool_call_json)['tool_calls']
                    data['choices'][0]['message'] = new_message
                    return Response(content=json.dumps(data), status_code=resp.status_code) # type: ignore
        except json.JSONDecodeError:
            pass
        # Если ничего не нашли, возвращаем как есть
        return Response(content=raw_response, status_code=resp.status_code) # type: ignore
