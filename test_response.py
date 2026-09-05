import requests as rq
import json

data = rq.post('http://localhost:9625/v1/chat/completions', headers={
    'Content-Type': 'application/json'
}, json={
  "model": "free-minimax-m2.7",
  "messages": [
    {"role": "user", "content": "Привет"}
  ],
  "stream": False
})
print(json.loads(data.content))
