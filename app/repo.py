"""Typed load/save helpers over the database.

Loaders raise 404 when the record is missing, and also when it belongs to someone else
(so ids of other users' records reveal nothing).
"""

from typing import TypeVar

from fastapi import HTTPException
from pydantic import BaseModel

from app.db import get_db
from app.models import Brief, Editor, Order, Upload, UserProfile

M = TypeVar("M", bound=BaseModel)


def load(collection: str, doc_id: str, model: type[M], label: str, owner: str | None = None) -> M:
    data = get_db().get(collection, doc_id)
    if data is None or (owner is not None and data.get("owner") != owner):
        raise HTTPException(404, f"No {label} with id '{doc_id}'")
    return model.model_validate(data)


def save(collection: str, record: Editor | Brief | Upload | Order | UserProfile) -> None:
    get_db().put(collection, record.id, record.model_dump(mode="json"))


def get_editor(editor_id: str) -> Editor:
    return load("editors", editor_id, Editor, "editor")


def get_brief(brief_id: str, owner: str) -> Brief:
    return load("briefs", brief_id, Brief, "brief", owner)


def get_upload(upload_id: str, owner: str | None) -> Upload:
    """owner=None only for signed media links, where the signature already proves access."""
    return load("uploads", upload_id, Upload, "upload", owner)


def get_order(order_id: str, owner: str) -> Order:
    return load("orders", order_id, Order, "order", owner)


def list_orders(owner: str) -> list[Order]:
    return [Order.model_validate(d) for d in get_db().list("orders", owner=owner)]


def order_has_media(owner: str, upload_id: str) -> bool:
    """True if one of this client's orders has the upload as its cut or thumbnail."""
    db = get_db()
    return bool(db.list("orders", owner=owner, cut_upload_id=upload_id)
                or db.list("orders", owner=owner, thumbnail_upload_id=upload_id))


def list_orders_for_editor(editor_id: str) -> list[Order]:
    return [Order.model_validate(d) for d in get_db().list("orders", editor_id=editor_id)]


def get_order_for_editor(order_id: str, editor_id: str) -> Order:
    """An order placed with this editor (not necessarily owned by the caller)."""
    order = load("orders", order_id, Order, "order")
    if order.editor_id != editor_id:
        raise HTTPException(404, f"No order with id '{order_id}'")
    return order
