"""Утилиты для парсинга curl-команд и извлечения account_id."""
import re
import json


def curl_to_python(curl_text: str):
    """Преобразует curl-команду в словарь с url, method, headers, cookies, data."""
    # Убираем обратные слэши и лишние пробелы
    curl_text = re.sub(r'\\\s*\n', ' ', curl_text).strip()
    
    # Извлекаем URL
    url_match = re.search(r"curl\s+(?:--url\s+)?'([^']+)'", curl_text)
    if not url_match:
        url_match = re.search(r'curl\s+(?:--url\s+)"([^"]+)"', curl_text)
    url = url_match.group(1) if url_match else None

    # Извлекаем все -H заголовки (включая значения с кавычками)
    headers = {}
    for match in re.finditer(r"-H\s+'([^:]+):\s*([^']+)'", curl_text):
        key, value = match.group(1).strip(), match.group(2).strip()
        headers[key] = value
    for match in re.finditer(r'-H\s+"([^:]+):\s*([^"]+)"', curl_text):
        key, value = match.group(1).strip(), match.group(2).strip()
        headers[key] = value

    # Извлекаем куки (-b)
    cookies = {}
    cookie_match = re.search(r"-b\s+'([^']+)'", curl_text) or re.search(r'-b\s+"([^"]+)"', curl_text)
    if cookie_match:
        cookie_str = cookie_match.group(1)
        # Можно разобрать как строку cookie (key=value; key2=value2)
        for part in cookie_str.split(';'):
            if '=' in part:
                k, v = part.strip().split('=', 1)
                cookies[k] = v

    # Извлекаем данные --data-raw
    data = None
    data_match = re.search(r"--data-raw\s+'([^']+)'", curl_text) or re.search(r'--data-raw\s+"([^"]+)"', curl_text)
    if data_match:
        raw = data_match.group(1)
        try:
            data = json.loads(raw)   # если JSON
        except:
            data = raw               # если просто строка

    # Метод (по умолчанию GET, но если есть --data – POST)
    method = 'POST' if data else 'GET'
    if re.search(r'-X\s+(\w+)', curl_text):
        method = re.search(r'-X\s+(\w+)', curl_text).group(1)

    return {
        'url': url,
        'method': method,
        'headers': headers,
        'cookies': cookies,
        'data': data,
    }


def extract_account_ids_from_accounts(accounts: list[str]) -> list[str]:
    """
    Извлекает account_id из списка curl-команд ACCOUNTS.
    
    Args:
        accounts: Список curl-команд из accaunts.py
        
    Returns:
        Список account_id (из заголовка new-api-user)
    """
    account_ids = []
    for acc_curl in accounts:
        parsed = curl_to_python(acc_curl)
        account_id = parsed['headers'].get('new-api-user', 'unknown')
        account_ids.append(account_id)
    return account_ids
