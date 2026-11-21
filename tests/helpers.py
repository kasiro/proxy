"""Заглушки upstream-ответов и конструкторы payload для тестов."""
import json


class FakeResponse:
    """Минимальная заглушка requests.Response для подмены session.post."""

    def __init__(self, status_code=200, json_body=None, text=None, lines=None,
                 headers=None, json_error=False):
        self.status_code = status_code
        self._json_body = json_body
        self._json_error = json_error
        self.headers = headers or {}
        if text is None and json_body is not None:
            text = json.dumps(json_body, ensure_ascii=False)
        self.text = text if text is not None else ""
        self._lines = list(lines or [])

    @property
    def content(self):
        """Тело ответа в байтах."""
        return self.text.encode("utf-8")

    def json(self):
        """Возвращает JSON-тело либо падает, как requests при его отсутствии."""
        if self._json_error or self._json_body is None:
            raise ValueError("FakeResponse: нет JSON-тела")
        return self._json_body

    def iter_lines(self, decode_unicode=False, **kwargs):
        """Итерирует строки SSE-потока в байтах."""
        for line in self._lines:
            yield line if isinstance(line, bytes) else line.encode("utf-8")


class FakeUpstream:
    """Управляемая заглушка test_proxy.session.post."""

    def __init__(self, responses=None):
        self.calls = []
        self.responses = list(responses or [])
        self.default = None

    def add(self, response):
        """Добавляет ответ в очередь."""
        self.responses.append(response)
        return self

    def set_default(self, response):
        """Задаёт ответ, который отдаётся после исчерпания очереди."""
        self.default = response
        return self

    def post(self, url, **kwargs):
        """Записывает вызов и возвращает подготовленный ответ."""
        self.calls.append({"url": url, **kwargs})
        index = len(self.calls) - 1
        if index < len(self.responses):
            return self.responses[index]
        if self.default is not None:
            return self.default
        if self.responses:
            return self.responses[-1]
        raise AssertionError("FakeUpstream: не задан ни один ответ")

    @property
    def last_payload(self):
        """JSON-payload последнего запроса к upstream."""
        return self.calls[-1]["json"]


def chat_payload(model="free-gemini-2.5-flash", stream=False, messages=None, **extra):
    """Собирает тело запроса к /v1/chat/completions."""
    body = {
        "model": model,
        "stream": stream,
        "messages": messages if messages is not None
        else [{"role": "user", "content": "привет"}],
    }
    body.update(extra)
    return body


def sse_chunk(content="", finish_reason=None, extra=None):
    """Собирает одну data-строку SSE с delta.content."""
    data = {
        "id": "chatcmpl-stream",
        "object": "chat.completion.chunk",
        "choices": [{"index": 0, "delta": {"content": content},
                     "finish_reason": finish_reason}],
    }
    if extra:
        data.update(extra)
    return "data: " + json.dumps(data, ensure_ascii=False)


def sse_ban_line(message="Пользователь заблокирован"):
    """Собирает SSE-строку, где бан лежит в choices[].message.content."""
    data = {"choices": [{"index": 0, "message": {"role": "assistant", "content": message}}]}
    return "data: " + json.dumps(data, ensure_ascii=False)
