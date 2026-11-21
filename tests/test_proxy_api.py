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
OPEN_TAG = "<" + "thinking>"
CLOSE_TAG = "</" + "thinking>"


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


def test_check_account_ban_empty_list_raises_index_error_bug(proxy):
    """Баг: пустой список choices приводит к IndexError вместо False."""
    with pytest.raises(IndexError):
        proxy.check_account_ban({"choices": []})


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
