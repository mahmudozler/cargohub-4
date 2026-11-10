import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

API_BASE_URL = os.environ.get("CARGOHUB_URL", "http://145.24.237.163:8000/api/v1")
API_KEY = "r2e4c6e8i0v3i5n7g9s"


def get(path, api_key=API_KEY):
    request = Request(f"{API_BASE_URL}{path}", headers={"API_KEY": api_key}, method="GET")
    try:
        with urlopen(request, timeout=30) as response:
            status, body = response.status, response.read()
    except HTTPError as error:
        status, body = error.code, error.read()
    return status, (json.loads(body) if body else None)


def test_get_item_lines_good():
    status, body = get("/item_lines")
    assert status == 200
    assert len(body) > 0


def test_get_item_line_good():
    status, body = get("/item_lines/1")
    assert status == 200
    assert body["name"] == "Aardappelen, groente en fruit"


def test_get_item_line_bad_unknown_id():
    status, body = get("/item_lines/99999")
    assert status == 200
    assert body is None


def test_get_item_line_items_good():
    status, body = get("/item_lines/1/items")
    assert status == 200
    assert body[:8] == [4, 9, 21, 22, 55, 56, 58, 62]
