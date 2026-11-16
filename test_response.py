import requests as rq
import json
# from accaunts import ACCOUNTS
# from utils import curl_to_python

def dd(data):
    print(json.dumps(data, ensure_ascii=False, indent=4))

# print('-- port 9625 --')
# data = rq.post('http://localhost:9625/v1/chat/completions', headers={
#     'Content-Type': 'application/json'
# }, json={
#   "model": "free-qwen3.5-plus",
#   "messages": [
#     {"role": "user", "content": "Привет"}
#   ],
#   "stream": False
# })
# print(data)
# if data.status_code == 200:
#     print(json.loads(data.content))
# else:
print('-- port 5000 --')
data = rq.post('http://localhost:5000/v1/chat/completions', headers = {
    'Content-Type': 'application/json'
}, json={
  "model": "free-qwen3.5-plus",
  "messages": [
    {"role": "user", "content": "Привет"}
  ],
  "stream": False
})
print(data)
dd(data.content.decode())
