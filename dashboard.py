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

from stats_client import init_db, record_request_async, get_all_stats, init_accounts, get_recent_requests, check_daily_reset
from accaunts import ACCOUNTS
from utils import extract_account_ids_from_accounts


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    ACCOUNT_IDS = extract_account_ids_from_accounts(ACCOUNTS)
    init_accounts(ACCOUNT_IDS)
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
