This file is a merged representation of the entire codebase, combined into a single document by Repomix.
The content has been processed where security check has been disabled.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching default ignore patterns are excluded
- Security check has been disabled - content may contain sensitive information
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
accaunts.py
count_accounts.py
dashboard.py
INFO.md
LOGGING.md
NEWS.md
proxy_launcher.py
QUICKSTART.md
setup.sh
stats_client.py
test_logging.py
test_proxy.py
test_response.py
TODO.md
utils.py
```

# Files

## File: NEWS.md
````markdown
# Changelog

## 2026-11-23: Stream chunks → прямая отдача без накопления в память

**Проблема:** `collect_and_check_stream()` собирал весь поток в список `chunks`, затем передавал `iter(chunks)` в `StreamingResponse`. Это создавало задержку до начала отдачи клиенту.

**Решение:** Прямой возврат `StreamingResponse` на генератор из `collect_and_check_stream()`.

**Было:**
```python
chunks = []
for chunk in collect_and_check_stream():
    chunks.append(chunk)
return StreamingResponse(iter(chunks), ...)
```

**Стало:**
```python
return StreamingResponse(collect_and_check_stream(), ...)
```

То же самое для retry-loop после переключения аккаунта (строки ~633+).

**Сохранена:**
- Ловля `BanDetectedException` вокруг `StreamingResponse`
- Проверка бана в каждом чанке
- Accumulation choices для пост-проверки после `[DONE]`
- Запись статистики токенов
````

## File: count_accounts.py
````python
from utils import curl_to_python
from accaunts import ACCOUNTS
import json

def dump(data) -> str:
    return json.dumps(
        data,
        ensure_ascii=False,
        indent=4
    )

len_ = len(ACCOUNTS)

count = 0
for i in range(len_):
    d = curl_to_python(ACCOUNTS[i])
    id_ = d['headers']['new-api-user']
    new = True if 'tmr_lvid' in d['cookies'].keys() else False
    print(id_, ':', 'account is updated...' if new else 'not updated')
    if new:
        count += 1

proc = count * 100 / len_
print('updated count:', f'{count}/{len_}', f'{round(proc, 2)}%')
````

## File: LOGGING.md
````markdown
# Логирование proxy

## Режимы работы

### 1. Обычный режим (по умолчанию)

```bash
python proxy_launcher.py
```

**Поведение:**
- `[retry]` логи (переключение аккаунтов, 429 ошибки) → **консоль + файл**
- `[proxy]` логи (запросы к API) → **только файл** (`proxy_launcher.log`)
- Запросы/ответы proxy → **только файл**

**Использование:** повседневная работа, когда не нужно отлаживать запросы.

---

### 2. Debug режим

**Способ 1: через переменную окружения**
```bash
PROXY_DEBUG=1 python proxy_launcher.py
```

Или через экспорт:
```bash
export PROXY_DEBUG=1
python proxy_launcher.py
```

**Способ 2: через флаг --debug**
```bash
python proxy_launcher.py --debug
```

**Поведение:**
- `[retry]` логи → **консоль + файл**
- `[proxy]` логи (запросы к API) → **консоль + файл**
- Payload запросов (без tools и system messages) → **консоль + файл**
- Статусы ответов (200, 429, др.) → **консоль + файл**

**Использование:** отладка проблем с запросами, анализ payload'ов.

---

## Структура логов

### Файл: `proxy_launcher.log`

Содержит **все** логи от обоих процессов (proxy + compat) с метками времени:

```
[2026-09-15 13:45:00] [Launcher] Рабочая директория: /home/kasiro/Документы/python_projects/test_revers_proxy
[2026-09-15 13:45:01] [proxy] [retry] Переключён на аккаунт 2/5
[2026-09-15 13:45:01] [proxy] [proxy] Request to https://api.opencode.ai/v1/chat/completions
[2026-09-15 13:45:02] [proxy] [proxy] Response: 200 OK (аккаунт 2)
```

### Консоль

**Обычный режим:**
```
[retry] Переключён на аккаунт 2/5
[retry] Аккаунт 2 вернул 429 (попытка 2/5)
```

**Debug режим:**
```
[retry] Переключён на аккаунт 2/5
[proxy] Request to https://api.opencode.ai/v1/chat/completions
{
  "group": "default",
  "messages": [...],
  "model": "free-qwen3.5-plus",
  "stream": true
}
[proxy] Response: 200 OK (аккаунт 2)
```

---

## Настройки

### Переменные окружения

| Переменная | Значение | Описание |
|------------|----------|----------|
| `PROXY_DEBUG` | `0` (default) / `1` | Включает детальное логирование запросов proxy |

### Аргументы командной строки

```bash
python proxy_launcher.py --help
```

- `--proxy-port <port>` — порт proxy (по умолчанию: 5000)
- `--compat-port <port>` — порт compat proxy (по умолчанию: 9625)
- `--upstream-url <url>` — URL upstream для compat proxy
- `--reload` — hot-reload для uvicorn
- `--debug` — включить debug логи proxy (запросы/ответы)

---

## Примеры использования

### 1. Запуск в фоне с логированием

```bash
nohup python proxy_launcher.py > proxy_console.log 2>&1 &
```

### 2. Просмотр логов в реальном времени

```bash
tail -f proxy_launcher.log
```

### 3. Отладка 429 ошибок

```bash
PROXY_DEBUG=1 python proxy_launcher.py | grep -E "\[retry\]|\[proxy\]"
```

### 4. Фильтрация только payload'ов

```bash
PROXY_DEBUG=1 python proxy_launcher.py 2>&1 | grep -A 20 "^{"
```

---

## Безопасность

Функция `safe_print_payload()` автоматически скрывает:
- Поле `tools` из запросов
- Сообщения с `role: "system"`

Это предотвращает утечку системных промптов и инструментов в логи.

**Важно:** даже в debug режиме не логируются:
- API ключи
- Cookies
- Заголовки авторизации
````

## File: QUICKSTART.md
````markdown
# Быстрый старт: логирование proxy

## Запуск

### Обычный режим (только retry на консоль)
```bash
python proxy_launcher.py
```

### Debug режим (все логи на консоль)
```bash
# Вариант 1: через переменную окружения
PROXY_DEBUG=1 python proxy_launcher.py

# Вариант 2: через флаг
python proxy_launcher.py --debug
```

## Куда что пишется

| Лог | Обычный режим | Debug режим |
|-----|---------------|-------------|
| `[retry]` переключение аккаунтов | консоль + файл | консоль + файл |
| `[retry]` 429 ошибки | консоль + файл | консоль + файл |
| `[proxy]` запросы к API | только файл | консоль + файл |
| `[proxy]` статусы ответов | только файл | консоль + файл |
| Payload запросов | только файл | консоль + файл |

## Файлы

- `proxy_launcher.log` — полный лог всех событий
- `LOGGING.md` — подробная документация
- `test_logging.py` — тест системы логирования

## Примеры

### 1. Запуск в фоне
```bash
nohup python proxy_launcher.py > proxy_console.log 2>&1 &
```

### 2. Мониторинг в реальном времени
```bash
tail -f proxy_launcher.log
```

### 3. Отладка 429 ошибок
```bash
python proxy_launcher.py --debug 2>&1 | grep "\[retry\]"
```

### 4. Просмотр payload'ов
```bash
PROXY_DEBUG=1 python proxy_launcher.py 2>&1 | grep -A 15 "^{"
```
````

## File: test_logging.py
````python
#!/usr/bin/env python3
"""
Тест системы логирования proxy.

Запуск:
    python test_logging.py                 # обычный режим
    python test_logging.py --debug         # debug режим
"""

import argparse
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Тест логирования proxy")
    parser.add_argument("--debug", action="store_true", help="Запустить в debug режиме")
    parser.add_argument("--duration", type=int, default=5, help="Длительность теста в секундах")
    return parser.parse_args()

def main():
    args = parse_args()
    
    workdir = Path(__file__).parent.resolve()
    log_file = workdir / "proxy_launcher.log"
    
    # Очистить лог файл перед тестом
    if log_file.exists():
        log_file.unlink()
        print(f"[test] Очистка лог файла: {log_file}")
    
    # Сформировать окружение
    env = os.environ.copy()
    if args.debug:
        env["PROXY_DEBUG"] = "1"
        print("[test] Запуск в DEBUG режиме (PROXY_DEBUG=1)")
    else:
        print("[test] Запуск в обычном режиме")
    
    # Запустить proxy_launcher.py
    print(f"[test] Запуск proxy_launcher.py на {args.duration} секунд...")
    
    proc = subprocess.Popen(
        [sys.executable, "proxy_launcher.py"],
        env=env,
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    
    # Ждём указанное время
    try:
        time.sleep(args.duration)
    except KeyboardInterrupt:
        print("\n[test] Прервано пользователем")
    
    # Остановить процесс
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    
    print(f"\n[test] Процесс завершён (код {proc.returncode})")
    
    # Проверить лог файл
    if log_file.exists():
        print(f"\n[test] Лог файл создан: {log_file}")
        print(f"[test] Размер: {log_file.stat().st_size} байт")
        
        # Показать последние 10 строк
        print("\n[test] Последние 10 строк лога:")
        print("-" * 60)
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    print(line.rstrip())
        except Exception as e:
            print(f"[test] Ошибка чтения лога: {e}")
        print("-" * 60)
    else:
        print(f"\n[test] WARNING: лог файл не создан!")
    
    print("\n[test] Тест завершён")

if __name__ == "__main__":
    main()
````

## File: TODO.md
````markdown
## fix

## начато


## под вопросом (пофикшено?) (проверить)
- перестать делать запросы к тем аккаунтам которые вернули 429 ранее.
- токены через какое то время вообще куда то пропадают (уменьшаются) + модели тоже из фильтра куда то пропадают... и аккаунты тоже... испаряются?
- сброс лимитов в 7:00 утра по Новосибирску. (UTC+7 00:00)
- токены за сегодня отображаются ещё со вчерашнего дня.
- каким то чудом выпадает 101/100 пофиксить. и придумать чё делать. переопределять на 100?
    * account_6683 - 101

## пофикшено с багом
- переделать дизайн + переделать дизайн тёмной темы
    * у кнопок пресетов сделать белый текст в тёмной теме а не серый

## пофикшено 100%.
- а надо делать накопление! + пагинацию надо сделать для последней таблички. + брать все данные из бд. даже если они старые.
- надо сделать для последней таблицы пагинацию по страницам!
    * при перелистывании длинна списка умножается на 2 на 4 на 8 но не происходит фиксированного перелистывания
- поиск в фильтре вообще не работает (удалён)
- у тебя все поля ввода очень высокие, убавь высоту на четверть.
````

## File: utils.py
````python
"""Утилиты для парсинга curl-команд и извлечения account_id."""
import re
import json


def curl_to_python(curl_text: str):
    """Преобразует curl-команду в словарь с url, method, headers, cookies, data."""
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
        method = re.search(r'-X\s+(\w+)', curl_text).group(1)

    return {
        'url': url,
        'method': method,
        'headers': headers,
        'cookies': cookies,
        'data': data,
    }


def extract_account_ids_from_accounts(accounts: list[str]) -> list[str]:
    """
    Извлекает account_id из списка curl-команд ACCOUNTS.
    
    Args:
        accounts: Список curl-команд из accaunts.py
        
    Returns:
        Список account_id (из заголовка new-api-user)
    """
    account_ids = []
    for acc_curl in accounts:
        parsed = curl_to_python(acc_curl)
        account_id = parsed['headers'].get('new-api-user', 'unknown')
        account_ids.append(account_id)
    return account_ids
````

## File: INFO.md
````markdown
# INFO — kasiro-proxy

## Назначение
Reverse-proxy для OpenRouter-подобного API (odirouter.ai) с пулом аккаунтов, переключением при бане/лимите и дашбордом статистики.

## Файлы проекта
- `proxy_launcher.py` — запуск uvicorn-процессов proxy (:5000) и dashboard (:5001). Флаги: `--dashboard`, `--dashboard-port`, `--proxy-port`, `--proxy-app`, `--debug`, `--reload`.
- `test_proxy.py` — FastAPI-приложение proxy: `/v1/models`, `/v1/chat/completions`.
- `dashboard.py` — FastAPI дашборд: `/`, `/api/stats`, `/api/record`, `/sse/stats`; lifespan: `init_db` → `extract_account_ids_from_accounts` → `init_accounts` → `sync_accounts` → `check_daily_reset`.
- `stats_client.py` — SQLite (`stats.db`): таблицы `account_stats`, `request_log`; `init_db`, `record_request`, `record_request_async`, `get_all_stats`, `get_recent_requests`, `get_account_states`, `is_account_available`, `check_daily_reset`, `init_accounts`, `sync_accounts`.
- `accaunts.py` — ЕДИНСТВЕННЫЙ источник правды по аккаунтам: список `ACCOUNTS` с curl-командами (ID берётся из заголовка `new-api-user`).
- `utils.py` — `curl_to_python()`, `extract_account_ids_from_accounts()`.
- `test_response.py` — ручной тест прокси.
- `templates/dashboard.html` — UI (Jinja2 delimiters `[[ ]]`, задаётся в `dashboard.py`).

## Ключевые механизмы
- Аккаунты: `accaunts.py` → `extract_account_ids_from_accounts` → `ACCOUNT_IDS`.
- `sync_accounts()`: при старте dashboard удаляет из `account_stats` и `request_log` аккаунты, отсутствующие в `accaunts.py`.
- `init_accounts()`: `INSERT OR IGNORE` (защита от `UNIQUE constraint failed` при рестарте).
- Счётчик: `request_count`, лимит 100/сутки, сброс в 00:00 UTC, `429` → `request_count=100` + `last_429_at`.
- `X-Test-Account-ID` (заголовок): принудительный выбор аккаунта по ID для отладки; `is_test_request=True` → при бане НЕТ переключения, сразу ошибка клиенту.
- Бан: upstream при бане отдаёт HTTP 200 + JSON `{"message": "Пользователь заблокирован", "success": false}` даже при `stream=true`.
- `BanDetectedException`: поднимается из `collect_and_check_stream()`; сбор чанков выполняется ДО создания `StreamingResponse` (`chunks = [...]; StreamingResponse(iter(chunks))`) — иначе retry невозможен.
- `401` и `429` в stream-режиме → `BanDetectedException` → `switch_account` + повторный запрос.
- Таймауты: `timeout=180` в обоих `session.post`; `HTTPAdapter(max_retries=Retry(total=2, backoff_factor=0.5, status_forcelist=[502, 503, 504]))`.
- `stats.db` и `*-wal`/`*-shm` — в `.gitignore` (маски `*.db`, `stats.db*`), удалены из git-трекинга (коммит 422f153).

## Известные баги / нюансы (актуально на 2026-11-22)
1. При бане в `stream=true` клиенту возвращается обычный JSON 403 (`{"error": "All accounts are banned", ...}`) вместо SSE-формата `data: {"error": ...}` → строгие SSE-клиенты (OpenAI SDK со `stream=True`) могут падать на парсинге.
2. У этого 403-ответа отсутствует заголовок `content-type`.
3. Лог печатает `[retry] Бан детектирован: ... Переключаем аккаунт...` ДО проверки `is_test_request`, затем `Бан найден в тестовом режиме` — сообщения вводят в заблуждение.
4. `pkill -f 'uvicorn test_proxy:app'` убивает собственную bash-оболочку (паттерн совпадает с cmdline) → убивать по PID через `ps -eo pid,args | rg '[u]vicorn'`.
5. `pgrep` заблокирован bash-фильтром `*grep*` → использовать `ps | rg`.
6. dashboard: старый uvicorn-процесс может висеть «зомби» и не отдавать порт, SIGTERM не берёт → `kill -9` по PID.

## Production-баги (найдены при покрытии тестами, 2026-11-22) — [x] все 4 починены 2026-11-22
1. [x] **Фильтр think-тегов в stream мёртв** — `strip_think_from_sse_line(line)` вызывается (test_proxy.py стр. ~487/556), но результат отбрасывается: yield идёт по оригиналу `line`.
2. [x] **Не-JSON тело upstream роняет запрос** — `json.loads(resp.content)` (стр. ~399) без try/except; ветка `except JSONDecodeError` (стр. ~682-683) недостижима.
3. [x] **Regex tool_calls не захватывает `}`** (стр. ~699) → `json.loads` падает → 500 (стр. ~706-707 недостижимы).
4. [x] **`check_account_ban` на пустом `choices` → IndexError** вместо False (стр. ~37).

Статус: [x] починены все 4 (py_compile чистый, 101 passed). Regex tool_calls: паттерн `.*\]\}` + try/except — извлечение tool_calls из текста работает.

## Совместимость SSE-ошибок (уточнение на 2026-11-22)

Пункты 1–2 выше устарели: формат ответа при бане в `stream=true` изменён на SSE.

1. Текущий ответ при бане в `stream=true`: HTTP `403` + `content-type: text/event-stream`, тело `data: {"error": ..., "detail": ...}\n\ndata: [DONE]\n\n` (97 байт, с `Content-Length`, НЕ chunked). Формат валиден по спеке SSE (проверено парсером), НО клиенты `openai-python`/OpenCode на 4xx бросают `APIStatusError`, не читая тело → SSE-ошибка может быть отброшена. Альтернатива при необходимости: `200` + SSE-событие ошибки.
2. В SSE-ответе ошибки нет `Cache-Control: no-cache` (best practice для SSE).
3. Схема ошибки не OpenAI-совместима: `{"error": "<строка>", "detail": ...}` вместо `{"error": {"message": ..., "type": ..., "code": ...}}`.
4. Наблюдение из логов: большинство аккаунтов пула отдают `401 Unauthorized` или `429` — вероятно, истекли cookies/session (нужна переавторизация). Аккаунт `11466` вернул `403 model_not_allowed` для `free-gemini-2.5-flash` — модель не разрешена на этом аккаунте; цикл retry прерывается на статусах кроме `429`/`401`.
5. Перезапуск: НЕ использовать `pkill -f` (убивает собственную оболочку). PID искать через `ps -eo pid,args | rg '[u]vicorn (test_proxy|dashboard):app'`, затем `kill`; dashboard может требовать `kill -9`. Запуск: `nohup .venv/bin/python proxy_launcher.py --dashboard > /tmp/opencode/launcher_run.log 2>&1 &`.

## Проверка
```bash
curl -sS -N -m 60 -X POST http://localhost:5000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H 'X-Test-Account-ID: 11940' \
  -d '{"model":"free-qwen3.5-plus","messages":[{"role":"user","content":"Привет"}],"stream":true}'
```
- Дашборд: http://localhost:5001
````

## File: dashboard.py
````python
"""Dashboard для мониторинга запросов OpenRouter аккаунтов."""
import json
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from stats_client import init_db, record_request_async, get_all_stats, init_accounts, sync_accounts, get_recent_requests, check_daily_reset
from accaunts import ACCOUNTS
from utils import extract_account_ids_from_accounts


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    ACCOUNT_IDS = extract_account_ids_from_accounts(ACCOUNTS)
    init_accounts(ACCOUNT_IDS)
    sync_accounts(ACCOUNT_IDS)
    check_daily_reset()
    yield


app = FastAPI(title="OpenRouter Dashboard", lifespan=lifespan)

# Шаблоны
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=templates_dir)
# Изменяем delimiters Jinja2 чтобы не конфликтовали с Vue.js {{ }}
templates.env.variable_start_string = '[['
templates.env.variable_end_string = ']]'


class RecordRequest(BaseModel):
    account_id: str
    status_code: int


@app.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Веб-интерфейс dashboard."""
    return templates.TemplateResponse(request, "dashboard.html", context={"request": request})


@app.get("/api/stats", response_class=JSONResponse)
async def get_stats():
    """Получить всю статистику по аккаунтам."""
    stats = get_all_stats()
    return JSONResponse(content=stats)


@app.post("/api/record")
async def record_stats(record: RecordRequest):
    """Записать статистику запроса."""
    await record_request_async(record.account_id, record.status_code)
    return {"status": "ok"}


@app.get("/sse/stats")
async def sse_stats() -> StreamingResponse:
    """SSE поток для обновлений в реальном времени."""
    
    async def generate() -> AsyncGenerator[str, None]:
        try:
            while True:
                stats = get_all_stats()
                requests = get_recent_requests(limit=None)  # Брать все данные
                yield f"data: {json.dumps({'stats': stats, 'requests': requests}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.5)  # Обновление каждые 500мс
        except asyncio.CancelledError:
            raise
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


if __name__ == "__main__":
    import signal
    import os
    
    config = uvicorn.Config(
        "dashboard:app",
        host="localhost",
        port=5001,
        reload=False,
        log_level="info",
        timeout_keep_alive=0,  # Немедленно закрывать keep-alive соединения
        timeout_notify=0,      # Немедленно закрывать уведомления
        timeout_graceful_shutdown=0,  # Без ожидания graceful shutdown
    )
    server = uvicorn.Server(config)
    
    def handle_sigint(signum, frame):
        """Принудительное завершение при Ctrl+C."""
        server.should_exit = True
        os._exit(0)  # Мгновенный выход без cleanup
    
    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGTERM, handle_sigint)
    
    server.run()
````

## File: stats_client.py
````python
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
                """INSERT OR IGNORE INTO account_stats 
                   (account_id, request_count, first_request_at, last_request_at, last_429_at)
                   VALUES (?, 0, NULL, NULL, NULL)""",
                (account_id,)
            )
    
    conn.commit()
    conn.close()


def sync_accounts(account_ids: list[str]):
    """
    Синхронизировать БД с актуальным списком аккаунтов.
    Удаляет из БД аккаунты, которых нет в accaunts.py.
    
    Args:
        account_ids: Список ID аккаунтов из accaunts.py (актуальный список)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Получить все account_id из БД
    cursor.execute("SELECT account_id FROM account_stats")
    db_accounts = {row[0] for row in cursor.fetchall()}
    
    # Преобразовать список в множество для быстрого сравнения
    actual_accounts = set(account_ids)
    
    # Найти аккаунты для удаления (есть в БД, но нет в accaunts.py)
    to_remove = db_accounts - actual_accounts
    
    if to_remove:
        # Удалить из account_stats
        placeholders = ",".join("?" * len(to_remove))
        cursor.execute(
            f"DELETE FROM account_stats WHERE account_id IN ({placeholders})",
            list(to_remove)
        )
        
        # Удалить из request_log
        cursor.execute(
            f"DELETE FROM request_log WHERE account_id IN ({placeholders})",
            list(to_remove)
        )
        
        conn.commit()
        print(f"[stats] Синхронизация: удалено {len(to_remove)} аккаунтов: {to_remove}")
    else:
        print("[stats] Синхронизация: все аккаунты актуальны")
    
    conn.close()
````

## File: proxy_launcher.py
````python
#!/usr/bin/env python3
"""
Launcher для запуска трёх uvicorn-процессов: proxy, compat и dashboard.

Запускает:
  - proxy: uvicorn на порту 5000 (test_proxy:app из корня проекта)
  - dashboard: uvicorn на порту 5001 (dashboard:app из корня проекта)

Все процессы работают в фоне, основной процесс ждёт их завершения.
При Ctrl+C — лаунчер завершается мгновенно, НЕ убивая proxy-процессы (они остаются работать в фоне).

Использование:
    python proxy_launcher.py                                 # по умолчанию: test_proxy:app + opencode_compat_proxy/proxy:app
    python proxy_launcher.py --proxy-app custom:app          # кастомное proxy приложение
    python proxy_launcher.py --dashboard                     # запустить также dashboard на порту 5001
    python proxy_launcher.py --dashboard --dashboard-port 8080  # dashboard на кастомном порту
"""

import argparse
import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Запуск uvicorn-процесса reverse proxy"
    )
    parser.add_argument(
        "--proxy-app",
        type=str,
        default="test_proxy:app",
        help="Uvicorn приложение для proxy в формате module:app (по умолчанию: test_proxy:app)"
    )
    parser.add_argument(
        "--proxy-port",
        type=int,
        default=5000,
        help="Порт для proxy (по умолчанию: 5000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Включить hot-reload для uvicorn"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Включить debug логи proxy (запросы/ответы)"
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Запустить dashboard вместе с proxy"
    )
    parser.add_argument(
        "--dashboard-port",
        type=int,
        default=5001,
        help="Порт для dashboard (по умолчанию: 5001)"
    )
    return parser.parse_args()


def create_process(name, cmd, env=None, cwd=None, logger=None):
    """Создаёт дочерний процесс и возвращает объект Popen."""
    if logger:
        logger.info("[%s] Запуск: %s", name, " ".join(cmd))
        if cwd:
            logger.info("[%s] Рабочая директория: %s", name, cwd)
    else:
        print(f"[{name}] Запуск: {' '.join(cmd)}")
        if cwd:
            print(f"[{name}] Рабочая директория: {cwd}")
    process = subprocess.Popen(
        cmd,
        env=env,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # Line buffered
    )
    return process


def stream_output(process, prefix, logger, output_to_console=True, console_filter=None):
    """
    Поток для чтения вывода процесса.
    Читает пока процесс жив или пока есть данные в буфере.
    Пишет в лог и (опционально) на консоль без блокировки основного цикла.
    
    Args:
        process: subprocess.Popen объект
        prefix: префикс для логов
        logger: logger объект
        output_to_console: если True — выводить на консоль, если False — только в файл
        console_filter: если задано — выводить на консоль только строки содержащие этот текст
    """
    try:
        for line in process.stdout:
            if line:
                line_stripped = line.rstrip()
                if logger:
                    logger.debug("[%s] %s", prefix, line_stripped)
                
                # Проверка фильтра для консоли
                if output_to_console:
                    if console_filter is None or console_filter in line_stripped:
                        print(f"[{prefix}] {line_stripped}", flush=True)
    except Exception as e:
        if logger:
            logger.debug("[%s] Ошибка чтения вывода: %s", prefix, e)


class UnbufferedFileHandler(logging.FileHandler):
    """FileHandler с принудительным flush после каждой записи."""
    def emit(self, record):
        super().emit(record)
        self.flush()


def setup_logging(workdir):
    """Настраивает логирование в файл и консоль."""
    log_file = workdir / "proxy_launcher.log"
    
    # Создаём logger
    logger = logging.getLogger("Launcher")
    logger.setLevel(logging.DEBUG)
    
    # Очищаем старые handlers (если были)
    logger.handlers.clear()
    
    # Формат: [YYYY-MM-DD HH:MM:SS] [источник] сообщение
    formatter = logging.Formatter(
        fmt="[{asctime}] [{name}] {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # FileHandler - append mode, без буферизации
    file_handler = UnbufferedFileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # StreamHandler - консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def main():
    args = parse_args()
    
    # Определяем рабочую директорию
    workdir = Path(__file__).parent.resolve()
    os.chdir(workdir)
    
    # Настраиваем логирование
    logger = setup_logging(workdir)
    logger.info("Рабочая директория: %s", workdir)
    logger.info("Proxy приложение: %s", args.proxy_app)
    
    # Определяем пути к venv
    proxy_venv = workdir / ".venv"
    
    # Проверяем существование venv
    if not proxy_venv.exists():
        logger.error("Proxy venv не найден: %s", proxy_venv)
        sys.exit(1)
    
        logger.info("Proxy venv: %s", proxy_venv)
    
    # Определяем путь к dashboard venv
    dashboard_venv = workdir / ".venv"
    logger.info("Dashboard venv: %s", dashboard_venv)
    
    # Формируем команды для uvicorn с полными путями
    proxy_uvicorn = proxy_venv / "bin" / "uvicorn"
    dashboard_uvicorn = dashboard_venv / "bin" / "uvicorn"
    
    proxy_cmd = [
        str(proxy_uvicorn),
        args.proxy_app,
        "--host", "0.0.0.0",
        "--port", str(args.proxy_port),
    ]
    if args.reload:
        proxy_cmd.append("--reload")
    
    # Передать флаг debug в окружение для test_proxy.py
    proxy_env = os.environ.copy()
    if args.debug:
        proxy_env["PROXY_DEBUG"] = "1"
    
    # Создаём процессы
    proxy_process = create_process("proxy", proxy_cmd, env=proxy_env, logger=logger)
    
    # Создаём процесс dashboard если запрошено
    dashboard_process = None
    dashboard_thread = None
    if args.dashboard:
        dashboard_cmd = [
            str(dashboard_uvicorn),
            "dashboard:app",
            "--host", "localhost",
            "--port", str(args.dashboard_port),
        ]
        if args.reload:
            dashboard_cmd.append("--reload")
        
        dashboard_process = create_process(
            "dashboard",
            dashboard_cmd,
            env=os.environ.copy(),
            logger=logger
        )
    
    logger.info("Процессы запущены:")
    logger.info("  - proxy: PID %s на порту %s", proxy_process.pid, args.proxy_port)
    if dashboard_process:
        logger.info("  - dashboard: PID %s на порту %s", dashboard_process.pid, args.dashboard_port)
    logger.info("Нажмите Ctrl+C для остановки")
    
    # Запускаем потоки для чтения вывода каждого процесса
    # Потоки daemon=True закроются автоматически при завершении программы
    # proxy: output_to_console=False — логи только в файл (кроме [retry])
    proxy_thread = threading.Thread(
        target=stream_output,
        args=(proxy_process, "proxy", logger, True),  # Только в файл
        daemon=True,
        name="proxy-output"
    )
    
    
    proxy_thread.start()
    
    if dashboard_process:
        dashboard_thread = threading.Thread(
            target=stream_output,
            args=(dashboard_process, "dashboard", logger, False),  # Только в файл
            daemon=True,
            name="dashboard-output"
        )
        dashboard_thread.start()
    
    # Основной цикл: только ждёт завершения процессов
    try:
        while True:
            # Проверяем, живы ли процессы
            proxy_alive = proxy_process.poll() is None
            dashboard_alive = dashboard_process is None or dashboard_process.poll() is None
            
            if not proxy_alive and not dashboard_alive:
                logger.info("Все процессы завершились")
                break
            
            # Небольшая пауза чтобы не грузить CPU
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        # Выходим сразу, НЕ завершая процессы
        print("\n🛑 proxy_launcher завершён (процессы остались работать)")
        os._exit(0)
    
    finally:
        # Потоки закроются автоматически (daemon=True)
        proxy_thread.join(timeout=0.1)
        if dashboard_thread:
            dashboard_thread.join(timeout=0.1)


if __name__ == "__main__":
    main()
````

## File: setup.sh
````bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Проверка uv ==="
if ! command -v uv &>/dev/null; then
    echo "ОШИБКА: uv не найден. Установите: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "uv: $(uv --version)"

echo ""
echo "=== Проект 1: test_revers_proxy ==="
cd "$SCRIPT_DIR"
if [ ! -d ".venv" ]; then
    echo "Создаю venv..."
    uv venv .venv
    echo "Устанавливаю зависимости из requirements-deps.txt..."
    uv pip install --python .venv/bin/python -r requirements-deps.txt
    echo "Готово."
else
    echo "test_revers_proxy venv is ready."
fi


cd "$SCRIPT_DIR/opencode_compat_proxy"
echo ""
echo "=== Проект 2: opencode_compat_proxy ==="
if [ ! -d ".venv" ]; then
    echo "Создаю venv..."
    uv venv .venv
    echo "Устанавливаю зависимости из opencode_compat_proxy/requirements-deps.txt..."
    uv pip install --python .venv/bin/python -r requirements.txt
    echo "Готово."
else
    echo "test_revers_proxy/opencode_compat_proxy venv is ready."
fi

echo ""
echo "=== Все зависимости установлены ==="
````

## File: test_response.py
````python
import requests as rq
import json
# from accaunts import ACCOUNTS
# from utils import curl_to_python

def dd(data):
    print(json.dumps(data, ensure_ascii=False, indent=4))

# print('-- port 9625 --')
# data = rq.post('http://localhost:9625/v1/chat/completions', headers={
#     'Content-Type': 'application/json'
# }, json={
#   "model": "free-qwen3.5-plus",
#   "messages": [
#     {"role": "user", "content": "Привет"}
#   ],
#   "stream": False
# })
# print(data)
# if data.status_code == 200:
#     print(json.loads(data.content))
# else:
print('-- port 5000 --')
data = rq.post('http://localhost:5000/v1/chat/completions', headers = {
    'Content-Type': 'application/json',
}, json={
  "model": "free-qwen3.5-plus",
  "messages": [
    {"role": "user", "content": "Привет"}
  ],
  "stream": True
})
print(data)
dd(data.content.decode())
````

## File: accaunts.py
````python
# Чтобы добавить аккаунт — просто скопируй curl-команду сюда:


ACCOUNTS = [
    """
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; mdd=0; session=MTc5Mjk0MTEyNnxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVlBQkhKdmJHVURhVzUwQkFJQUFnWnpkSEpwYm1jTUNBQUdjM1JoZEhWekEybHVkQVFDQUFJR2MzUnlhVzVuREFjQUJXZHliM1Z3Qm5OMGNtbHVad3dKQUFka1pXWmhkV3gwQm5OMGNtbHVad3dFQUFKcFpBTnBiblFFQkFELU5EWUdjM1J5YVc1bkRBb0FDSFZ6WlhKdVlXMWxCbk4wY21sdVp3d1VBQkoxWDJFeU5UaG1ObVkzTmpZNU1UTTNZV009fOce4Hw6auW-YpaPk5UNEZEUSLeZGLCzszhgY7H16Szt; OdiRouter-authenticated=1' \
  -H 'new-api-user: 6683' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="155", "Not(A:Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: 61d039a0-f414-4444-b719-28a8178c90b6' \
  -H 'x-starry-window-id: 7bdede60-396d-4b52-9448-b0ccd8a8abd0' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'
""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b '_ym_uid=1790271334319132896; _ym_d=1794312443; _ym_isad=1; mdd=0; session=MTc5NDc4Nzk1OXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQWNBQldkeWIzVndCbk4wY21sdVp3d0pBQWRrWldaaGRXeDBCbk4wY21sdVp3d0VBQUpwWkFOcGJuUUVCQUQtWFVnR2MzUnlhVzVuREFvQUNIVnpaWEp1WVcxbEJuTjBjbWx1Wnd3VUFCSjFYMlkwTWpJNU5EazRaVGt4WWpjNE1EUUdjM1J5YVc1bkRBWUFCSEp2YkdVRGFXNTBCQUlBQWdaemRISnBibWNNQ0FBR2MzUmhkSFZ6QTJsdWRBUUNBQUk9fLJVmk8gUiGPhJS-UBOP-3JmG88FQa3_JDZ5TNb3dzg3; OdiRouter-authenticated=1' \
  -H 'new-api-user: 11940' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="157", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: model_page' \
  -H 'x-starry-ref-page-name: model_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/models' \
  -H 'x-starry-session-id: 9d876b80-bdd2-406f-a278-be52a9ae5842' \
  -H 'x-starry-window-id: 95351ac7-aaa9-4873-a223-1129660e533a' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'
""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b '_ym_uid=1790271334319132896; _ym_d=1794312443; _ym_isad=1; mdd=0; session=MTc5NDc4ODA4OXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA1ZFNnWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmTURCallqQmtNekl5WmpKaU9EaGtPUVp6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fAtPOJ9xl_pPvqfLwTPrV3oQwaybSq3wJiT_xB37wDrT; OdiRouter-authenticated=1' \
  -H 'new-api-user: 11941' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="157", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: model_page' \
  -H 'x-starry-ref-page-name: model_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/models' \
  -H 'x-starry-session-id: 9d876b80-bdd2-406f-a278-be52a9ae5842' \
  -H 'x-starry-window-id: 95351ac7-aaa9-4873-a223-1129660e533a' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-gemini-3-flash-preview","stream":true}'
""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjM2MjM2M3xEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA0ODZnWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmT1RRd1pqTTNOR05rWXpjMlpHUXhZd1p6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fM5aiWQtr8DMHGKqiUxLyhp62h-k6zHUXPnf8tLnLT5C; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7797' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="155", "Not(A:Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: df0302cb-055c-446b-aac4-28d41d2cb21c' \
  -H 'x-starry-window-id: e5b6d639-99da-431a-984a-1fa6a1fb679f' \
  --data-raw '{"group":"default","messages":[{"content":"hi","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjA4NTg2MXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQWdBQm5OMFlYUjFjd05wYm5RRUFnQUNCbk4wY21sdVp3d0hBQVZuY205MWNBWnpkSEpwYm1jTUNRQUhaR1ZtWVhWc2RBWnpkSEpwYm1jTUJBQUNhV1FEYVc1MEJBUUFfajBJQm5OMGNtbHVad3dLQUFoMWMyVnlibUZ0WlFaemRISnBibWNNRkFBU2RWOHlZams1TnpJMU1tWTBaakl6TWpWaUJuTjBjbWx1Wnd3R0FBUnliMnhsQTJsdWRBUUNBQUk9fGdz4yeBstyAwTGK5setrOnP__QvEv5DBjIGVi434Psj; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7812' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="153", "Not_A Brand";v="8"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: c1b131d1-d249-490a-aae6-904c95db4cf6' \
  -H 'x-starry-window-id: 8518f21c-9a81-4aa8-8884-57afc9f1a6f8' \
  --data-raw '{"group":"default","messages":[{"content":"привет?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b '_ym_uid=1790271334319132896; _ym_d=1794312443; _ym_isad=1; mdd=0; session=MTc5NDc4NzY3NHxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQW9BQ0hWelpYSnVZVzFsQm5OMGNtbHVad3dVQUJKMVgyRmxaVGs1T1RVNFl6Vm1PRGRoTVRJR2MzUnlhVzVuREFZQUJISnZiR1VEYVc1MEJBSUFBZ1p6ZEhKcGJtY01DQUFHYzNSaGRIVnpBMmx1ZEFRQ0FBSUdjM1J5YVc1bkRBY0FCV2R5YjNWd0JuTjBjbWx1Wnd3SkFBZGtaV1poZFd4MEJuTjBjbWx1Wnd3RUFBSnBaQU5wYm5RRUJBRC1QUW89fAoPaLmJ3LI4u4S9TDXF5huhCrKG_bJ6RJcP4WHIAEoZ; OdiRouter-authenticated=1' \
  -H 'new-api-user: 7813' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="157", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: 9d876b80-bdd2-406f-a278-be52a9ae5842' \
  -H 'x-starry-window-id: 95351ac7-aaa9-4873-a223-1129660e533a' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjA4NjMxM3xEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA1RW5nWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmTmpaaE1qUTRNelUwTUdWbFpERXhOUVp6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fN40iLuTu-JBQsxhbFlvwG2ED4BAubg6RpdYErRL0pzr; OdiRouter-authenticated=1' \
  -H 'new-api-user: 8783' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="153", "Not_A Brand";v="8"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: c1b131d1-d249-490a-aae6-904c95db4cf6' \
  -H 'x-starry-window-id: 8518f21c-9a81-4aa8-8884-57afc9f1a6f8' \
  --data-raw '{"group":"default","messages":[{"content":"привет?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'tmr_lvid=17da0594be27b1c4b50aa898c80442c7; tmr_lvidTS=1790271333127; _ym_uid=1790271334319132896; _ym_d=1790271334; _ym_isad=1; session=MTc5MjA4NjIxOXxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQW9BQ0hWelpYSnVZVzFsQm5OMGNtbHVad3dVQUJKMVh6QTNZV1l6TURVelpqUmtZV0kyTldJR2MzUnlhVzVuREFZQUJISnZiR1VEYVc1MEJBSUFBZ1p6ZEhKcGJtY01DQUFHYzNSaGRIVnpBMmx1ZEFRQ0FBSUdjM1J5YVc1bkRBY0FCV2R5YjNWd0JuTjBjbWx1Wnd3SkFBZGtaV1poZFd4MEJuTjBjbWx1Wnd3RUFBSnBaQU5wYm5RRUJBRC1SS0k9fASK4NXsyZEiC4Hkulq8LTIfAmCl1upZvEWXXB81KqqL; OdiRouter-authenticated=1' \
  -H 'new-api-user: 8785' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="153", "Not_A Brand";v="8"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: c1b131d1-d249-490a-aae6-904c95db4cf6' \
  -H 'x-starry-window-id: 8518f21c-9a81-4aa8-8884-57afc9f1a6f8' \
  --data-raw '{"group":"default","messages":[{"content":"привет?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b '_ym_uid=1790271334319132896; _ym_d=1794312443; _ym_isad=1; mdd=0; session=MTc5NDc4NzU4NHxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA1WmxBWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRCUUFFblZmWm1FM05UVTNObVUxWlRabE1qY3hZUVp6ZEhKcGJtY01CZ0FFY205c1pRTnBiblFFQWdBQ0JuTjBjbWx1Wnd3SUFBWnpkR0YwZFhNRGFXNTBCQUlBQWdaemRISnBibWNNQndBRlozSnZkWEFHYzNSeWFXNW5EQWtBQjJSbFptRjFiSFE9fCSlPZ3yXtaUJCCeLW74JwzUYOfXjgzhhaXVQlZ_HJfL; OdiRouter-authenticated=1' \
  -H 'new-api-user: 11466' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="157", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: 9d876b80-bdd2-406f-a278-be52a9ae5842' \
  -H 'x-starry-window-id: 95351ac7-aaa9-4873-a223-1129660e533a' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
"""
curl --url 'https://odirouter.ai/api/relay/pg/chat/completions' \
  -H 'accept: text/event-stream' \
  -H 'accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b '_ym_uid=1790271334319132896; _ym_d=1794312443; _ym_isad=1; mdd=0; session=MTc5NDc4NzQ1NHxEWDhFQVFMX2dBQUJFQUVRQUFEX25mLUFBQVVHYzNSeWFXNW5EQWdBQm5OMFlYUjFjd05wYm5RRUFnQUNCbk4wY21sdVp3d0hBQVZuY205MWNBWnpkSEpwYm1jTUNRQUhaR1ZtWVhWc2RBWnpkSEpwYm1jTUJBQUNhV1FEYVc1MEJBUUFfbG1XQm5OMGNtbHVad3dLQUFoMWMyVnlibUZ0WlFaemRISnBibWNNRkFBU2RWODNZVFkwTW1Jek4yUmtOVGszWmpka0JuTjBjbWx1Wnd3R0FBUnliMnhsQTJsdWRBUUNBQUk9fONAgBPBs_y_PsfXG1JZxJD1NQLPbkYDyc95vK8-dsqR; OdiRouter-authenticated=1' \
  -H 'new-api-user: 11467' \
  -H 'origin: https://odirouter.ai' \
  -H 'priority: u=1, i' \
  -H 'referer: https://odirouter.ai/dashboard/playground' \
  -H 'sec-ch-ua: "Chromium";v="157", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36' \
  -H 'x-starry-current-page-id: playground_page' \
  -H 'x-starry-current-page-name: playground_page' \
  -H 'x-starry-current-page-url: https://odirouter.ai/dashboard/playground' \
  -H 'x-starry-distinct-id: 1d95acc2-594f-417d-8f6c-0fbbd8078b7e' \
  -H 'x-starry-ref-page-id: home_page' \
  -H 'x-starry-ref-page-name: home_page' \
  -H 'x-starry-ref-page-url: https://odirouter.ai/dashboard/home' \
  -H 'x-starry-session-id: 9d876b80-bdd2-406f-a278-be52a9ae5842' \
  -H 'x-starry-window-id: 95351ac7-aaa9-4873-a223-1129660e533a' \
  --data-raw '{"group":"default","messages":[{"content":"hello?","role":"user"}],"model":"free-qwen3.5-plus","stream":true}'""",
]
````

## File: test_proxy.py
````python
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
    choices = final_response.get('choices') or []
    if not choices:
        return False
    message = choices[0].get('message', '')
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

def stream_generator(line_iter, first_line, resp, account_id, model, input_tokens, current_account_id):
    """
    Прямая потоковая отдача SSE без накопления в память.

    Первый чанк (first_line) уже был peek'нут в handler'е — отдаём его первым.
    Каждый чанк проверяется на JSON с "заблокирован":
      - если бан найден mid-stream (headers уже отправлены, аккаунт не переключить)
        → отдаём SSE-ошибку и завершаем поток.
    """
    output_tokens = 0
    try:
        # 1. Отдать peek'нутый первый чанк
        if first_line is not None:
            line_str = first_line.decode() if isinstance(first_line, bytes) else first_line
            if line_str.strip():
                if line_str.strip() == 'data: [DONE]':
                    yield f'data: {json.dumps({"done": True})}\n\n'
                    return
                if line_str.startswith('data: '):
                    line_str = strip_think_from_sse_line(line_str)
                yield line_str + '\n\n'

        # 2. Стримить остаток напрямую (без list/append)
        for line in line_iter:
            if not line:
                continue

            line_str = line.decode() if isinstance(line, bytes) else line

            # Non-SSE JSON — проверка на бан
            if not line_str.startswith('data:') and line_str.strip():
                try:
                    json_data = json.loads(line_str)
                    msg = json_data.get('message', '')
                    if isinstance(msg, str) and 'заблокирован' in msg:
                        print(f"[banned] Бан в mid-stream (JSON): {msg}")
                        yield f'data: {json.dumps({"error": "Account is banned"}, ensure_ascii=False)}\n\n'
                        yield 'data: [DONE]\n\n'
                        return
                except json.JSONDecodeError:
                    pass

            if line_str.strip() == 'data: [DONE]':
                yield f'data: {json.dumps({"done": True})}\n\n'
                return

            # SSE чанк — фильтр think-тегов + проверка на бан в content + usage
            if line_str.startswith('data: '):
                line_str = strip_think_from_sse_line(line_str)
                try:
                    payload_str = line_str[6:]
                    if payload_str.strip() != '[DONE]':
                        data = json.loads(payload_str)

                        # Проверка бана в message.content
                        for choice in data.get('choices', []):
                            msg = choice.get('message', {})
                            content = msg.get('content')
                            if isinstance(content, str) and 'заблокирован' in content:
                                print(f"[banned] Бан в SSE чанке: {content}")
                                yield f'data: {json.dumps({"error": "Account is banned"}, ensure_ascii=False)}\n\n'
                                yield 'data: [DONE]\n\n'
                                return

                        # Попытка достать usage (если upstream прислал)
                        usage = data.get('usage') or {}
                        if usage:
                            output_tokens = (
                                usage.get('completion_tokens')
                                or usage.get('output_tokens')
                                or output_tokens
                            )
                except (json.JSONDecodeError, ValueError):
                    pass

            yield line_str + '\n\n'
    finally:
        # Закрыть upstream-соединение
        try:
            resp.close()
        except Exception:
            pass
        # Записать статистику
        if STATS_ENABLED:
            threading.Thread(
                target=record_request,
                args=(account_id, 200, model, input_tokens, output_tokens),
                daemon=True,
            ).start()

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
                try:
                    json_ = json.loads(resp.content.decode())
                except (json.JSONDecodeError, ValueError):
                    print(f"[proxy] Не-JSON тело upstream ({resp.status_code})")
                    return Response(content=resp.content, status_code=resp.status_code)
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
        # --- Stream handling with retry loop for ban detection ---
        # Не накапливаем чанки в память. Делаем только peek первого чанка,
        # чтобы отловить бан-JSON (upstream при бане отдаёт HTTP 200 + обычный
        # JSON {"message": "Пользователь заблокирован", ...} даже при stream=true).
        max_attempts = len(ACCOUNTS)

        for attempt in range(max_attempts):
            if attempt > 0:
                print(f"[retry] Stream retry #{attempt}/{max_attempts} после бана")
                try:
                    resp.close()
                except Exception:
                    pass
                resp = session.post(TARGET_URL, json=payload, stream=True, timeout=180)

                if resp.status_code != 200:
                    print(f"[retry] Аккаунт {current_account_id} вернул {resp.status_code}, пробуем следующий")
                    switch_account()
                    account_id = get_current_account_id()
                    current_account_id = 'account_' + ACCOUNT_IDS[current_acc_index]
                    continue

            # --- Peek первого чанка: ловим бан-JSON ---
            line_iter = resp.iter_lines(decode_unicode=False)
            first_line = next(line_iter, None)
            ban_found = False

            if first_line:
                first_str = first_line.decode() if isinstance(first_line, bytes) else first_line
                if not first_str.startswith('data:') and first_str.strip():
                    try:
                        json_data = json.loads(first_str)
                        msg = json_data.get('message', '')
                        if isinstance(msg, str) and 'заблокирован' in msg:
                            print(f"[banned] Запрещённый ответ от upstream (JSON): {msg}")
                            ban_found = True
                    except json.JSONDecodeError:
                        pass

            if ban_found:
                try:
                    resp.close()
                except Exception:
                    pass

                if is_test_request:
                    print(f"[retry] Бан детектирован (тестовый режим), аккаунт не переключается")
                    err_body = (
                        'data: ' + json.dumps({"error": "Account is banned"}, ensure_ascii=False) + '\n\n'
                        + 'data: [DONE]\n\n'
                    )
                    return Response(
                        content=err_body,
                        status_code=403,
                        media_type='text/event-stream',
                    )

                print(f"[retry] Бан детектирован. Переключаем аккаунт...")
                switch_account()
                account_id = get_current_account_id()
                current_account_id = 'account_' + ACCOUNT_IDS[current_acc_index]
                continue

            # --- Бана нет: стримим напрямую, без накопления ---
            return StreamingResponse(
                stream_generator(
                    line_iter=line_iter,
                    first_line=first_line,
                    resp=resp,
                    account_id=account_id,
                    model=model,
                    input_tokens=input_tokens,
                    current_account_id=current_account_id,
                ),
                status_code=resp.status_code,
                media_type='text/event-stream',
            )

        # Все попытки исчерпаны
        print("[retry] Все аккаунты исчерпаны после банов")
        err_body = (
            'data: ' + json.dumps({"error": "All accounts are banned"}, ensure_ascii=False) + '\n\n'
            + 'data: [DONE]\n\n'
        )
        return Response(
            content=err_body,
            status_code=403,
            media_type='text/event-stream',
        )


def _iter_lines(lines):
    """Helper: превратить список строк в генератор строк."""
    for line in lines:
        yield line

        def stream_generator_with_usage(resp_obj, usage_dict):
            """Прямая потоковая отдача без накопления, с параметрами."""
            for line in resp_obj.iter_lines(decode_unicode=False): # type: ignore
                if line:
                    line = line.decode()
                    
                    # Проверка на JSON с баном (если не SSE формат)
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
                        yield f'data: {json.dumps({"done": True})}\n\n'
                        break
                    
                    # Прямая отдача чанка без накопления
                    if line.startswith('data: '):
                        # Фильтрация <think> тегов
                        line = strip_think_from_sse_line(line)
                        # Парсинг для проверки бана в текущем чанке
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

        # Общий цикл обработки stream-ответов с retry на случай бана
        max_attempts = len(ACCOUNTS)
        
        for attempt in range(max_attempts):
            # Первый запрос уже выполнен (resp), далее — retry
            if attempt > 0:
                print(f"[retry] Retry #{attempt}/{max_attempts} после бана")
                resp = session.post(TARGET_URL, json=payload, stream=payload.get('stream', True), timeout=180)
                
                if resp.status_code not in [200]:
                    print(f"[retry] Аккаунт {current_account_id} вернул {resp.status_code}, пробуем следующий")
                    switch_account()
                    current_account_id = 'account_' + ACCOUNT_IDS[current_acc_index]
                    continue
            
            usage_data_attempt = {'input_tokens': input_tokens, 'output_tokens': 0}
            
            # Явно собираем чанки и ловим BanDetectedException
            ban_detected = False
            ban_exception = None
            collected_chunks = []
            
            try:
                for line in resp.iter_lines(decode_unicode=False): # type: ignore
                    if line:
                        line = line.decode()
                        
                        # Проверка на JSON с баном (если не SSE формат)
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
                            collected_chunks.append(f'data: {json.dumps({"done": True})}\n\n')
                            break
                        
                        # Прямая отдача чанка без накопления
                        if line.startswith('data: '):
                            # Фильтрация <think> тегов
                            line_filtered = strip_think_from_sse_line(line)
                            # Парсинг для проверки бана в текущем чанке
                            try:
                                payload_str = line_filtered[6:]  # убираем 'data: '
                                if payload_str.strip() != '[DONE]':
                                    data = json.loads(payload_str)
                                    
                                    # Проверка бана в КАЖДОМ choice текущего чанка
                                    for choice in data.get('choices', []):
                                        msg = choice.get('message', {})
                                        content = msg.get('content')
                                        if isinstance(content, str) and 'заблокирован' in content:
                                            print(f"[banned] Найдено 'заблокирован' в SSE чанке: {content}")
                                            raise BanDetectedException(f"Account '{account_id}' is banned in chunk")
                                                    
                            except (json.JSONDecodeError, ValueError):
                                pass
                        
                        collected_chunks.append(line + '\n\n') # type: ignore
                
                # Если дошли сюда — бан не обнаружен, возвращаем StreamingResponse
                if is_test_request:
                    # Для тестовых запросов — возвращаем ошибку сразу при обнаружении бана выше
                    pass
                
                return StreamingResponse(
                    _iter_lines(collected_chunks),
                    status_code=resp.status_code,
                    media_type='text/event-stream'
                )
                
            except BanDetectedException as e:
                ban_detected = True
                ban_exception = e
            
            # Бан детектирован — переключаем аккаунт
            if is_test_request:
                print(f"[retry] Бан детектирован (тестовый режим), аккаунт не переключается: {ban_exception}")
                err_body = (
                    'data: ' + json.dumps({"error": "Account is banned"}, ensure_ascii=False) + '\n\n' + 'data: [DONE]\n\n'
                )
                return Response(
                    content=err_body,
                    status_code=403,
                    media_type='text/event-stream'
                )
            
            # Не тестовый режим — переключаем аккаунт и продолжаем retry
            print(f"[retry] Бан детектирован: {ban_exception}. Переключаем аккаунт...")
            switch_account()
            current_account_id = 'account_' + ACCOUNT_IDS[current_acc_index]
        
        # Все аккаунты исчерпаны
        print("[retry] Все аккаунты исчерпаны после банов")
        err_body = (
            'data: ' + json.dumps({"error": "All accounts are banned", "detail": str(ban_exception)}, ensure_ascii=False) + '\n\n' + 'data: [DONE]\n\n'
        )
        return Response(
            content=err_body,
            status_code=403,
            media_type='text/event-stream'
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
            match = re.search(r'(\{"tool_calls":\s*\[.*\]\})', content, re.DOTALL)
            if match:
                tool_call_json = match.group(1)
                # Заменяем content на этот JSON и добавляем tool_calls в message
                new_message = message.copy()
                new_message['content'] = None  # или убираем
                try:
                    new_message['tool_calls'] = json.loads(tool_call_json)['tool_calls']
                except (json.JSONDecodeError, ValueError):
                    # Неполный захват JSON — возвращаем исходный ответ без преобразования
                    return Response(content=raw_response, status_code=resp.status_code) # type: ignore
                data['choices'][0]['message'] = new_message
                return Response(content=json.dumps(data), status_code=resp.status_code) # type: ignore
        # Если ничего не нашли, возвращаем как есть
        return Response(content=raw_response, status_code=resp.status_code) # type: ignore
````
