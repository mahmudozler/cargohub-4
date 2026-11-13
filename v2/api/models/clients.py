from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from v2.api.database.models import Client


class Clients:
    """Database-backed client operations."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_dict(client: Client) -> dict[str, Any]:
        result = {}
        for column in Client.__table__.columns:
            value = getattr(client, column.name)
            result[column.name] = (
                value.isoformat() if isinstance(value, datetime) else value
            )
        return result

    def get_clients(self) -> list[dict[str, Any]]:
        try:
            clients = self.db.scalars(select(Client).order_by(Client.id)).all()
            return [self._to_dict(client) for client in clients]
        finally:
            self.db.close()

    def get_client(self, client_id: int) -> dict[str, Any] | None:
        try:
            client = self.db.get(Client, client_id)
            return self._to_dict(client) if client is not None else None
        finally:
            self.db.close()

    # def add_client(self, client_data: dict[str, Any]) -> dict[str, Any]:
    #     try:
    #         client = Client(
    #             **{
    #                 column.name: client_data[column.name]
    #                 for column in Client.__table__.columns
    #                 if column.name in client_data and column.name != "id"
    #             }
    #         )
    #         self.db.add(client)
    #         self.db.commit()
    #         self.db.refresh(client)
    #         return self._to_dict(client)
    #     except Exception:
    #         self.db.rollback()
    #         raise
    #     finally:
    #         self.db.close()

    # def update_client(
    #     self, client_id: int, client_data: dict[str, Any]
    # ) -> dict[str, Any] | None:
    #     pass

    def remove_client(self, client_id: int) -> None:
        try:
            existing = self.db.get(Client, client_id)
            if existing is not None:
                self.db.delete(existing)
                self.db.commit()
            else:
                self.db.rollback()
        except Exception:
            self.db.rollback()
            raise
        finally:
            self.db.close()

    def save(self) -> None:
        pass
