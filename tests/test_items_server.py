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


def test_get_items_good():
    status, body = get("/items")
    assert status == 200
    assert len(body) > 0


def test_get_items_bad_without_api_key():
    status, _ = get("/items", api_key="onzin-key")
    assert status == 401


def test_get_item_good():
    status, body = get("/items/1")
    assert status == 200
    assert body["code"] == "ITM-000001"


def test_get_item_bad_unknown_id():
    status, body = get("/items/99999")
    assert status == 200
    assert body is None


def test_get_item_inventory_good():
    status, body = get("/items/1/inventory")
    assert status == 200
    assert all(row["item_id"] == 1 for row in body)


def test_get_item_inventory_totals_good():
    status, body = get("/items/1/inventory/totals")
    assert status == 200
    assert set(body) == {"total_expected", "total_ordered", "total_allocated", "total_available"}
