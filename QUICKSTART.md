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
