import json

from models.base import Base

ITEMS = []

# Velden die een item minimaal moet hebben bij POST en PUT.
REQUIRED_FIELDS = [
    "id", "code", "description", "item_line_id",
    "item_group_id", "item_type_id", "supplier_id",
]

class Items(Base):
    """Alle items uit data/item.json."""

    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "item.json"
        self.load(is_debug)

    def get_items(self):
        """Geef de lijst met alle items."""
        return self.data

    def get_item(self, item_id):
        """Geef het item met dit id, of None als het niet bestaat."""
        for item in self.data:
            if item["id"] == item_id:
                return item
        return None

    def get_items_for_item_line(self, item_line_id):
        """Geef de id's van alle items in deze item line."""
        return self.get_item_ids_where("item_line_id", item_line_id)

    def get_items_for_item_group(self, item_group_id):
        """Geef de id's van alle items in deze item group."""
        return self.get_item_ids_where("item_group_id", item_group_id)

    def get_items_for_item_type(self, item_type_id):
        """Geef de id's van alle items van dit item type."""
        return self.get_item_ids_where("item_type_id", item_type_id)

    def get_items_for_supplier(self, supplier_id):
        """Geef de volledige items (niet alleen id's) van deze leverancier."""
        return [item for item in self.data if item["supplier_id"] == supplier_id]

    def get_missing_fields(self, item):
        """Geef de verplichte velden die in dit item ontbreken."""
        return [field for field in REQUIRED_FIELDS if field not in item]

    def get_item_ids_where(self, field, value):
        """Geef de id's van alle items waarbij field gelijk is aan value."""
        return [item["id"] for item in self.data if item[field] == value]

    def add_item(self, item):
        """Voeg een item toe aan de lijst en zet created_at en updated_at."""
        item["created_at"] = self.get_timestamp()
        item["updated_at"] = self.get_timestamp()
        self.data.append(item)

    def update_item(self, item_id, item):
        """Vervang het item met dit id door het nieuwe item en zet updated_at."""
        item["updated_at"] = self.get_timestamp()
        for index, existing_item in enumerate(self.data):
            if existing_item["id"] == item_id:
                self.data[index] = item
                break

    def remove_item(self, item_id):
        """Haal het item met dit id uit de lijst."""
        self.data = [item for item in self.data if item["id"] != item_id]

    def load(self, is_debug):
        """Lees item.json in."""
        if is_debug:
            self.data = ITEMS
        else:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def save(self):
        """Schrijf de lijst met items terug naar item.json."""
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f)
