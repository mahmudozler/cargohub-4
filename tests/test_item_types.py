
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2", "api"))

from models.item_types import ItemTypes  # pylint: disable=wrong-import-position

# Kleine, vaste testdata: 3 item types.
TEST_ITEM_TYPES = [
    {"id": 1, "name": "Single", "description": "Packaging tier: Single"},
    {"id": 2, "name": "Multipack", "description": "Packaging tier: Multipack"},
    {"id": 3, "name": "Crate", "description": "Packaging tier: Crate"},
]


@pytest.fixture
def item_types(tmp_path):
    (tmp_path / "item_type.json").write_text(json.dumps(TEST_ITEM_TYPES), encoding="utf-8")
    return ItemTypes(str(tmp_path) + os.sep)


# get_item_types
 """Goed: alle item types komen terug."""
def test_get_item_types_good(item_types):
    assert item_types.get_item_types() == TEST_ITEM_TYPES

"""Slecht: een leeg bestand geeft een lege lijst (geen fout)."""
def test_get_item_types_bad_empty_file(tmp_path):
    (tmp_path / "item_type.json").write_text("[]", encoding="utf-8")
    assert ItemTypes(str(tmp_path) + os.sep).get_item_types() == []


# get_item_type
"""Goed: item type 2 bestaat en komt terug."""
def test_get_item_type_good(item_types):
    assert item_types.get_item_type(2) == TEST_ITEM_TYPES[1]

 """Slecht: item type 99 bestaat niet, dus None."""
def test_get_item_type_bad_unknown_id(item_types):
    assert item_types.get_item_type(99) is None
