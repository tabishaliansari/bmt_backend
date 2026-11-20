"""The editor's side: orders placed with the signed-in editor, accept or decline, deliver a cut.

Only Google accounts linked to an editor profile (EDITOR_ACCOUNTS) can use these routes, and
only for orders placed with that editor.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app import links, repo
from app.auth import CurrentIdentity
from app.models import Brief, DeliverRequest, Order
from app.payments import escrow
from app.routers.me import load_profile

router = APIRouter(prefix="/editor", tags=["editor"])


def linked_editor(identity: CurrentIdentity) -> tuple[str, str]:
    """(uid, editor_id) of the signed-in editor; 403 if the account isn't linked to one."""
    editor_id = load_profile(identity).editor_id
    if not editor_id:
        raise HTTPException(403, "This account isn't linked to an editor profile yet.")
    return identity.uid, editor_id


Editor = Annotated[tuple[str, str], Depends(linked_editor)]


class MediaItem(BaseModel):
    id: str
    kind: str
    label: str
    filename: str
    url: str


@router.get("/orders")
def list_jobs(editor: Editor) -> list[Order]:
    _, editor_id = editor
    return sorted(repo.list_orders_for_editor(editor_id), key=lambda o: o.created_at, reverse=True)


@router.get("/orders/{order_id}")
def get_job(order_id: str, editor: Editor) -> Order:
    return repo.get_order_for_editor(order_id, editor[1])


@router.get("/orders/{order_id}/media")
def job_media(order_id: str, editor: Editor) -> list[MediaItem]:
    """Signed links to the client's raw clips, the thumbnail concept and the delivered cut."""
    order = repo.get_order_for_editor(order_id, editor[1])
    items: list[tuple[str, str]] = []
    if order.brief_id:
        brief = repo.load("briefs", order.brief_id, Brief, "brief")
        items += [(upload_id, f"Raw clip {i + 1}") for i, upload_id in enumerate(brief.upload_ids)]
    if order.thumbnail_upload_id:
        items.append((order.thumbnail_upload_id, "Thumbnail concept"))
    if order.cut_upload_id:
        items.append((order.cut_upload_id, "Your delivered cut"))
    media = []
    for upload_id, label in items:
        upload = repo.get_upload(upload_id, owner=None)
        media.append(MediaItem(id=upload.id, kind=upload.kind, label=label, filename=upload.filename, url=links.media_url(upload.id)))
    return media


@router.post("/orders/{order_id}/accept")
def accept(order_id: str, editor: Editor) -> Order:
    order = escrow.transition(repo.get_order_for_editor(order_id, editor[1]), "accept")
    repo.save("orders", order)
    return order


@router.post("/orders/{order_id}/decline")
def decline(order_id: str, editor: Editor) -> Order:
    """Decline a new order: the client's held payment is refunded (simulated)."""
    order = escrow.transition(repo.get_order_for_editor(order_id, editor[1]), "decline")
    repo.save("orders", order)
    return order


@router.post("/orders/{order_id}/deliver")
def deliver(order_id: str, body: DeliverRequest, editor: Editor) -> Order:
    uid, editor_id = editor
    order = repo.get_order_for_editor(order_id, editor_id)
    if order.status == "funded":
        raise HTTPException(409, "Accept the order before delivering a cut.")
    upload = repo.get_upload(body.cut_upload_id, owner=uid)
    if upload.kind != "cut":
        raise HTTPException(422, "Deliver an upload of kind 'cut', not raw footage.")
    order = escrow.transition(order, "deliver")
    order = order.model_copy(update={"cut_upload_id": upload.id, "review": None, "client_notes": []})
    repo.save("orders", order)
    return order
