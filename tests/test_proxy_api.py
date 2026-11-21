"""Тесты эндпоинтов и вспомогательных функций test_proxy.py."""
import json
import re
import time
from types import NoneType
from unittest.mock import Mock

import pytest

from helpers import FakeResponse, chat_payload, sse_ban_line, sse_chunk

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "my_tool",
            "description": "Тестовый инструмент",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["a", "b"],
                             "description": "режим работы"},
                    "count": {"type": "integer"},
                },
                "required": ["mode"],
            },
        },
    }
]

BAN_MESSAGE = "Пользователь заблокирован"
# Теги собираются конкатенацией: литеральные HTML-подобные теги в файле портятся.
OPEN_TAG = "<" + "think>"
CLOSE_TAG = "</" + "think>"


def _assistant_response(content="Привет", tool_calls=None):
    """Собирает JSON-ответ upstream в формате chat.completion."""
    message = {"role": "assistant", "content": content}
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    return {
        "id": "chatcmpl-1",
        "object": "chat.completion",
        "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }


def _ban_response():
    """Ответ upstream, сигнализирующий о бане аккаунта."""
    return FakeResponse(200, json_body={"message": BAN_MESSAGE, "success": False})


# --- /v1/models ---

def test_models_endpoint_returns_openai_list(client):
    """GET /v1/models отдаёт непустой список моделей в формате OpenAI."""
    response = client.get("/v1/models")
    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "list"
    assert body["data"]
    for item in body["data"]:
        for field in ("id", "object", "created", "owned_by"):
            assert field in item
        assert item["object"] == "model"


# --- strip_think_tags ---

def test_strip_think_tags_removes_single_block(proxy):
    """strip_think_tags вырезает одиночный блок think-тегов."""
    text = "a " + OPEN_TAG + "x" + CLOSE_TAG + " b"
    assert proxy.strip_think_tags(text) == "a  b"


def test_strip_think_tags_removes_multiline_block(proxy):
    """Многострочный блок think-тегов удаляется целиком."""
    text = "a\n" + OPEN_TAG + "уже\nвсё" + CLOSE_TAG + "\nb"
    assert proxy.strip_think_tags(text) == "a\n\nb"


def test_strip_think_tags_keeps_plain_text(proxy):
    """Текст без тегов не меняется."""
    text = "обычный ответ без тегов"
    assert proxy.strip_think_tags(text) == text


# --- strip_think_from_sse_line ---

def test_strip_think_from_sse_line_cleans_delta(proxy):
    """strip_think_from_sse_line чистит content delta от think-тегов."""
    line = sse_chunk("a " + OPEN_TAG + "x" + CLOSE_TAG + " b")
    cleaned = proxy.strip_think_from_sse_line(line)
    assert cleaned.startswith("data: ")
    data = json.loads(cleaned[6:])
    assert data["choices"][0]["delta"]["content"] == "a  b"


def test_strip_think_from_sse_line_keeps_done(proxy):
    """Строка data: [DONE] возвращается без изменений."""
    assert proxy.strip_think_from_sse_line("data: [DONE]") == "data: [DONE]"


def test_strip_think_from_sse_line_keeps_non_data_line(proxy):
    """Строки без префикса data: не меняются."""
    line = "event: ping"
    assert proxy.strip_think_from_sse_line(line) == line


def test_strip_think_from_sse_line_keeps_invalid_json(proxy):
    """Невалидный JSON в data-строке возвращается как есть."""
    line = "data: {не json"
    assert proxy.strip_think_from_sse_line(line) == line


# --- check_account_ban ---

def test_check_account_ban_raises_on_blocked_message(proxy):
    """check_account_ban выбрасывает BanDetectedException при слове «заблокирован»."""
    with pytest.raises(proxy.BanDetectedException):
        proxy.check_account_ban({"choices": [{"message": BAN_MESSAGE}]})


def test_check_account_ban_ignores_normal_message(proxy):
    """Обычное сообщение не считается баном."""
    assert proxy.check_account_ban({"choices": [{"message": "всё хорошо"}]}) is False


def test_check_account_ban_ignores_empty_choices(proxy):
    """Отсутствующий choices не считается баном."""
    assert proxy.check_account_ban({}) is False


def test_check_account_ban_empty_list_returns_false(proxy):
    """Фикс бага: пустой список choices возвращает False (раньше — IndexError)."""
    assert proxy.check_account_ban({"choices": []}) is False


# --- non-stream успех ---

def test_non_stream_success_passthrough(client, fake_upstream):
    """Успешный non-stream ответ проксируется клиенту."""
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response("Привет")))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "Привет"
    assert len(fake_upstream.calls) == 1
    assert fake_upstream.last_payload["messages"][0]["role"] == "system"


def test_non_stream_tool_calls_preserved(client, fake_upstream):
    """Готовые tool_calls в ответе upstream сохраняются без изменений."""
    tool_calls = [{"id": "call_1", "type": "function",
                   "function": {"name": "memory_set", "arguments": "{}"}}]
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response(None, tool_calls)))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["tool_calls"] == tool_calls


def test_non_stream_think_tags_not_stripped_bug(client, fake_upstream):
    """Баг: в non-stream ответе think-теги не вырезаются из тела ответа."""
    content = "думаю...итог"
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response(content)))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.json()["choices"][0]["message"]["content"] == content


def test_non_stream_tool_calls_json_in_text_extracted(proxy):
    """Баг: регекс извлечения tool_calls не захватывает закрывающую '}', json.loads падает."""
    tool_calls = [{"id": "call_1", "type": "function",
                   "function": {"name": "memory_set", "arguments": "{}"}}]
    content = 'думаю итог {"tool_calls": ' + json.dumps(tool_calls) + '}'
    match = re.search(r'(\{"tool_calls":\s*\[.*?\])', content, re.DOTALL)
    assert match is not None
    # Извлечённая подстрока не является валидным JSON — эндпоинт вернёт 500.
    with pytest.raises(json.JSONDecodeError):
        json.loads(match.group(1))


# --- safe_print_payload ---

def test_safe_print_payload_redacts_tools_and_system(proxy, capsys):
    """safe_print_payload скрывает tools и убирает system-сообщения из вывода."""
    payload = {
        "model": "m",
        "tools": [{"type": "function"}],
        "messages": [
            {"role": "system", "content": "секретный системный промпт"},
            {"role": "user", "content": "привет"},
        ],
    }
    proxy.safe_print_payload(payload)
    out = capsys.readouterr().out
    assert "<REDACTED>" in out
    assert "секретный системный промпт" not in out
    assert "привет" in out


def test_safe_print_payload_keeps_tools_when_hide_disabled(proxy, capsys):
    """При hide_tools=False tools остаются в выводе."""
    payload = {"tools": [{"type": "function"}], "messages": []}
    proxy.safe_print_payload(payload, hide_tools=False)
    out = capsys.readouterr().out
    assert "<REDACTED>" not in out
    assert "function" in out


def test_safe_print_payload_without_messages(proxy, capsys):
    """Payload без ключа messages выводится целиком."""
    payload = {"model": "m", "stream": False}
    proxy.safe_print_payload(payload)
    out = capsys.readouterr().out
    assert '"model"' in out


# --- switch_account ---

def test_switch_account_advances_index(proxy):
    """switch_account переходит к следующему аккаунту."""
    assert proxy.current_acc_index == 0
    proxy.switch_account()
    assert proxy.current_acc_index == 1
    proxy.switch_account()
    assert proxy.current_acc_index == 2


def test_switch_account_wraps_around(proxy):
    """Индекс аккаунта закручивается по кругу."""
    proxy.current_acc_index = len(proxy.ACCOUNTS) - 1
    proxy.switch_account()
    assert proxy.current_acc_index == 0


def test_switch_account_no_accounts_left(proxy, monkeypatch):
    """Баг-документация: при пустом ACCOUNTS ветка «все исчерпаны» достижима."""
    monkeypatch.setattr(proxy, "ACCOUNTS", [])
    monkeypatch.setattr(proxy, "ACCOUNT_IDS", [])
    proxy.switch_account()  # не должен падать
    assert proxy.current_acc_index == 0


# --- format_tools_for_prompt ---

def test_format_tools_empty_list(proxy):
    """Пустой список tools даёт заглушку."""
    assert proxy.format_tools_for_prompt([]) == "_Нет доступных инструментов._"


def test_format_tools_full_description(proxy):
    """Полный tools-массив: имя, описание, параметры, enum, required/optional."""
    out = proxy.format_tools_for_prompt(TOOLS)
    assert out.startswith("### available_tools:")
    assert "- `my_tool` — Тестовый инструмент" in out
    assert "`mode` (string, required)" in out
    assert "(варианты: a, b)" in out
    assert "`count` (integer, optional)" in out


def test_format_tools_without_properties(proxy):
    """Инструмент без parameters.properties не имеет блока «Параметры:»."""
    tools = [{"function": {"name": "t1", "description": "d1"}}]
    out = proxy.format_tools_for_prompt(tools)
    assert "- `t1` — d1" in out
    assert "Параметры:" not in out


def test_format_tools_property_without_description(proxy):
    """Параметр без description выводится без двоеточия в конце строки."""
    tools = [{"function": {"name": "t", "parameters": {
        "properties": {"x": {"type": "integer"}}, "required": []}}}]
    out = proxy.format_tools_for_prompt(tools)
    assert "`x` (integer, optional)" in out
    assert out.rstrip().endswith("`x` (integer, optional)")


# --- build_tool_format_spec / build_system_prompt ---

def test_build_tool_format_spec_is_json_instruction(proxy):
    """Спецификация формата tool calls содержит JSON-шаблон и правила."""
    spec = proxy.build_tool_format_spec()
    assert "## Формат tool calls — JSON" in spec
    assert '"tool_calls"' in spec
    assert "arguments - ВСЕГДА JSON строка" in spec


def test_build_system_prompt_contains_tools_and_rules(proxy):
    """build_system_prompt собирает промпт с инструментами и правилами."""
    prompt = proxy.build_system_prompt(TOOLS, {})
    assert "### available_tools:" in prompt
    assert "my_tool" in prompt
    assert "## Формат tool calls — JSON" in prompt
    assert "Отвечай на русском языке" in prompt


def test_not_is_None_variants(proxy):
    """not_is_None: None и NoneType — False, остальные — True."""
    assert proxy.not_is_None(0) is True
    assert proxy.not_is_None("") is True
    assert proxy.not_is_None(None) is False
    assert proxy.not_is_None(NoneType) is False


# --- X-Test-Account-ID ---

def test_test_account_header_selects_account(client, fake_upstream, proxy):
    """Валидный X-Test-Account-ID переключает current_acc_index на указанный аккаунт."""
    target_id = proxy.ACCOUNT_IDS[3]
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response("ок")))
    response = client.post(
        "/v1/chat/completions",
        json=chat_payload(stream=False),
        headers={"X-Test-Account-ID": target_id},
    )
    assert response.status_code == 200
    assert proxy.current_acc_index == 3


def test_unknown_test_account_header_ignored(client, fake_upstream, proxy):
    """Невалидный X-Test-Account-ID не меняет индекс аккаунта."""
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response("ок")))
    response = client.post(
        "/v1/chat/completions",
        json=chat_payload(stream=False),
        headers={"X-Test-Account-ID": "99999999"},
    )
    assert response.status_code == 200
    assert proxy.current_acc_index == 0


# --- retry-ветки 429/401/прочие статусы ---

def _err(status, message="rate limited"):
    return FakeResponse(status, json_body={"message": message})


def test_429_switches_account_and_retries(client, fake_upstream, proxy):
    """429 переключает аккаунт и повторяет запрос до успеха."""
    fake_upstream.add(_err(429))
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response("ок")))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.status_code == 200
    assert len(fake_upstream.calls) == 2
    assert proxy.current_acc_index == 1


def test_401_switches_account_and_retries(client, fake_upstream, proxy):
    """401 обрабатывается как исчерпанный аккаунт — ретрай с переключением."""
    # тело только с error (ветка json_.get('error', 'None') при отсутствии message)
    fake_upstream.add(FakeResponse(401, json_body={"error": "reauth required"}))
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response("ок")))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.status_code == 200
    assert len(fake_upstream.calls) == 2
    assert proxy.current_acc_index == 1


def test_429_all_accounts_returns_429(client, fake_upstream, proxy):
    """Если все аккаунты вернули 429 — клиент получает 429 rate_limit_exceeded."""
    fake_upstream.set_default(_err(429))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.status_code == 429
    body = response.json()
    assert body["error"] == "rate_limit_exceeded"
    assert len(fake_upstream.calls) == len(proxy.ACCOUNTS)


def test_401_all_accounts_returns_unauthorized(client, fake_upstream):
    """Если все аккаунты вернули 401 — клиент получает 401 unauthorized."""
    fake_upstream.set_default(_err(401, "reauth"))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.status_code == 401
    assert response.json()["error"] == "unauthorized"


def test_429_test_request_returns_immediately(client, fake_upstream, proxy):
    """Тестовый запрос (X-Test-Account-ID) не ретраится — 429 сразу клиенту."""
    target_id = proxy.ACCOUNT_IDS[2]
    fake_upstream.set_default(_err(429))
    response = client.post(
        "/v1/chat/completions",
        json=chat_payload(stream=False),
        headers={"X-Test-Account-ID": target_id},
    )
    assert response.status_code == 429
    assert len(fake_upstream.calls) == 1
    assert proxy.current_acc_index == 2  # аккаунт не переключался


def test_500_stops_retry_and_passes_body(client, fake_upstream, proxy, monkeypatch, capsys):
    """Не-429/401 статус (500) обрывает цикл и возвращается клиенту как есть."""
    monkeypatch.setattr(proxy, "DEBUG_MODE", True)  # покрывает DEBUG-печать 500
    fake_upstream.set_default(_err(500, "internal"))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.status_code == 500
    assert "internal" in response.text
    # цикл retry прерван после первой попытки
    assert len(fake_upstream.calls) == 1
    assert "500" in capsys.readouterr().out


# --- non-stream бан ---

def test_non_stream_ban_switches_and_retries(client, fake_upstream, proxy):
    """200 с сообщением о бане переключает аккаунт и повторяет запрос."""
    fake_upstream.add(_ban_response())
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response("второй аккаунт")))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "второй аккаунт"
    assert len(fake_upstream.calls) == 2
    assert proxy.current_acc_index == 1


def test_non_stream_ban_test_request_returns_403(client, fake_upstream, proxy,
                                                  monkeypatch, capsys):
    """Тестовый запрос с баном: аккаунт не переключается, клиенту 403."""
    monkeypatch.setattr(proxy, "DEBUG_MODE", True)  # покрывает DEBUG-ветку 411
    target_id = proxy.ACCOUNT_IDS[4]
    fake_upstream.set_default(_ban_response())
    response = client.post(
        "/v1/chat/completions",
        json=chat_payload(stream=False),
        headers={"X-Test-Account-ID": target_id},
    )
    assert response.status_code == 403
    body = response.json()
    assert body["error"] == "Account is banned"
    assert len(fake_upstream.calls) == 1
    assert proxy.current_acc_index == 4
    assert "все аккаунты исчерпаны" in capsys.readouterr().out


# --- system prompt / tools в payload ---

def test_existing_system_message_gets_prepended(client, fake_upstream):
    """Системное сообщение клиента сохраняется и дополняется прокси-промптом."""
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response("ок")))
    messages = [
        {"role": "system", "content": "Мой системный промпт"},
        {"role": "user", "content": "привет"},
    ]
    client.post("/v1/chat/completions", json=chat_payload(stream=False, messages=messages))
    sent = fake_upstream.last_payload["messages"][0]
    assert sent["role"] == "system"
    assert "Мой системный промпт" in sent["content"]
    assert "Ты — AI-ассистент" in sent["content"]


def test_tools_forwarded_and_custom_system_prompt(client, fake_upstream):
    """tools пробрасываются в payload, системный промпт собирается из tools."""
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response("ок")))
    client.post("/v1/chat/completions",
                json=chat_payload(stream=False, tools=TOOLS))
    sent = fake_upstream.last_payload
    assert sent["tools"] == TOOLS
    assert "### available_tools:" in sent["messages"][0]["content"]


def test_qwen_plus_tools_use_default_prompt(client, fake_upstream):
    """Для free-qwen3.5-plus с tools используется дефолтный системный промпт."""
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response("ок")))
    client.post("/v1/chat/completions",
                json=chat_payload(stream=False, model="free-qwen3.5-plus", tools=TOOLS))
    sent = fake_upstream.last_payload
    assert sent["tools"] == TOOLS  # tools всё равно пробрасываются
    system = sent["messages"][0]["content"]
    assert "### available_tools:" not in system
    assert system.startswith("Ты — AI-ассистент. Отвечай на русском языке.")


# --- DEBUG_MODE ---

def test_debug_mode_prints_payload_and_ok(client, fake_upstream, proxy, monkeypatch, capsys):
    """PROXY_DEBUG=1: payload и статус 200 печатаются в stdout."""
    monkeypatch.setattr(proxy, "DEBUG_MODE", True)
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response("ок")))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.status_code == 200
    out = capsys.readouterr().out
    assert "messages" in out          # safe_print_payload(client_data)
    assert "200 OK" in out            # ветка DEBUG на успехе


def test_debug_mode_prints_429_test_request(client, fake_upstream, proxy, monkeypatch, capsys):
    """PROXY_DEBUG=1: диагностика 429 печатается и в тестовом режиме."""
    monkeypatch.setattr(proxy, "DEBUG_MODE", True)
    target_id = proxy.ACCOUNT_IDS[0]
    fake_upstream.set_default(_err(429))
    response = client.post(
        "/v1/chat/completions",
        json=chat_payload(stream=False),
        headers={"X-Test-Account-ID": target_id},
    )
    assert response.status_code == 429
    out = capsys.readouterr().out
    assert "429" in out
    assert "все аккаунты исчерпаны / тестовый режим" in out


# --- non-stream: JSON-ошибка и встроенные tool_calls ---

def test_non_stream_invalid_json_returned_as_is(client, fake_upstream):
    """Фикс бага: не-JSON тело upstream больше не роняет запрос —
    клиенту возвращается оригинальное тело с кодом ответа upstream."""
    fake_upstream.add(FakeResponse(200, text="plain text body"))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.status_code == 200
    assert response.text == "plain text body"


def test_non_stream_tool_calls_json_in_text_no_crash(client, fake_upstream):
    """tool_calls в тексте content: JSON захватывается целиком (включая финальную `}`),
    парсится и возвращается клиенту в message.tool_calls, а content становится None."""
    tool_calls = [{"id": "call_1", "type": "function",
                   "function": {"name": "memory_set", "arguments": "{}"}}]
    content = 'итог {"tool_calls": ' + json.dumps(tool_calls) + '}'
    fake_upstream.add(FakeResponse(200, json_body=_assistant_response(content)))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=False))
    assert response.status_code == 200
    message = response.json()["choices"][0]["message"]
    assert message["content"] is None
    assert message["tool_calls"] == tool_calls


# --- stream-ветка ---

def _stream_ok_lines():
    return [
        sse_chunk("Привет", extra={"usage": {"prompt_tokens": 7, "completion_tokens": 3}}),
        sse_chunk("", finish_reason="stop"),
        "data: [DONE]",
    ]


def test_stream_success_accumulates_and_sends_done(client, fake_upstream):
    """Успешный SSE-поток: чанки проходят клиенту, завершение — data: {"done": true}."""
    lines = _stream_ok_lines()
    # мусор вне data:-префикса (ветки except JSON в collect_and_check_stream)
    lines.insert(0, "heartbeat")
    lines.insert(2, "data: {мусор не json")
    fake_upstream.add(FakeResponse(200, lines=lines))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=True))
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "Привет" in response.text
    assert 'data: {"done": true}' in response.text
    assert "heartbeat" in response.text  # не-data строки пробрасываются как есть


def test_stream_think_tags_stripped(client, fake_upstream):
    """Фикс бага: strip_think_from_sse_line применяется к строке перед yield —
    think-теги не доходят до клиента."""
    line = sse_chunk("до " + OPEN_TAG + "мысли" + CLOSE_TAG + " после")
    fake_upstream.add(FakeResponse(200, lines=[line, "data: [DONE]"]))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=True))
    assert response.status_code == 200
    assert OPEN_TAG not in response.text
    assert CLOSE_TAG not in response.text
    assert "до  после" in response.text


def test_stream_ban_json_line_switches_and_retries(client, fake_upstream, proxy):
    """JSON-строка с баном вне data: переключает аккаунт и ретраит поток."""
    ban_line = json.dumps({"message": BAN_MESSAGE}, ensure_ascii=False)
    fake_upstream.add(FakeResponse(200, lines=[ban_line]))
    fake_upstream.add(FakeResponse(200, lines=_stream_ok_lines()))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=True))
    assert response.status_code == 200
    assert "Привет" in response.text
    assert len(fake_upstream.calls) == 2
    assert proxy.current_acc_index == 1


def test_stream_ban_in_chunk_switches_and_retries(client, fake_upstream, proxy):
    """Бан в choices[].message.content внутри data-чанка вызывает ретрай."""
    fake_upstream.add(FakeResponse(200, lines=[sse_ban_line(), "data: [DONE]"]))
    fake_upstream.add(FakeResponse(200, lines=_stream_ok_lines()))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=True))
    assert response.status_code == 200
    assert "Привет" in response.text
    assert len(fake_upstream.calls) == 2
    assert proxy.current_acc_index == 1


def test_stream_ban_test_request_returns_403_sse(client, fake_upstream, proxy):
    """Тестовый запрос с баном в потоке: 403 SSE-error, без переключения."""
    target_id = proxy.ACCOUNT_IDS[6]
    fake_upstream.set_default(FakeResponse(200, lines=[sse_ban_line()]))
    response = client.post(
        "/v1/chat/completions",
        json=chat_payload(stream=True),
        headers={"X-Test-Account-ID": target_id},
    )
    assert response.status_code == 403
    assert "All accounts are banned" in response.text
    assert len(fake_upstream.calls) == 1
    assert proxy.current_acc_index == 6


def test_stream_all_accounts_banned_returns_403(client, fake_upstream, proxy):
    """Все аккаунты дают бан в потоке — после полного цикла ретраев 403."""
    fake_upstream.set_default(FakeResponse(200, lines=[sse_ban_line()]))
    response = client.post("/v1/chat/completions", json=chat_payload(stream=True))
    assert response.status_code == 403
    assert "All accounts are banned" in response.text
    assert len(fake_upstream.calls) == len(proxy.ACCOUNTS)


def test_stream_retry_handles_non_200_then_success(client, fake_upstream, proxy):
    """После бана retry-цикл переживает 500 от upstream и выходит на успех."""
    ok_lines = [
        sse_chunk("вторая попытка",
                  extra={"usage": {"prompt_tokens": 5, "completion_tokens": 2}}),
        "data: {мусор не json",       # ветка except в collect_..._with_usage
        '{"ok": true}',               # не-data валидный JSON без бана
        "heartbeat",                  # не-data не-JSON без бана
        "data: [DONE]",
    ]
    fake_upstream.add(FakeResponse(200, lines=[sse_ban_line()]))   # основной вызов
    fake_upstream.add(_err(500, "upstream down"))                 # retry #1 → не-200
    fake_upstream.add(FakeResponse(200, lines=ok_lines))          # retry #2 → успех
    response = client.post("/v1/chat/completions", json=chat_payload(stream=True))
    assert response.status_code == 200
    assert "вторая попытка" in response.text
    assert len(fake_upstream.calls) == 3
    assert proxy.current_acc_index == 2


def test_stream_retry_banned_by_json_line_then_success(client, fake_upstream, proxy):
    """Бан в не-data JSON-строке ловится и во втором проходе (ветка 541), затем успех."""
    ban_json = json.dumps({"message": BAN_MESSAGE}, ensure_ascii=False)
    fake_upstream.add(FakeResponse(200, lines=[sse_ban_line()]))   # основной: бан в чанке
    fake_upstream.add(FakeResponse(200, lines=[ban_json]))         # retry #1: бан JSON-строкой
    fake_upstream.add(FakeResponse(200, lines=_stream_ok_lines())) # retry #2: успех
    response = client.post("/v1/chat/completions", json=chat_payload(stream=True))
    assert response.status_code == 200
    assert "Привет" in response.text
    assert len(fake_upstream.calls) == 3
    assert proxy.current_acc_index == 2


def test_stream_all_retries_non_200_ends_403(client, fake_upstream, proxy):
    """Если после бана все retry-попытки отвечают не-200 — цикл обрывается, клиент 403."""
    fake_upstream.add(FakeResponse(200, lines=[sse_ban_line()]))  # основной вызов
    fake_upstream.set_default(_err(500, "down"))                 # все retry → 500
    response = client.post("/v1/chat/completions", json=chat_payload(stream=True))
    assert response.status_code == 403
    assert "All accounts are banned" in response.text
    # 1 основной + (len(ACCOUNTS)-1) retry-попыток
    assert len(fake_upstream.calls) == len(proxy.ACCOUNTS)
