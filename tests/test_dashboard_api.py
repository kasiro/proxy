"""Тесты эндпоинтов dashboard.py через TestClient."""
import json

import pytest


# --- GET / ---

def test_dashboard_page_renders(dashboard_client):
    """Главная страница dashboard отдаёт HTML с заголовком."""
    response = dashboard_client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<html" in response.text.lower()


# --- GET /api/stats ---

def test_api_stats_returns_account_list(dashboard_client):
    """/api/stats возвращает список статистики по аккаунтам (lifespan init_accounts)."""
    response = dashboard_client.get("/api/stats")
    assert response.status_code == 200
    stats = response.json()
    assert isinstance(stats, list)
    assert len(stats) > 0
    entry = stats[0]
    for field in ("account_id", "request_count", "limit", "status"):
        assert field in entry
    assert entry["request_count"] == 0
    assert entry["status"] == "active"


# --- POST /api/record ---

def test_api_record_adds_request_to_log(dashboard_client):
    """/api/record пишет запрос в лог и подтверждает статусом ok."""
    response = dashboard_client.post(
        "/api/record",
        json={"account_id": "42", "status_code": 200},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    from stats_client import get_recent_requests
    requests = get_recent_requests()
    assert len(requests) == 1
    assert requests[0]["account_id"] == "42"
    assert requests[0]["status_code"] == 200


def test_api_record_missing_fields_rejected(dashboard_client):
    """Без обязательных полей запрос отклоняется валидацией pydantic (422)."""
    response = dashboard_client.post("/api/record", json={})
    assert response.status_code == 422


def test_api_record_bad_status_type_rejected(dashboard_client):
    """Невалидный тип status_code отклоняется (422)."""
    response = dashboard_client.post(
        "/api/record",
        json={"account_id": "1", "status_code": "не число"},
    )
    assert response.status_code == 422


# --- GET /sse/stats ---
#
# ВНИЯНИЕ: starlette TestClient буферизует тело ответа целиком
# (portal.call(self.app, ...) ждёт завершения ASGI-приложения), поэтому
# бесконечный SSE-генератор /sse/stats через client.stream() зависает навсегда.
# Эндпоинт тестируется прямым вызовом sse_stats() + итерация body_iterator.

def test_sse_stats_streams_data(dashboard):
    """/sse/stats отдаёт text/event-stream с data-пакетом stats+requests."""
    import asyncio

    async def read_sse():
        response = await dashboard.sse_stats()
        iterator = response.body_iterator
        first = await iterator.__anext__()
        # Второй __anext__ отрабатывает asyncio.sleep(0.5) внутри generate().
        second = await iterator.__anext__()
        # Отмена генератора: CancelledError ловится в except и пробрасывается.
        with pytest.raises(asyncio.CancelledError):
            await iterator.athrow(asyncio.CancelledError())
        return response, first, second

    response, first, second = asyncio.run(read_sse())

    assert response.media_type == "text/event-stream"
    assert response.headers["cache-control"] == "no-cache"
    assert response.headers["connection"] == "keep-alive"
    assert response.headers["x-accel-buffering"] == "no"

    assert first.startswith("data: ")
    payload = json.loads(first[len("data: "):])
    assert "stats" in payload
    assert "requests" in payload
    assert isinstance(payload["stats"], list)
    assert isinstance(payload["requests"], list)
    assert second.startswith("data: ")


# --- lifespan ---

def test_lifespan_initializes_stats(dashboard_client):
    """Lifespan инициализирует БД и наполняет account_stats аккаунтами из accaunts."""
    import stats_client
    response = dashboard_client.get("/api/stats")
    assert response.status_code == 200
    stats = response.json()
    from accaunts import ACCOUNTS
    assert len(stats) == len(ACCOUNTS)
