"""Тесты модуля stats_client на временной SQLite-БД."""
import re
import sqlite3
from datetime import datetime

import pytest

import stats_client

DAY = 86400


class FakeClock:
    """Управляемые часы: подменяют модуль time в stats_client."""

    def __init__(self, now):
        self.now = now

    def time(self):
        """Возвращает фиксированное «текущее» время."""
        return self.now


@pytest.fixture
def clock(monkeypatch):
    """Подменяет stats_client.time управляемыми часами."""
    fake = FakeClock(1_800_000_000)
    monkeypatch.setattr(stats_client, "time", fake)
    return fake


def _insert_account(account_id, request_count=0, first_request_at=None,
                    last_request_at=None, last_429_at=None):
    """Прямая вставка строки account_stats для подготовки состояния."""
    conn = sqlite3.connect(stats_client.DB_PATH)
    conn.execute(
        """INSERT INTO account_stats
               (account_id, request_count, first_request_at, last_request_at, last_429_at)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(account_id) DO UPDATE SET
               request_count = excluded.request_count,
               first_request_at = excluded.first_request_at,
               last_request_at = excluded.last_request_at,
               last_429_at = excluded.last_429_at""",
        (account_id, request_count, first_request_at, last_request_at, last_429_at),
    )
    conn.commit()
    conn.close()


def _fetch_account(account_id):
    """Читает строку account_stats напрямую из БД."""
    conn = sqlite3.connect(stats_client.DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM account_stats WHERE account_id = ?", (account_id,)
    ).fetchone()
    conn.close()
    return row


def _table_names():
    """Возвращает множество имён таблиц во временной БД."""
    conn = sqlite3.connect(stats_client.DB_PATH)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    return {row[0] for row in rows}


# --- init_db / init_accounts ---

def test_init_db_creates_tables():
    """init_db создаёт таблицы account_stats и request_log."""
    stats_client.init_db()
    assert {"account_stats", "request_log"} <= _table_names()


def test_init_db_idempotent():
    """Повторный init_db не падает и не ломает схему."""
    stats_client.init_db()
    stats_client.init_db()
    assert {"account_stats", "request_log"} <= _table_names()


def test_init_accounts_adds_zero_count():
    """init_accounts добавляет аккаунты с request_count=0 и NULL-таймстампами."""
    stats_client.init_accounts(["acc-1", "acc-2"])
    rows = {s["account_id"]: s for s in stats_client.get_all_stats()}
    assert set(rows) == {"acc-1", "acc-2"}
    for row in rows.values():
        assert row["request_count"] == 0
        assert row["first_request_at"] is None


def test_init_accounts_idempotent():
    """Повторный init_accounts не дублирует записи."""
    stats_client.init_accounts(["acc-1"])
    stats_client.init_accounts(["acc-1", "acc-2"])
    assert len(stats_client.get_all_stats()) == 2


# --- sync_accounts ---

def test_sync_accounts_removes_missing():
    """sync_accounts удаляет аккаунты и их логи, отсутствующие в списке."""
    stats_client.init_accounts(["a", "b", "c"])
    stats_client.record_request("a", 200, "m")
    stats_client.record_request("c", 200, "m")

    stats_client.sync_accounts(["a"])

    assert {s["account_id"] for s in stats_client.get_all_stats()} == {"a"}
    assert {r["account_id"] for r in stats_client.get_recent_requests()} == {"a"}


def test_sync_accounts_keeps_present():
    """sync_accounts сохраняет присутствующие аккаунты с их счётчиками."""
    stats_client.init_accounts(["a", "b"])
    stats_client.record_request("a", 200, "m")

    stats_client.sync_accounts(["a", "b"])

    rows = {s["account_id"]: s for s in stats_client.get_all_stats()}
    assert set(rows) == {"a", "b"}
    assert rows["a"]["request_count"] == 1


def test_sync_accounts_empty_removes_all():
    """Пустой список аккаунтов удаляет всё из обеих таблиц."""
    stats_client.init_accounts(["a", "b"])
    stats_client.record_request("a", 200, "m")

    stats_client.sync_accounts([])

    assert stats_client.get_all_stats() == []
    assert stats_client.get_recent_requests() == []


# --- record_request ---

def test_record_request_first(clock):
    """Первый запрос создаёт запись с request_count=1."""
    stats_client.record_request("acc", 200, "m", 5, 7)
    row = _fetch_account("acc")
    assert row["request_count"] == 1
    assert row["first_request_at"] == clock.now
    assert row["last_request_at"] == clock.now
    assert row["last_429_at"] is None


def test_record_request_increments(clock):
    """Повторные запросы инкрементируют request_count."""
    stats_client.record_request("acc", 200)
    stats_client.record_request("acc", 200)
    assert _fetch_account("acc")["request_count"] == 2


def test_record_request_429_sets_limit_and_timestamp(clock):
    """429 выставляет request_count=100 и заполняет last_429_at."""
    stats_client.record_request("acc", 200)
    stats_client.record_request("acc", 429)
    row = _fetch_account("acc")
    assert row["request_count"] == 100
    assert row["last_429_at"] == clock.now


def test_record_request_429_for_new_account_keeps_count_one(clock):
    """Баг: 429 у аккаунта без истории ставит request_count=1, но аккаунт считается доступным."""
    stats_client.record_request("new", 429)
    row = _fetch_account("new")
    assert row["request_count"] == 1
    assert row["last_429_at"] == clock.now
    assert stats_client.is_account_available("new") is True


def test_record_request_never_exceeds_100(clock):
    """request_count не превышает 100 (MIN(..., 100))."""
    _insert_account("acc", 99, clock.now, clock.now)
    stats_client.record_request("acc", 200)
    assert _fetch_account("acc")["request_count"] == 100
    stats_client.record_request("acc", 200)
    assert _fetch_account("acc")["request_count"] == 100


def test_record_request_resets_on_new_day(clock):
    """При смене суток счётчик начинается заново с 1."""
    old = clock.now - 2 * DAY
    _insert_account("acc", 50, old, old)
    stats_client.record_request("acc", 200)
    row = _fetch_account("acc")
    assert row["request_count"] == 1
    assert row["first_request_at"] == clock.now


def test_record_request_log_fields(clock):
    """record_request пишет запись в request_log с моделью и токенами."""
    stats_client.record_request("acc", 200, "free-x", 11, 22)
    log = stats_client.get_recent_requests()
    assert len(log) == 1
    assert log[0]["account_id"] == "acc"
    assert log[0]["model"] == "free-x"
    assert log[0]["input_tokens"] == 11
    assert log[0]["output_tokens"] == 22
    assert log[0]["status_code"] == 200


# --- get_all_stats ---

def test_get_all_stats_fields(clock):
    """get_all_stats возвращает ожидаемый набор полей и limit=100."""
    _insert_account("acc", 5, clock.now, clock.now)
    stats = stats_client.get_all_stats()
    assert len(stats) == 1
    item = stats[0]
    for field in ("account_id", "request_count", "limit", "status",
                  "first_request_at", "last_request_at", "last_429_at",
                  "resets_in_seconds", "reset_at"):
        assert field in item
    assert item["limit"] == 100


def test_get_all_stats_statuses(clock):
    """Статусы active/warning/exhausted вычисляются по счётчику и 429."""
    now = clock.now
    _insert_account("a-active", 5, now, now)
    _insert_account("b-warning", 85, now, now)
    _insert_account("c-exhausted-count", 100, now, now)
    _insert_account("d-exhausted-429", 10, now, now, now)

    stats = {s["account_id"]: s for s in stats_client.get_all_stats()}
    assert stats["a-active"]["status"] == "active"
    assert stats["b-warning"]["status"] == "warning"
    assert stats["c-exhausted-count"]["status"] == "exhausted"
    assert stats["d-exhausted-429"]["status"] == "exhausted"


def test_get_all_stats_resets_none_when_no_first_request(clock):
    """resets_in_seconds и reset_at равны None, если запросов ещё не было."""
    _insert_account("fresh", 0, None)
    item = stats_client.get_all_stats()[0]
    assert item["resets_in_seconds"] is None
    assert item["reset_at"] is None


# --- get_recent_requests ---

def test_get_recent_requests_order_and_format(clock):
    """Лог отдаётся по убыванию времени с форматированной датой."""
    conn = sqlite3.connect(stats_client.DB_PATH)
    conn.execute(
        "INSERT INTO request_log (account_id, timestamp, status_code, model) VALUES (?, ?, ?, ?)",
        ("a", clock.now - 100, 200, "m1"),
    )
    conn.execute(
        "INSERT INTO request_log (account_id, timestamp, status_code, model) VALUES (?, ?, ?, ?)",
        ("b", clock.now, 429, "m2"),
    )
    conn.commit()
    conn.close()

    log = stats_client.get_recent_requests()
    assert [r["account_id"] for r in log] == ["b", "a"]
    assert len(log[0]["datetime"]) == 16
    assert log[0]["datetime"][2] == "." and log[0]["datetime"][5] == "."


def test_get_recent_requests_unknown_model(clock):
    """NULL-модель в логе отображается как 'unknown'."""
    stats_client.record_request("a", 200, None)
    assert stats_client.get_recent_requests()[0]["model"] == "unknown"


def test_get_recent_requests_id_and_datetime_format(clock):
    """Запись лога содержит числовой id и дату строго в формате dd.mm.YYYY HH:MM."""
    stats_client.record_request("a", 200, "m")
    item = stats_client.get_recent_requests()[0]
    expected = datetime.fromtimestamp(clock.now).strftime("%d.%m.%Y %H:%M")
    assert isinstance(item["id"], int)
    assert item["datetime"] == expected
    assert re.fullmatch(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}", item["datetime"])


# --- is_account_available ---

def test_is_account_available_missing_account():
    """Аккаунт без записи в БД считается доступным."""
    assert stats_client.is_account_available("нет-такого") is True


def test_is_account_available_below_limit(clock):
    """Счётчик меньше 100 — аккаунт доступен."""
    _insert_account("acc", 99, clock.now, clock.now)
    assert stats_client.is_account_available("acc") is True


def test_is_account_available_exhausted(clock):
    """100 запросов в тех же сутках — аккаунт недоступен."""
    _insert_account("acc", 100, clock.now, clock.now)
    assert stats_client.is_account_available("acc") is False


def test_is_account_available_after_day_change(clock):
    """После смены суток исчерпанный аккаунт снова доступен."""
    _insert_account("acc", 100, clock.now - DAY, clock.now - DAY)
    assert stats_client.is_account_available("acc") is True


# --- check_daily_reset ---

def test_check_daily_reset_resets_old_accounts(clock):
    """check_daily_reset обнуляет счётчик и last_429_at у аккаунтов прошлого дня."""
    old = clock.now - 2 * DAY
    _insert_account("old", 50, old, old, old)

    stats_client.check_daily_reset()

    row = _fetch_account("old")
    assert row["request_count"] == 0
    assert row["last_429_at"] is None
    assert row["first_request_at"] == clock.now


def test_check_daily_reset_keeps_today(clock):
    """Аккаунты текущих суток не сбрасываются."""
    _insert_account("today", 30, clock.now, clock.now)

    stats_client.check_daily_reset()

    assert _fetch_account("today")["request_count"] == 30


def test_check_daily_reset_skips_null_first_request(clock):
    """Аккаунты с first_request_at=NULL не сбрасываются."""
    _insert_account("fresh", 7, None)

    stats_client.check_daily_reset()

    row = _fetch_account("fresh")
    assert row["request_count"] == 7
    assert row["first_request_at"] is None


# --- get_account_states ---

def test_get_account_states_variants(clock):
    """resets_in=0 при смене суток, >0 в тех же сутках, 0 при None."""
    now = clock.now
    _insert_account("old", 10, now - DAY, now - DAY)
    _insert_account("today", 10, now, now)
    _insert_account("fresh", 0, None)

    states = stats_client.get_account_states()

    assert states["old"]["resets_in"] == 0
    assert 0 < states["today"]["resets_in"] <= DAY
    assert states["fresh"]["resets_in"] == 0
    assert states["fresh"]["first_request_at"] is None
