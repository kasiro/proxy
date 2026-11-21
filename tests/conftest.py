"""Общие фикстуры pytest для проекта kasiro-proxy.

Ключевая идея: путь к SQLite-БД статистики подменяется на временный
ДО импорта test_proxy/dashboard, чтобы тесты не трогали stats.db проекта.
"""
import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = Path(__file__).resolve().parent
for _path in (PROJECT_ROOT, TESTS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


@pytest.fixture(scope="session")
def tmp_db(tmp_path_factory):
    """Подменяет stats_client.DB_PATH на временный файл и создаёт схему."""
    import stats_client

    db_path = tmp_path_factory.mktemp("stats") / "test_stats.db"
    stats_client.DB_PATH = db_path
    stats_client.init_db()
    return db_path


@pytest.fixture(scope="session")
def proxy(tmp_db):
    """Импортирует test_proxy уже после подмены БД статистики."""
    import test_proxy

    return test_proxy


@pytest.fixture(scope="session")
def dashboard(tmp_db):
    """Импортирует dashboard уже после подмены БД статистики."""
    import dashboard

    return dashboard


@pytest.fixture(autouse=True)
def clean_stats_db(proxy):
    """Очищает таблицы статистики перед каждым тестом."""
    import stats_client

    conn = sqlite3.connect(stats_client.DB_PATH)
    conn.execute("DELETE FROM account_stats")
    conn.execute("DELETE FROM request_log")
    conn.commit()
    conn.close()
    yield


@pytest.fixture(autouse=True)
def reset_proxy_state(proxy):
    """Сбрасывает индекс аккаунта и состояние session до и после теста."""
    proxy.current_acc_index = 0
    saved_headers = dict(proxy.session.headers)
    saved_cookies = {c.name: c.value for c in proxy.session.cookies}
    saved_url = proxy.TARGET_URL
    yield
    proxy.current_acc_index = 0
    proxy.TARGET_URL = saved_url
    proxy.session.headers.clear()
    proxy.session.headers.update(saved_headers)
    proxy.session.cookies.clear()
    proxy.session.cookies.update(saved_cookies)


@pytest.fixture
def client(proxy):
    """TestClient для приложения test_proxy."""
    from fastapi.testclient import TestClient

    with TestClient(proxy.app) as test_client:
        yield test_client


@pytest.fixture
def dashboard_client(dashboard):
    """TestClient для приложения dashboard (с запуском lifespan)."""
    from fastapi.testclient import TestClient

    with TestClient(dashboard.app) as test_client:
        yield test_client


@pytest.fixture
def fake_upstream(proxy, monkeypatch):
    """Подменяет test_proxy.session.post управляемой заглушкой."""
    from helpers import FakeUpstream

    upstream = FakeUpstream()
    monkeypatch.setattr(proxy.session, "post", upstream.post)
    return upstream
