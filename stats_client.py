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
            # Проверка на сброс (24 часа)
            if now - first_request_at > 86400:
                # Сброс счётчика
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
                           SET request_count = request_count + 1, last_request_at = ?
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
            resets_in = max(0, 86400 - (now - first_request_at))
            reset_at = first_request_at + 86400
        
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


def get_recent_requests(limit: int = 50) -> list[dict]:
    """
    Получить последние запросы из лога.
    
    Args:
        limit: Максимальное количество записей
        
    Returns:
        Список словарей с информацией о запросах
    """
    from datetime import datetime
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM request_log 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        dt = datetime.fromtimestamp(row["timestamp"])
        result.append({
            "datetime": dt.strftime("%d.%m.%Y %H:%M"),
            "account_id": row["account_id"],
            "model": row["model"] or "unknown",
            "input_tokens": row["input_tokens"],
            "output_tokens": row["output_tokens"],
            "status_code": row["status_code"]
        })
    
    conn.close()
    return result


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
