#!/usr/bin/env python3
"""
Launcher для запуска двух uvicorn-процессов reverse proxy.

Запускает:
  - proxy: uvicorn на порту 5000 (test_proxy:app из корня проекта)
  - opencode_compat_proxy: uvicorn на порту 9625 (proxy:app из папки opencode_compat_proxy/)

Оба процесса работают в фоне, основной процесс ждёт их завершения.
При Ctrl+C — корректно завершает оба процесса.

Использование:
    python proxy_launcher.py                                 # по умолчанию: test_proxy:app + opencode_compat_proxy/proxy:app
    python proxy_launcher.py --proxy-app custom:app          # кастомное proxy приложение
    python proxy_launcher.py --compat-app custom:app         # кастомное compat приложение
    python proxy_launcher.py --compat-cwd /path/to/dir       # кастомная директория для compat
"""

import argparse
import logging
import os
import signal
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


def stream_output(process, prefix, logger):
    """
    Поток для чтения вывода процесса.
    Читает пока процесс жив или пока есть данные в буфере.
    Пишет в лог и консоль без блокировки основного цикла.
    """
    try:
        for line in process.stdout:
            if line:
                line_stripped = line.rstrip()
                if logger:
                    logger.debug("[%s] %s", prefix, line_stripped)
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
    
    # Формируем команды для uvicorn с полными путями
    proxy_uvicorn = proxy_venv / "bin" / "uvicorn"
    compat_uvicorn = compat_venv / "bin" / "uvicorn"
    
    proxy_cmd = [
        str(proxy_uvicorn),
        args.proxy_app,
        "--host", "0.0.0.0",
        "--port", str(args.proxy_port),
    ]
    if args.reload:
        proxy_cmd.append("--reload")
    
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
    proxy_process = create_process("proxy", proxy_cmd, logger=logger)
    compat_process = create_process("compat", compat_cmd, env=compat_env, cwd=compat_cwd, logger=logger)
    
    logger.info("Оба процесса запущены:")
    logger.info("  - proxy: PID %s на порту %s", proxy_process.pid, args.proxy_port)
    logger.info("  - compat: PID %s на порту %s (UPSTREAM_URL=%s)", compat_process.pid, args.compat_port, upstream_url)
    logger.info("Нажмите Ctrl+C для остановки")
    
    # Запускаем потоки для чтения вывода каждого процесса
    # Потоки daemon=True закроются автоматически при завершении программы
    proxy_thread = threading.Thread(
        target=stream_output,
        args=(proxy_process, "proxy", logger),
        daemon=True,
        name="proxy-output"
    )
    compat_thread = threading.Thread(
        target=stream_output,
        args=(compat_process, "compat", logger),
        daemon=True,
        name="compat-output"
    )
    
    proxy_thread.start()
    compat_thread.start()
    
    # Обработчик сигналов для корректного завершения
    shutdown_requested = False
    
    def signal_handler(signum, frame):
        nonlocal shutdown_requested
        if shutdown_requested:
            logger.critical("Принудительное завершение...")
            proxy_process.kill()
            compat_process.kill()
            sys.exit(1)
        shutdown_requested = True
        logger.warning("Получен сигнал остановки, завершаем процессы...")
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Основной цикл: только ждёт завершения процессов
    try:
        while True:
            # Проверяем, живы ли процессы
            proxy_alive = proxy_process.poll() is None
            compat_alive = compat_process.poll() is None
            
            if not proxy_alive and not compat_alive:
                logger.info("Оба процесса завершились")
                break
            
            # Небольшая пауза чтобы не грузить CPU
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        # Обработано в signal_handler
        pass
    
    finally:
        # Завершаем процессы если ещё живы
        logger.info("Завершение процессов...")
        
        for proc, name in [(proxy_process, "proxy"), (compat_process, "compat")]:
            if proc.poll() is None:
                proc.terminate()
                logger.info("[%s] Отправлен SIGTERM", name)
        
        # Ждём завершения
        for proc, name in [(proxy_process, "proxy"), (compat_process, "compat")]:
            try:
                proc.wait(timeout=5)
                logger.info("[%s] Завершён с кодом %s", name, proc.returncode)
            except subprocess.TimeoutExpired:
                proc.kill()
                logger.warning("[%s] Убит (не ответил на SIGTERM)", name)
        
        # Потоки закроются автоматически (daemon=True)
        proxy_thread.join(timeout=1)
        compat_thread.join(timeout=1)
        
        logger.info("Готово")


if __name__ == "__main__":
    main()
