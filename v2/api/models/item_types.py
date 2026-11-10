import json

from models.base import Base

ITEM_TYPES = []

class ItemTypes(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "item_type.json"
        self.load(is_debug)

      """Geef de lijst met alle item types."""
    def get_item_types(self):
        return self.data

        """Geef het item type met dit id, of None als het niet bestaat."""
    def get_item_type(self, item_type_id):
        for item_type in self.data:
            if item_type["id"] == item_type_id:
                return item_type
        return None

    def add_item_type(self, item_type):
        item_type["created_at"] = self.get_timestamp()
        item_type["updated_at"] = self.get_timestamp()
        self.data.append(item_type)

    def update_item_type(self, item_type_id, item_type):
        item_type["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == item_type_id:
                self.data[i] = item_type
                break

    def remove_item_type(self, item_type_id):
        for x in self.data:
            if x["id"] == item_type_id:
                self.data.remove(x)

    def load(self, is_debug):
        if is_debug:
            self.data = ITEM_TYPES
        else:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def save(self):
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f)