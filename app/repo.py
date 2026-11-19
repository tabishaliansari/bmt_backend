"""Typed load/save helpers over the database. Loaders raise 404 when the record is missing."""

from typing import TypeVar

from fastapi import HTTPException
from pydantic import BaseModel

from app.db import get_db
from app.models import Brief, Editor, Order, Upload

M = TypeVar("M", bound=BaseModel)


def load(collection: str, doc_id: str, model: type[M], label: str) -> M:
    data = get_db().get(collection, doc_id)
    if data is None:
        raise HTTPException(404, f"No {label} with id '{doc_id}'")
    return model.model_validate(data)


def save(collection: str, record: Editor | Brief | Upload | Order) -> None:
    get_db().put(collection, record.id, record.model_dump(mode="json"))


def get_editor(editor_id: str) -> Editor:
    return load("editors", editor_id, Editor, "editor")


def get_brief(brief_id: str) -> Brief:
    return load("briefs", brief_id, Brief, "brief")


def get_upload(upload_id: str) -> Upload:
    return load("uploads", upload_id, Upload, "upload")


def get_order(order_id: str) -> Order:
    return load("orders", order_id, Order, "order")


def list_orders() -> list[Order]:
    return [Order.model_validate(d) for d in get_db().list("orders")]
