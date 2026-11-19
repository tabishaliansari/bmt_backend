"""Pydantic models shared by the API, the database and (later) the AI layer."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Package(BaseModel):
    id: str
    editor_id: str
    title: str
    desc: str
    price_inr: float
    price_usd: float
    eta_hours: int
    tag: Literal["try", "best"] | None = None
    g: int  # thumbnail gradient index (UI only)


class Credit(BaseModel):
    g: int
    title: str
    channel: str
    views: str
    date: str
    len: str
    confirmed: bool = True


class Review(BaseModel):
    name: str
    av: int
    stars: int
    text: str
    item: str
    when: str


class Editor(BaseModel):
    id: str
    name: str
    initials: str
    av: int
    handle: str
    city: str
    styles: list[str]
    categories: list[str]
    cover: int
    rating: float
    rating_count: int
    credits: int
    channels: int
    views: str
    on_time: int
    reply: str
    from_inr: float
    days: str
    packages: list[Package]
    credit_list: list[Credit]
    reviews: list[Review]
    work: list[int]


UploadKind = Literal["raw", "cut"]


class UploadOut(BaseModel):
    id: str
    kind: UploadKind
    filename: str
    mime: str
    size: int


class Upload(UploadOut):
    storage_path: str
    created_at: datetime
