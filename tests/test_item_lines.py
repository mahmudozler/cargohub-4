import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2", "api"))

from models.item_lines import ItemLines  

# Kleine, vaste testdata: 3 item lines.
TEST_ITEM_LINES = [
    {"id": 1, "name": "Zuivel", "description": "Melk, kaas en yoghurt"},
    {"id": 2, "name": "Diepvries", "description": "Diepvriesproducten"},
    {"id": 3, "name": "Brood", "description": "Brood en banket"},
]

@pytest.fixture
def item_lines(tmp_path):
    """Maak een ItemLines-model met de 3 test-item-lines in een tijdelijke map."""
    (tmp_path / "item_line.json").write_text(json.dumps(TEST_ITEM_LINES), encoding="utf-8")
    return ItemLines(str(tmp_path) + os.sep)

# get_item_lines

def test_get_item_lines_good(item_lines):
    """Goed: alle item lines komen terug."""
    assert item_lines.get_item_lines() == TEST_ITEM_LINES


def test_get_item_lines_bad_empty_file(tmp_path):
    """Slecht: een leeg bestand geeft een lege lijst."""
    (tmp_path / "item_line.json").write_text("[]", encoding="utf-8")
    assert ItemLines(str(tmp_path) + os.sep).get_item_lines() == []

# get_item_line

def test_get_item_line_good(item_lines):
    """Goed: item line 2 bestaat en komt terug."""
    assert item_lines.get_item_line(2) == TEST_ITEM_LINES[1]


def test_get_item_line_bad_unknown_id(item_lines):
    """Slecht: item line 99 bestaat niet, dus None."""
    assert item_lines.get_item_line(99) is None


def reload_item_lines(tmp_path):
    """Maak een nieuw model dat item_line.json opnieuw inleest."""
    return ItemLines(str(tmp_path) + os.sep)


NEW_ITEM_LINE = {"id": 4, "name": "Groente", "description": "Verse groente"}

# add_item_line (POST)

def test_add_item_line_good(item_lines, tmp_path):
    """Goed: na toevoegen en opslaan staat de nieuwe item line in het bestand."""
    item_lines.add_item_line(dict(NEW_ITEM_LINE))
    item_lines.save()
    new_item_line = reload_item_lines(tmp_path).get_item_line(4)
    assert new_item_line["name"] == "Groente"
    assert "created_at" in new_item_line and "updated_at" in new_item_line


def test_add_item_line_bad_not_saved_without_save(item_lines, tmp_path):
    """Slecht: zonder save() komt de nieuwe item line niet in het bestand."""
    item_lines.add_item_line(dict(NEW_ITEM_LINE))
    assert reload_item_lines(tmp_path).get_item_line(4) is None

# update_item_line (PUT)

def test_update_item_line_good(item_lines, tmp_path):
    """Goed: na wijzigen en opslaan heeft item line 2 de nieuwe naam."""
    item_lines.update_item_line(2, {"id": 2, "name": "Vriezer", "description": "Bevroren"})
    item_lines.save()
    assert reload_item_lines(tmp_path).get_item_line(2)["name"] == "Vriezer"


def test_update_item_line_bad_unknown_id(item_lines):
    """Slecht: item line 99 bestaat niet, dus er verandert niets."""
    item_lines.update_item_line(99, {"id": 99, "name": "X", "description": "Y"})
    assert item_lines.get_item_lines() == TEST_ITEM_LINES

# remove_item_line (DELETE)

def test_remove_item_line_good(item_lines, tmp_path):
    """Goed: na verwijderen en opslaan is item line 2 weg."""
    item_lines.remove_item_line(2)
    item_lines.save()
    reloaded = reload_item_lines(tmp_path)
    assert reloaded.get_item_line(2) is None
    assert len(reloaded.get_item_lines()) == 2


def test_remove_item_line_bad_unknown_id(item_lines):
    """Slecht: item line 99 bestaat niet, dus er verandert niets."""
    item_lines.remove_item_line(99)
    assert item_lines.get_item_lines() == TEST_ITEM_LINES


# get_missing_fields (controle bij POST en PUT)

def test_get_missing_fields_good(item_lines):
    """Goed: een complete item line mist geen velden."""
    assert item_lines.get_missing_fields(dict(NEW_ITEM_LINE)) == []


def test_get_missing_fields_bad_missing_fields(item_lines):
    """Slecht: een item line zonder name en description mist precies die twee velden."""
    assert item_lines.get_missing_fields({"id": 4}) == ["name", "description"]
