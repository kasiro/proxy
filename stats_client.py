"""Клиент для записи статистики запросов в SQLite БД."""
import asyncio
import time
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "stats.db"


def init_db():
    """Инициализировать базу данных."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Включаем WAL режим для уменьшения блокировок при чтении/записи
    cursor.execute("PRAGMA journal_mode=WAL")
    
    # Таблица статистики аккаунтов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS account_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT UNIQUE NOT NULL,
            request_count INTEGER DEFAULT 0,
            first_request_at INTEGER,
            last_request_at INTEGER,
            last_429_at INTEGER
        )
    """)
    
    # Таблица логов запросов (опционально)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            status_code INTEGER NOT NULL,
            model TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER
        )
    """)
    
    conn.commit()
    conn.close()


def record_request(account_id: str, status_code: int, model: str | None = None, input_tokens: int | None = None, output_tokens: int | None = None):
    """
    Записать статистику запроса.
    
    Args:
        account_id: ID аккаунта (из заголовка new-api-user)
        status_code: HTTP статус ответа
        model: Название модели
        input_tokens: Количество входных токенов
        output_tokens: Количество выходных токенов
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Убеждаемся что WAL режим включён (на случай если БД создана старой версией)
    cursor.execute("PRAGMA journal_mode=WAL")
    
    # Блокируем запись для других потоков до завершения транзакции (защита от race condition)
    conn.execute("BEGIN IMMEDIATE")
    
    now = int(time.time())
    
    # Проверяем существование аккаунта
    cursor.execute(
        "SELECT first_request_at FROM account_stats WHERE account_id = ?",
        (account_id,)
    )
    row = cursor.fetchone()
    
    if row is None:
        # Первый запрос для этого аккаунта
        cursor.execute(
            """INSERT INTO account_stats 
               (account_id, request_count, first_request_at, last_request_at, last_429_at)
               VALUES (?, 1, ?, ?, ?)""",
            (account_id, now, now, now if status_code == 429 else None)
        )
    else:
        first_request_at = row[0] if row[0] is not None else now
        
        # Если first_request_at был NULL, обновляем его
        if row[0] is None:
            cursor.execute(
                """UPDATE account_stats 
                   SET first_request_at = ?, request_count = ?, last_request_at = ?, last_429_at = ?
                   WHERE account_id = ?""",
                (now, 100 if status_code == 429 else 1, now, now if status_code == 429 else None, account_id)
            )
        else:
            # Сброс в 00:00 UTC (разные сутки)
            if now // 86400 > first_request_at // 86400:
                # Сброс: обнуляем счётчик, обновляем first_request_at на сегодня
                cursor.execute(
                    """UPDATE account_stats 
                       SET request_count = 1, first_request_at = ?, last_request_at = ?, last_429_at = ?
                       WHERE account_id = ?""",
                    (now, now, now if status_code == 429 else None, account_id)
                )
            else:
                # Инкремент
                if status_code == 429:
                    # 429 означает лимит исчерпан — ставим 100
                    cursor.execute(
                        """UPDATE account_stats 
                           SET request_count = 100, last_request_at = ?, last_429_at = ?
                           WHERE account_id = ?""",
                        (now, now, account_id)
                    )
                else:
                    cursor.execute(
                        """UPDATE account_stats 
                           SET request_count = MIN(request_count + 1, 100), last_request_at = ?
                           WHERE account_id = ?""",
                        (now, account_id)
                    )
    
    # Лог запроса
    cursor.execute(
        """INSERT INTO request_log 
           (account_id, timestamp, status_code, model, input_tokens, output_tokens) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (account_id, now, status_code, model, input_tokens, output_tokens)
    )
    
    conn.commit()
    conn.close()


async def record_request_async(account_id: str, status_code: int, model: str | None = None, input_tokens: int | None = None, output_tokens: int | None = None):
    """Асинхронная версия record_request."""
    await asyncio.to_thread(record_request, account_id, status_code, model, input_tokens, output_tokens)


def get_all_stats() -> list[dict]:
    """Получить всю статистику по аккаунтам."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM account_stats ORDER BY account_id")
    rows = cursor.fetchall()
    
    now = int(time.time())
    result = []
    
    for row in rows:
        if row["first_request_at"] is None:
            # Аккаунт ещё не делал запросов — отсчёт не начался
            resets_in = None
            first_request_at = None
            reset_at = None
        else:
            first_request_at = row["first_request_at"]
            # reset_at = следующая полночь UTC
            next_midnight = (now // 86400 + 1) * 86400
            resets_in = max(0, next_midnight - now)
            reset_at = next_midnight
        
        # Определение статуса
        if row["last_429_at"] and row["last_429_at"] >= first_request_at:
            status = "exhausted"
        elif row["request_count"] >= 100:
            status = "exhausted"
        elif row["request_count"] >= 80:
            status = "warning"
        else:
            status = "active"
        
        result.append({
            "account_id": row["account_id"],
            "request_count": row["request_count"],
            "limit": 100,
            "first_request_at": first_request_at,
            "last_request_at": row["last_request_at"],
            "last_429_at": row["last_429_at"],
            "resets_in_seconds": resets_in,
            "reset_at": reset_at,
            "status": status
        })
    
    conn.close()
    return result


def get_recent_requests(limit: int | None = None) -> list[dict]:
    """
    Получить ВСЕ запросы из лога.
    
    Args:
        limit: НЕ используется — брать все данные
        
    Returns:
        Список словарей с информацией о запросах
    """
    from datetime import datetime
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Брать ВСЕ запросы (без LIMIT)
    cursor.execute("""
        SELECT id, account_id, timestamp, status_code, model, input_tokens, output_tokens 
        FROM request_log 
        ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        dt = datetime.fromtimestamp(row["timestamp"])
        result.append({
            "id": row["id"],
            "datetime": dt.strftime("%d.%m.%Y %H:%M"),
            "account_id": row["account_id"],
            "model": row["model"] or "unknown",
            "input_tokens": row["input_tokens"],
            "output_tokens": row["output_tokens"],
            "status_code": row["status_code"]
        })
    
    conn.close()
    return result


def get_account_states() -> dict[str, dict]:
    """
    Получить состояние всех аккаунтов: request_count, first_request_at, resets_in.
    Возвращает dict: {account_id: {"request_count": int, "first_request_at": int|None, "resets_in": int}}
    """
    now = int(time.time())

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT account_id, request_count, first_request_at FROM account_stats")
    rows = cursor.fetchall()

    result = {}
    for row in rows:
        first_at = row["first_request_at"]
        if first_at is not None and now // 86400 > first_at // 86400:
            resets_in = 0  # Уже сбросился (новые сутки)
        elif first_at is not None:
            next_midnight = (now // 86400 + 1) * 86400
            resets_in = max(0, next_midnight - now)
        else:
            resets_in = 0

        result[row["account_id"]] = {
            "request_count": row["request_count"],
            "first_request_at": first_at,
            "resets_in": resets_in
        }

    conn.close()
    return result


def is_account_available(account_id: str) -> bool:
    """
    Проверить доступен ли аккаунт (request_count < 100 или уже сбросился).
    """
    now = int(time.time())

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT request_count, first_request_at FROM account_stats WHERE account_id = ?", (account_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return True  # Нет записи — аккаунт новый, доступен

    if row["request_count"] < 100:
        return True  # Ещё есть место

    # Проверить сброс (00:00 UTC — разные сутки)
    if row["first_request_at"] is not None and now // 86400 > row["first_request_at"] // 86400:
        return True  # Сбросился

    return False  # Исчерпан


def check_daily_reset():
    """
    Проверить и выполнить дневной сброс.
    Сброс происходит в 00:00 UTC (07:00 Новосибирск).
    Если текущие сутки отличаются от дня первого запроса — сбросить счётчик.
    Вызывать при старте приложения.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Блокируем запись для других потоков до завершения транзакции
    conn.execute("BEGIN IMMEDIATE")

    now = int(time.time())
    today = now // 86400  # Текущие сутки UTC

    # Найти аккаунты которые ещё не сброшены сегодня
    cursor.execute("""
        SELECT account_id, first_request_at FROM account_stats
        WHERE first_request_at IS NOT NULL
    """)
    rows = cursor.fetchall()

    reset_count = 0
    for row in rows:
        account_id = row[0]
        first_day = row[1] // 86400

        if today > first_day:
            # Разные сутки — сбросить
            cursor.execute("""
                UPDATE account_stats
                SET request_count = 0, first_request_at = ?, last_429_at = NULL
                WHERE account_id = ?
            """, (now, account_id))
            reset_count += 1

    conn.commit()
    conn.close()

    if reset_count > 0:
        print(f"[stats] Дневной сброс: {reset_count} аккаунтов обнулено")
    else:
        print("[stats] Дневной сброс: все аккаунты уже сброшены или нет данных")


def init_accounts(account_ids: list[str]):
    """
    Инициализировать БД реальными аккаунтами.
    Добавляет отсутствующие аккаунты с request_count=0.
    
    Args:
        account_ids: Список ID аккаунтов для инициализации
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = int(time.time())
    
    for account_id in account_ids:
        # Проверяем существование
        cursor.execute(
            "SELECT account_id FROM account_stats WHERE account_id = ?",
            (account_id,)
        )
        if cursor.fetchone() is None:
            # Добавляем новый аккаунт с нулевым счётчиком
            cursor.execute(
                """INSERT INTO account_stats 
                   (account_id, request_count, first_request_at, last_request_at, last_429_at)
                   VALUES (?, 0, NULL, NULL, NULL)""",
                (account_id,)
            )
    
    conn.commit()
    conn.close()
