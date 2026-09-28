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
fi
echo "Устанавливаю зависимости из requirements-deps.txt..."
uv pip install --python .venv/bin/python -r requirements-deps.txt
echo "Готово."

cd "$SCRIPT_DIR/opencode_compat_proxy"
echo ""
echo "=== Проект 2: opencode_compat_proxy ==="
if [ ! -d "opencode_compat_proxy/.venv" ]; then
    echo "Создаю venv..."
    uv venv .venv
fi

uv pip install --python .venv/bin/python -r requirements.txt
echo "Готово."

echo ""
echo "=== Все зависимости установлены ==="
