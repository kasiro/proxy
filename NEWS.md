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
