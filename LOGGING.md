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
