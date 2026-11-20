import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException

from app import repo
from app.ai.review_copilot import review_order
from app.ai.screen import screen_text
from app.auth import UserId
from app.models import (
    ClientNote, DeliverRequest, Order, OrderRequest, ReviewRequest, ReviewResult,
)
from app.payments import escrow
from app.payments.payouts import create_payout
from app.payments.pricing import find_package, quote
from app.ratelimit import check_ai_quota

router = APIRouter(prefix="/orders", tags=["orders"])

RUSH_HOURS = 24
BASE_REVISIONS = 2
ORDER_CODE_CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I/L
ORDER_CODE_LEN = 8


def new_order_id() -> str:
    """Random, so order ids can't be guessed or walked (BMT-7KQ2XDMA)."""
    return "BMT-" + "".join(secrets.choice(ORDER_CODE_CHARS) for _ in range(ORDER_CODE_LEN))


@router.post("", status_code=201)
def create_order(body: OrderRequest, uid: UserId) -> Order:
    editor = repo.get_editor(body.editor_id)
    package = find_package(editor, body.package_id)
    brief = repo.get_brief(body.brief_id, owner=uid) if body.brief_id else None
    total_usd, total_inr = quote(package, body.addons, body.rush)
    now = datetime.now(UTC)
    order = Order(
        id=new_order_id(), owner=uid, editor_id=editor.id, package_id=package.id,
        brief_id=brief.id if brief else None, brief=brief.result if brief else None,
        thumbnail_upload_id=brief.thumbnail_upload_id if brief else None,
        title=package.title, g=package.g, addons=list(dict.fromkeys(body.addons)), rush=body.rush,
        note=body.note, total_usd=total_usd, total_inr=total_inr, status="funded",
        revisions_left=BASE_REVISIONS + (1 if "revision" in body.addons else 0),
        due_at=now + timedelta(hours=RUSH_HOURS if body.rush else package.eta_hours),
        timeline=[escrow.event("funded")], created_at=now,
    )
    repo.save("orders", order)
    return order


@router.get("")
def list_orders(uid: UserId) -> list[Order]:
    """Only the signed-in user's orders, newest first."""
    return sorted(repo.list_orders(owner=uid), key=lambda o: o.created_at, reverse=True)


@router.get("/{order_id}")
def get_order(order_id: str, uid: UserId) -> Order:
    return repo.get_order(order_id, owner=uid)


@router.post("/{order_id}/deliver")
def deliver(order_id: str, body: DeliverRequest, uid: UserId) -> Order:
    """The editor delivers a cut. In the demo, the client uploads it on the editor's behalf."""
    upload = repo.get_upload(body.cut_upload_id, owner=uid)
    if upload.kind != "cut":
        raise HTTPException(422, "Deliver an upload of kind 'cut', not raw footage.")
    order = escrow.transition(repo.get_order(order_id, owner=uid), "deliver")
    order = order.model_copy(update={"cut_upload_id": upload.id, "review": None, "client_notes": []})
    repo.save("orders", order)
    return order


@router.post("/{order_id}/revisions")
def request_changes(order_id: str, uid: UserId) -> Order:
    order = repo.get_order(order_id, owner=uid)
    if order.revisions_left <= 0:
        raise HTTPException(409, "No revisions left on this order.")
    order = escrow.transition(order, "request_changes")
    order = order.model_copy(update={"revisions_left": order.revisions_left - 1})
    repo.save("orders", order)
    return order


@router.post("/{order_id}/notes", status_code=201)
def add_note(order_id: str, body: ClientNote, uid: UserId) -> Order:
    """A note the client pins at a moment in the cut."""
    order = repo.get_order(order_id, owner=uid)
    notes = sorted([*order.client_notes, body], key=lambda n: n.t)
    order = order.model_copy(update={"client_notes": notes})
    repo.save("orders", order)
    return order


@router.post("/{order_id}/review")
def review(order_id: str, body: ReviewRequest, uid: UserId) -> ReviewResult:
    order = repo.get_order(order_id, owner=uid)
    if order.status != "review" or not order.cut_upload_id:
        raise HTTPException(409, "There is no delivered cut to review yet.")
    check_ai_quota(uid)
    if body.client_feedback:
        verdict, _ = screen_text(body.client_feedback)
        if not verdict.allowed:
            raise HTTPException(422, f"Please rephrase your feedback: {verdict.reason}")
    result = review_order(order, repo.get_upload(order.cut_upload_id, owner=uid), body.client_feedback)
    repo.save("orders", order.model_copy(update={"review": result}))
    return result


@router.post("/{order_id}/approve")
def approve(order_id: str, uid: UserId) -> Order:
    order = escrow.transition(repo.get_order(order_id, owner=uid), "approve")
    order = order.model_copy(update={"payout": create_payout(order.total_usd)})
    repo.save("orders", order)
    return order
