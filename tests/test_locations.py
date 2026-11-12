import json
import os
import sys
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2", "api"),
)
from models.locations import Locations

TEST_LOCATIONS = [
    {"id": 1, "warehouse_id": 10, "code": "A-01"},
    {"id": 2, "warehouse_id": 20, "code": "B-01"},
    {"id": 3, "warehouse_id": 10, "code": "A-02"},
]


@pytest.fixture
def locations(tmp_path):
    data_file = tmp_path / "location.json"
    data_file.write_text(
        json.dumps(TEST_LOCATIONS),
        encoding="utf-8",
    )

    return Locations(str(tmp_path) + os.sep)


@pytest.fixture
def empty_locations(tmp_path):
    data_file = tmp_path / "location.json"
    data_file.write_text("[]", encoding="utf-8")

    return Locations(str(tmp_path) + os.sep)


def test_get_locations_good(locations):
    result = locations.get_locations()

    assert result == TEST_LOCATIONS


def test_get_locations_empty(empty_locations):
    result = empty_locations.get_locations()

    assert result == []


def test_get_location_good(locations):
    result = locations.get_location(2)

    assert result == TEST_LOCATIONS[1]


def test_get_location_bad_unknown_id(locations):
    result = locations.get_location(999)

    assert result is None


def test_get_location_empty(empty_locations):
    result = empty_locations.get_location(1)

    assert result is None


def test_get_locations_in_warehouse_good(locations):
    result = locations.get_locations_in_warehouse(10)

    assert result == [TEST_LOCATIONS[0], TEST_LOCATIONS[2]]


def test_get_locations_in_warehouse_one_location(locations):
    result = locations.get_locations_in_warehouse(20)

    assert result == [TEST_LOCATIONS[1]]


def test_get_locations_in_warehouse_bad_unknown_id(locations):
    result = locations.get_locations_in_warehouse(999)

    assert result == []


def test_add_location_good(locations):
    new_location = {"id": 4, "warehouse_id": 30, "code": "C-01"}

    locations.add_location(new_location)

    result = locations.get_location(4)
    assert result["warehouse_id"] == 30
    assert result["code"] == "C-01"
    assert len(locations.get_locations()) == 4


def test_add_location_sets_timestamps(locations):
    new_location = {"id": 4, "warehouse_id": 30, "code": "C-01"}

    before = datetime.now(timezone.utc).replace(tzinfo=None)
    locations.add_location(new_location)
    after = datetime.now(timezone.utc).replace(tzinfo=None)

    result = locations.get_location(4)
    assert result["created_at"].endswith("Z")
    assert result["updated_at"].endswith("Z")

    created_at = datetime.fromisoformat(result["created_at"][:-1])
    updated_at = datetime.fromisoformat(result["updated_at"][:-1])
    assert before <= created_at <= updated_at <= after


def test_add_location_empty(empty_locations):
    new_location = {"id": 1, "warehouse_id": 10, "code": "A-01"}

    empty_locations.add_location(new_location)

    assert len(empty_locations.get_locations()) == 1
    assert empty_locations.get_location(1)["code"] == "A-01"


def test_add_location_save_persists(locations, tmp_path):
    new_location = {"id": 4, "warehouse_id": 30, "code": "C-01"}

    locations.add_location(new_location)
    locations.save()

    reloaded = Locations(str(tmp_path) + os.sep)
    assert reloaded.get_location(4)["code"] == "C-01"


def test_update_location_good(locations):
    updated = {"id": 2, "warehouse_id": 20, "code": "B-99"}

    locations.update_location(2, updated)

    result = locations.get_location(2)
    assert result["code"] == "B-99"
    assert "updated_at" in result
    assert len(locations.get_locations()) == 3


