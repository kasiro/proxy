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
