from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from v2.api.database.database import engine
from models import (
    Base,
    Client,
    EndpointAccess,
    Inventory,
    Item,
    ItemGroup,
    ItemLine,
    ItemType,
    Location,
    Order,
    OrderItem,
    Shipment,
    ShipmentItem,
    Supplier,
    Transfer,
    TransferItem,
    User,
    Warehouse,
)
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

# moet iets hiermee doen als deze nog een keer wordt gebruikt, want nu wordt de database connectie niet gesloten

# DATABASE_URL = "postgresql+psycopg://admin:admin@localhost:5433/cargohub"
# engine = create_engine(DATABASE_URL)


TABLES = (
    Warehouse,
    Location,
    ItemLine,
    ItemGroup,
    ItemType,
    Supplier,
    Item,
    Inventory,
    Client,
    Order,
    OrderItem,
    Shipment,
    ShipmentItem,
    Transfer,
    TransferItem,
    User,
    EndpointAccess,
)


def read_rows(data_dir: Path, filename: str) -> list[dict[str, Any]]:
    with (data_dir / filename).open(encoding="utf-8") as data_file:
        rows = json.load(data_file)
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"{filename} must contain a JSON array of objects")
    return rows


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def rows_for_model(data_dir: Path, filename: str, model: type[Any]) -> list[Any]:
    result = []
    for row in read_rows(data_dir, filename):
        values = dict(row)
        for field in ("created_at", "updated_at", "order_date", "request_date", "shipment_date"):
            if field in values:
                values[field] = parse_datetime(values[field])
        result.append(model(**values))
    return result


def import_json_data(data_dir: Path, replace: bool = False) -> bool:
    """Import every v1 JSON file only when all target tables are empty."""
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        populated_tables = [
            model.__tablename__
            for model in TABLES
            if session.execute(select(model).limit(1)).first() is not None
        ]
        if populated_tables:
            print(
                "JSON import skipped; these tables already contain data: "
                + ", ".join(populated_tables)
            )
            return False

        if replace:
            for model in reversed(TABLES):
                session.execute(delete(model))

        files_and_models = (
            ("warehouse.json", Warehouse),
            ("location.json", Location),
            ("item_line.json", ItemLine),
            ("item_group.json", ItemGroup),
            ("item_type.json", ItemType),
            ("supplier.json", Supplier),
            ("item.json", Item),
            ("inventory.json", Inventory),
            ("client.json", Client),
            ("order.json", Order),
            ("order_item.json", OrderItem),
            ("shipment.json", Shipment),
            ("shipment_item.json", ShipmentItem),
            ("transfer.json", Transfer),
            ("transfer_item.json", TransferItem),
        )
        for filename, model in files_and_models:
            session.add_all(rows_for_model(data_dir, filename, model))

        for user_id, row in enumerate(read_rows(data_dir, "user.json"), start=1):
            permissions = row.get("endpoint_access", {})
            user = User(id=user_id, api_key=row["api_key"], app=row.get("app"))
            user.endpoint_access = [
                EndpointAccess(
                    resource=resource,
                    can_get=bool(values.get("get", False)),
                    can_post=bool(values.get("post", False)),
                    can_put=bool(values.get("put", False)),
                    can_delete=bool(values.get("delete", False)),
                )
                for resource, values in permissions.items()
            ]
            session.add(user)

        session.commit()
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "v1" / "data",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Retained for compatibility; populated tables are never deleted.",
    )
    args = parser.parse_args()
    imported = import_json_data(args.data_dir, replace=args.replace)
    if imported:
        print("JSON import completed.")


if __name__ == "__main__":
    main()
