import os

from models.clients import Clients
from models.inventories import Inventories
from models.item_groups import ItemGroups
from models.item_lines import ItemLines
from models.item_types import ItemTypes
from models.items import Items
from models.locations import Locations
from models.order_items import OrderItems
from models.orders import Orders
from models.shipment_items import ShipmentItems
from models.shipments import Shipments
from models.suppliers import Suppliers
from models.transfer_items import TransferItems
from models.transfers import Transfers
from models.warehouses import Warehouses

from v2.api.database.database import SessionLocal

DEBUG = False

_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)

ROOT_PATH = _ROOT + os.sep

def fetch_warehouse_pool():
    return Warehouses(ROOT_PATH, DEBUG)

def fetch_location_pool():
    return Locations(ROOT_PATH, DEBUG)

def fetch_transfer_pool():
    return Transfers(ROOT_PATH, DEBUG)

def fetch_transfer_item_pool():
    return TransferItems(ROOT_PATH, DEBUG)

def fetch_item_pool():
    return Items(ROOT_PATH, DEBUG)

def fetch_item_line_pool():
    return ItemLines(ROOT_PATH, DEBUG)

def fetch_item_group_pool():
    return ItemGroups(ROOT_PATH, DEBUG)

def fetch_item_type_pool():
    return ItemTypes(ROOT_PATH, DEBUG)

def fetch_inventory_pool():
    return Inventories(ROOT_PATH, DEBUG)

def fetch_supplier_pool():
    return Suppliers(ROOT_PATH, DEBUG)

def fetch_order_pool():
    return Orders(ROOT_PATH, DEBUG)

def fetch_order_item_pool():
    return OrderItems(ROOT_PATH, DEBUG)

def fetch_client_pool():
    return Clients(SessionLocal())

def fetch_shipment_pool():
    return Shipments(ROOT_PATH, DEBUG)

def fetch_shipment_item_pool():
    return ShipmentItems(ROOT_PATH, DEBUG)