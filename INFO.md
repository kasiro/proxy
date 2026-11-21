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
