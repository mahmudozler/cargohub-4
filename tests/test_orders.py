import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2", "api"))

from providers import data_provider
from models.orders import Orders


TEST_ORDERS = [
    {"id": 1, "client_id": 10, "ship_to_client_id": 20, "bill_to_client_id": 30},
    {"id": 2, "client_id": 20, "ship_to_client_id": 10, "bill_to_client_id": 30},
    {"id": 3, "client_id": 30, "ship_to_client_id": 30, "bill_to_client_id": 30},
]

TEST_ORDER_ITEMS = [
    {"id": 1, "order_id": 1, "item_id": 10, "amount": 5, "unit_price": 12},
    {"id": 2, "order_id": 1, "item_id": 11, "amount": 2},
    {"id": 3, "order_id": 2, "item_id": 12, "amount": 7},
]

EXPECTED_ORDERS = [
    {**TEST_ORDERS[0], "items": [{"item_id": 10, "amount": 5}, {"item_id": 11, "amount": 2}]},
    {**TEST_ORDERS[1], "items": [{"item_id": 12, "amount": 7}]},
    {**TEST_ORDERS[2], "items": []},
]


@pytest.fixture
def orders(tmp_path, monkeypatch):
    (tmp_path / "order.json").write_text(json.dumps(TEST_ORDERS), encoding="utf-8")
    (tmp_path / "order_item.json").write_text(json.dumps(TEST_ORDER_ITEMS), encoding="utf-8")
    monkeypatch.setattr(data_provider, "ROOT_PATH", str(tmp_path) + os.sep)
    return Orders(str(tmp_path) + os.sep)


@pytest.fixture
def empty_orders(orders, tmp_path):
    (tmp_path / "order.json").write_text("[]", encoding="utf-8")
    return Orders(str(tmp_path) + os.sep)


def test_get_orders_good(orders):
    assert orders.get_orders() == EXPECTED_ORDERS


def test_get_orders_empty(empty_orders):
    assert empty_orders.get_orders() == []


def test_get_order_good(orders):
    assert orders.get_order(2) == EXPECTED_ORDERS[1]


def test_get_order_bad_unknown_id(orders):
    assert orders.get_order(999) is None


def test_get_order_empty(empty_orders):
    assert empty_orders.get_order(1) is None


def test_get_order_without_items(orders):
    assert orders.get_order(3) == EXPECTED_ORDERS[2]


def test_get_items_in_order_good(orders):
    assert orders.get_items_in_order(1) == [
        {"item_id": 10, "amount": 5},
        {"item_id": 11, "amount": 2},
    ]


def test_get_items_in_order_bad_unknown_id(orders):
    assert orders.get_items_in_order(999) == []


def test_get_items_in_order_without_items(orders):
    assert orders.get_items_in_order(3) == []


def test_get_orders_for_client_good(orders):
    assert orders.get_orders_for_client(20) == EXPECTED_ORDERS[:2]


def test_get_orders_for_client_ship_to(orders):
    assert orders.get_orders_for_client(10) == EXPECTED_ORDERS[:2]


def test_get_orders_for_client_bill_to_without_duplicates(orders):
    assert orders.get_orders_for_client(30) == EXPECTED_ORDERS


def test_get_orders_for_client_bad_unknown_id(orders):
    assert orders.get_orders_for_client(999) == []


def test_get_orders_for_client_empty(empty_orders):
    assert empty_orders.get_orders_for_client(10) == []


def test_get_orders_does_not_change_stored_data(orders):
    orders.get_orders()
    orders.get_order(1)
    orders.get_orders_for_client(10)

    assert orders.data == TEST_ORDERS


NEW_ORDER = {"id": 4, "client_id": 40, "ship_to_client_id": 40, "bill_to_client_id": 40}
UPDATED_ORDER_2 = {"id": 2, "client_id": 99, "ship_to_client_id": 10, "bill_to_client_id": 30}


def reload_orders(tmp_path):
    return Orders(str(tmp_path) + os.sep)


def read_json(tmp_path, name):
    return json.loads((tmp_path / name).read_text(encoding="utf-8"))


def test_add_order_good(orders, tmp_path):
    orders.add_order({**NEW_ORDER, "items": [{"item_id": 10, "amount": 3}]})
    orders.save()

    new_order = reload_orders(tmp_path).get_order(4)
    assert new_order["client_id"] == 40
    assert "created_at" in new_order and "updated_at" in new_order


def test_add_order_items_not_in_order_record(orders):
    orders.add_order({**NEW_ORDER, "items": [{"item_id": 10, "amount": 3}]})

    assert "items" not in orders.data[-1]


def test_add_order_without_items(orders, tmp_path):
    orders.add_order(dict(NEW_ORDER))
    orders.save()

    assert reload_orders(tmp_path).get_order(4)["items"] == []


def test_add_order_bad_not_saved_without_save(orders, tmp_path):
    orders.add_order(dict(NEW_ORDER))

    assert reload_orders(tmp_path).get_order(4) is None


def test_update_order_good(orders, tmp_path):
    orders.update_order(2, dict(UPDATED_ORDER_2))
    orders.save()

    updated = reload_orders(tmp_path).get_order(2)
    assert updated["client_id"] == 99
    assert "updated_at" in updated


def test_update_order_keeps_items_without_items_in_body(orders, tmp_path):
    orders.update_order(2, dict(UPDATED_ORDER_2))
    orders.save()

    assert reload_orders(tmp_path).get_items_in_order(2) == [{"item_id": 12, "amount": 7}]


def test_update_order_other_orders_unchanged(orders):
    orders.update_order(2, dict(UPDATED_ORDER_2))

    assert orders.data[0] == TEST_ORDERS[0]
    assert orders.data[2] == TEST_ORDERS[2]


def test_update_order_bad_unknown_id(orders, tmp_path):
    orders.update_order(99, {"id": 99, "client_id": 1})

    assert orders.get_order(99) is None
    assert orders.data == TEST_ORDERS
    assert read_json(tmp_path, "order_item.json") == TEST_ORDER_ITEMS


def test_remove_order_good(orders, tmp_path):
    orders.remove_order(2)
    orders.save()

    reloaded = reload_orders(tmp_path)
    assert reloaded.get_order(2) is None
    assert len(reloaded.data) == 2


