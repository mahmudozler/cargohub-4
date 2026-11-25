import json

from models.base import Base
from providers import data_provider

ORDERS = []

class Orders(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "order.json"
        self.load(is_debug)

    def get_orders(self):
        if not self.data:
            return []

        items_per_order = {}
        for row in data_provider.fetch_order_item_pool().data:
            order_id = row["order_id"]
            if order_id not in items_per_order:
                items_per_order[order_id] = []
            items_per_order[order_id].append(
                {"item_id": row["item_id"], "amount": row["amount"]}
            )

        result = []
        for order in self.data:
            order = dict(order)
            order["items"] = items_per_order.get(order["id"], [])
            result.append(order)
        return result

    def get_order(self, order_id):
        for order in self.data:
            if order["id"] == order_id:
                return self._with_items(order)
        return None

    def get_items_in_order(self, order_id):
        rows = data_provider.fetch_order_item_pool().get_items_for_order(order_id)
        return [{"item_id": row["item_id"], "amount": row["amount"]} for row in rows]

    def get_orders_for_client(self, client_id):
        return [
            self._with_items(order) for order in self.data
            if client_id in (order["client_id"], order["ship_to_client_id"], order["bill_to_client_id"])
        ]

    def add_order(self, order):
        items = order.pop("items", [])
        order["created_at"] = self.get_timestamp()
        order["updated_at"] = self.get_timestamp()
        self.data.append(order)
        self._save_items_for_order(order["id"], items)

    def update_order(self, order_id, order):
        index = self._index_of(order_id)
        if index is None:
            return
        items = order.pop("items", None)
        order["updated_at"] = self.get_timestamp()
        self.data[index] = order
        if items is not None:
            self.update_items_in_order(order_id, items)

    def update_items_in_order(self, order_id, items):
        current = self.get_items_in_order(order_id)
        current_by_item = {x["item_id"]: x["amount"] for x in current}
        new_by_item = {x["item_id"]: x["amount"] for x in items}

        inventory_pool = data_provider.fetch_inventory_pool()
        for item_id, new_amount in new_by_item.items():
            old_amount = current_by_item.get(item_id, 0)
            delta = new_amount - old_amount
            if delta != 0:
                self._apply_allocation_delta(inventory_pool, item_id, delta)
        for item_id, old_amount in current_by_item.items():
            if item_id not in new_by_item:
                self._apply_allocation_delta(inventory_pool, item_id, -old_amount)

        inventory_pool.save()
        self._save_items_for_order(order_id, items)

    @staticmethod
    def _apply_allocation_delta(inventory_pool, item_id, delta):
        inventories = inventory_pool.get_inventories_for_item(item_id)
        if not inventories:
            return
        target = max(inventories, key=lambda z: z["quantity_on_hand"])
        target["quantity_allocated"] = max(0, target["quantity_allocated"] + delta)
        inventory_pool.update_inventory(item_id, target["location_id"], target)

    def remove_order(self, order_id):
        index = self._index_of(order_id)
        if index is None:
            return
        del self.data[index]
        order_item_pool = data_provider.fetch_order_item_pool()
        order_item_pool.remove_items_for_order(order_id)
        order_item_pool.save()

    def _index_of(self, order_id):
        for index, order in enumerate(self.data):
            if order["id"] == order_id:
                return index
        return None

    @staticmethod
    def _save_items_for_order(order_id, items):
        order_item_pool = data_provider.fetch_order_item_pool()
        order_item_pool.set_items_for_order(order_id, items)
        order_item_pool.save()

    def _with_items(self, order):
        order = dict(order)
        order["items"] = self.get_items_in_order(order["id"])
        return order

    def load(self, is_debug):
        if is_debug:
            self.data = ORDERS
        else:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def save(self):
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f)
