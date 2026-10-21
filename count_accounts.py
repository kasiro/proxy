from utils import curl_to_python
from accaunts import ACCOUNTS
import json

def dump(data) -> str:
    return json.dumps(
        data,
        ensure_ascii=False,
        indent=4
    )

len_ = len(ACCOUNTS)

count = 0
for i in range(len_):
    d = curl_to_python(ACCOUNTS[i])
    id_ = d['headers']['new-api-user']
    new = True if 'tmr_lvid' in d['cookies'].keys() else False
    print(id_, ':', 'account is updated...' if new else 'not updated')
    if new:
        count += 1

proc = count * 100 / len_
print('updated count:', f'{count}/{len_}', f'{round(proc, 2)}%')
