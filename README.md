run:
cd /home/kasiro/Документы/python_projects/test_revers_proxy && source .venv/bin/activate.fish
uvicorn test_proxy:app --host localhost --port 5000
cd /home/kasiro/Документы/python_projects/test_revers_proxy/opencode_compat_proxy && source .venv/bin/activate.fish
set -x UPSTREAM_URL "http://127.0.0.1:5000"
uvicorn proxy:app --host 0.0.0.0 --port 9625

scheme:
opencode -> opencode_compat_proxy -> reverse_proxy -> provider -> reverse_proxy -> opencode_compat_proxy -> opencode
