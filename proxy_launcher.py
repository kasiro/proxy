#!/usr/bin/env python3
"""
Launcher для запуска трёх uvicorn-процессов: proxy, compat и dashboard.

Запускает:
  - proxy: uvicorn на порту 5000 (test_proxy:app из корня проекта)
  - opencode_compat_proxy: uvicorn на порту 9625 (proxy:app из папки opencode_compat_proxy/)
  - dashboard: uvicorn на порту 5001 (dashboard:app из корня проекта)

Все процессы работают в фоне, основной процесс ждёт их завершения.
При Ctrl+C — лаунчер завершается мгновенно, НЕ убивая proxy-процессы (они остаются работать в фоне).

Использование:
    python proxy_launcher.py                                 # по умолчанию: test_proxy:app + opencode_compat_proxy/proxy:app
    python proxy_launcher.py --proxy-app custom:app          # кастомное proxy приложение
    python proxy_launcher.py --compat-app custom:app         # кастомное compat приложение
    python proxy_launcher.py --compat-cwd /path/to/dir       # кастомная директория для compat
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
        description="Запуск двух uvicorn-процессов reverse proxy"
    )
    parser.add_argument(
        "--proxy-app",
        type=str,
        default="test_proxy:app",
        help="Uvicorn приложение для proxy в формате module:app (по умолчанию: test_proxy:app)"
    )
    parser.add_argument(
        "--compat-app",
        type=str,
        default="proxy:app",
        help="Uvicorn приложение для compat proxy в формате module:app (по умолчанию: proxy:app)"
    )
    parser.add_argument(
        "--compat-cwd",
        type=str,
        default="opencode_compat_proxy",
        help="Рабочая директория для compat proxy (по умолчанию: opencode_compat_proxy)"
    )
    parser.add_argument(
        "--proxy-port",
        type=int,
        default=5000,
        help="Порт для proxy (по умолчанию: 5000)"
    )
    parser.add_argument(
        "--compat-port",
        type=int,
        default=9625,
        help="Порт для opencode_compat_proxy (по умолчанию: 9625)"
    )
    parser.add_argument(
        "--upstream-url",
        type=str,
        default=None,
        help="UPSTREAM_URL для compat proxy (по умолчанию: http://127.0.0.1:<proxy-port>)"
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
    logger.info("Compat приложение: %s (из %s)", args.compat_app, args.compat_cwd)
    
    # Определяем пути к venv
    proxy_venv = workdir / ".venv"
    compat_venv = workdir / args.compat_cwd / ".venv"
    
    # Проверяем существование venv
    if not proxy_venv.exists():
        logger.error("Proxy venv не найден: %s", proxy_venv)
        sys.exit(1)
    
    if not compat_venv.exists():
        logger.error("Compat venv не найден: %s", compat_venv)
        sys.exit(1)
    
    logger.info("Proxy venv: %s", proxy_venv)
    logger.info("Compat venv: %s", compat_venv)
    
    # Определяем путь к dashboard venv
    dashboard_venv = workdir / ".venv"
    logger.info("Dashboard venv: %s", dashboard_venv)
    
    # Формируем команды для uvicorn с полными путями
    proxy_uvicorn = proxy_venv / "bin" / "uvicorn"
    compat_uvicorn = compat_venv / "bin" / "uvicorn"
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
    
    upstream_url = args.upstream_url or f"http://127.0.0.1:{args.proxy_port}"
    compat_env = os.environ.copy()
    compat_env["UPSTREAM_URL"] = upstream_url
    
    compat_cmd = [
        str(compat_uvicorn),
        args.compat_app,
        "--host", "0.0.0.0",
        "--port", str(args.compat_port),
    ]
    if args.reload:
        compat_cmd.append("--reload")
    
    # Меняем рабочую директорию для compat proxy
    compat_cwd = workdir / args.compat_cwd
    logger.info("Compat рабочая директория: %s", compat_cwd)
    
    # Создаём процессы
    proxy_process = create_process("proxy", proxy_cmd, env=proxy_env, logger=logger)
    compat_process = create_process("compat", compat_cmd, env=compat_env, cwd=compat_cwd, logger=logger)
    
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
    logger.info("  - compat: PID %s на порту %s (UPSTREAM_URL=%s)", compat_process.pid, args.compat_port, upstream_url)
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
    compat_thread = threading.Thread(
        target=stream_output,
        args=(compat_process, "compat", logger, True),  # Выводить на консоль
        daemon=True,
        name="compat-output"
    )
    
    proxy_thread.start()
    compat_thread.start()
    
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
            compat_alive = compat_process.poll() is None
            dashboard_alive = dashboard_process is None or dashboard_process.poll() is None
            
            if not proxy_alive and not compat_alive and not dashboard_alive:
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
        compat_thread.join(timeout=0.1)
        if dashboard_thread:
            dashboard_thread.join(timeout=0.1)


if __name__ == "__main__":
    main()
