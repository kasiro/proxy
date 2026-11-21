"""Тесты утилит utils.py (парсинг curl и извлечение account_id)."""
import utils

CURL_SINGLE = """
curl --url 'https://api.example.com/v1/chat' \\
  -H 'accept: application/json' \\
  -H 'content-type: application/json' \\
  -H 'new-api-user: 12345' \\
  -b 'session=abc; other=def' \\
  --data-raw '{"model": "m", "stream": false}'
"""

CURL_DOUBLE = 'curl --url "https://api.example.com/v1/models" -H "content-type: application/json" -b "a=1; b=2"'

CURL_DOUBLE_NO_URL_FLAG = 'curl "https://api.example.com/v1/models" -H "accept: */*"'

CURL_NO_DATA = "curl 'https://api.example.com/ping' -H 'accept: */*'"

CURL_BAD_JSON = "curl 'https://api.example.com/x' --data-raw 'not a json'"

CURL_NO_URL = "curl -H 'accept: */*'"

CURL_MULTI_HEADERS = (
    "curl 'https://api.example.com/x' "
    "-H 'x-time: 12:34:56' "
    "-H 'accept: application/json' "
    "-H 'authorization: Bearer a:b:c'"
)

CURL_MULTI_HEADERS_DOUBLE = (
    'curl "https://api.example.com/x" '
    '-H "x-time: 12:34:56" '
    '-H "accept: application/json"'
)


def test_curl_to_python_single_quotes():
    """Однокавычная curl-команда разбирается на url, headers, cookies, data."""
    parsed = utils.curl_to_python(CURL_SINGLE)
    assert parsed["url"] == "https://api.example.com/v1/chat"
    assert parsed["headers"]["new-api-user"] == "12345"
    assert parsed["headers"]["content-type"] == "application/json"
    assert parsed["cookies"] == {"session": "abc", "other": "def"}
    assert parsed["data"] == {"model": "m", "stream": False}
    assert parsed["method"] == "POST"


def test_curl_to_python_double_quotes():
    """Двойные кавычки в curl-команде тоже поддерживаются."""
    parsed = utils.curl_to_python(CURL_DOUBLE)
    assert parsed["url"] == "https://api.example.com/v1/models"
    assert parsed["headers"]["content-type"] == "application/json"
    assert parsed["cookies"] == {"a": "1", "b": "2"}


def test_curl_to_python_double_quotes_requires_url_flag():
    """Баг: URL в двойных кавычках без --url не извлекается (url=None)."""
    parsed = utils.curl_to_python(CURL_DOUBLE_NO_URL_FLAG)
    assert parsed["url"] is None


def test_curl_to_python_without_data_is_get():
    """Без --data-raw метод по умолчанию GET."""
    parsed = utils.curl_to_python(CURL_NO_DATA)
    assert parsed["method"] == "GET"
    assert parsed["data"] is None


def test_curl_to_python_invalid_json_data_is_string():
    """Невалидный JSON в --data-raw остаётся строкой."""
    parsed = utils.curl_to_python(CURL_BAD_JSON)
    assert parsed["data"] == "not a json"
    assert parsed["method"] == "POST"


def test_curl_to_python_explicit_method():
    """Явный -X переопределяет метод."""
    parsed = utils.curl_to_python("curl -X PUT 'https://api.example.com/x'")
    assert parsed["method"] == "PUT"


def test_curl_to_python_without_url():
    """Без URL возвращается url=None и пустые коллекции."""
    parsed = utils.curl_to_python(CURL_NO_URL)
    assert parsed["url"] is None
    assert parsed["headers"] == {"accept": "*/*"}
    assert parsed["cookies"] == {}


def test_extract_account_ids_from_accounts():
    """account_id берётся из заголовка new-api-user, иначе 'unknown'."""
    accounts = [CURL_SINGLE, CURL_DOUBLE]
    assert utils.extract_account_ids_from_accounts(accounts) == ["12345", "unknown"]


def test_extract_account_ids_multiple():
    """Несколько аккаунтов извлекаются по порядку."""
    accounts = [
        "curl 'https://x' -H 'new-api-user: 1'",
        "curl 'https://x' -H 'new-api-user: 2'",
        "curl 'https://x'",
    ]
    assert utils.extract_account_ids_from_accounts(accounts) == ["1", "2", "unknown"]


def test_curl_to_python_multiple_headers_with_colon_value():
    """Несколько -H сохраняются, значение с двоеточиями не обрезается."""
    parsed = utils.curl_to_python(CURL_MULTI_HEADERS)
    assert parsed["headers"]["x-time"] == "12:34:56"
    assert parsed["headers"]["accept"] == "application/json"
    assert parsed["headers"]["authorization"] == "Bearer a:b:c"
    assert len(parsed["headers"]) == 3


def test_curl_to_python_multiple_headers_double_quotes():
    """Двойные кавычки: несколько -H и значение с двоеточиями разбираются верно."""
    parsed = utils.curl_to_python(CURL_MULTI_HEADERS_DOUBLE)
    assert parsed["headers"]["x-time"] == "12:34:56"
    assert parsed["headers"]["accept"] == "application/json"
    assert len(parsed["headers"]) == 2
