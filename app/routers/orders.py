from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException

from app import repo
from app.ai.review_copilot import review_order
from app.models import (
    ClientNote, DeliverRequest, Order, OrderRequest, ReviewRequest, ReviewResult,
)
from app.payments import escrow
from app.payments.payouts import create_payout
from app.payments.pricing import find_package, quote

router = APIRouter(prefix="/orders", tags=["orders"])

FIRST_ORDER_NUMBER = 2481
RUSH_HOURS = 24
BASE_REVISIONS = 2


def next_order_id() -> str:
    return f"BMT-{FIRST_ORDER_NUMBER + len(repo.list_orders())}"


@router.post("", status_code=201)
def create_order(body: OrderRequest) -> Order:
    editor = repo.get_editor(body.editor_id)
    package = find_package(editor, body.package_id)
    brief = repo.get_brief(body.brief_id) if body.brief_id else None
    total_usd, total_inr = quote(package, body.addons, body.rush)
    now = datetime.now(UTC)
    order = Order(
        id=next_order_id(), editor_id=editor.id, package_id=package.id,
        brief_id=brief.id if brief else None, brief=brief.result if brief else None,
        title=package.title, g=package.g, addons=list(dict.fromkeys(body.addons)), rush=body.rush,
        note=body.note, total_usd=total_usd, total_inr=total_inr, status="funded",
        revisions_left=BASE_REVISIONS + (1 if "revision" in body.addons else 0),
        due_at=now + timedelta(hours=RUSH_HOURS if body.rush else package.eta_hours),
        timeline=[escrow.event("funded")], created_at=now,
    )
    repo.save("orders", order)
    return order


@router.get("")
def list_orders() -> list[Order]:
    return sorted(repo.list_orders(), key=lambda o: o.created_at, reverse=True)


@router.get("/{order_id}")
def get_order(order_id: str) -> Order:
    return repo.get_order(order_id)


@router.post("/{order_id}/deliver")
def deliver(order_id: str, body: DeliverRequest) -> Order:
    """The editor delivers a cut. In the demo, the client uploads it on the editor's behalf."""
    upload = repo.get_upload(body.cut_upload_id)
    if upload.kind != "cut":
        raise HTTPException(422, "Deliver an upload of kind 'cut', not raw footage.")
    order = escrow.transition(repo.get_order(order_id), "deliver")
    order = order.model_copy(update={"cut_upload_id": upload.id, "review": None, "client_notes": []})
    repo.save("orders", order)
    return order


@router.post("/{order_id}/revisions")
def request_changes(order_id: str) -> Order:
    order = repo.get_order(order_id)
    if order.revisions_left <= 0:
        raise HTTPException(409, "No revisions left on this order.")
    order = escrow.transition(order, "request_changes")
    order = order.model_copy(update={"revisions_left": order.revisions_left - 1})
    repo.save("orders", order)
    return order


@router.post("/{order_id}/notes", status_code=201)
def add_note(order_id: str, body: ClientNote) -> Order:
    """A note the client pins at a moment in the cut."""
    order = repo.get_order(order_id)
    notes = sorted([*order.client_notes, body], key=lambda n: n.t)
    order = order.model_copy(update={"client_notes": notes})
    repo.save("orders", order)
    return order


@router.post("/{order_id}/review")
def review(order_id: str, body: ReviewRequest) -> ReviewResult:
    order = repo.get_order(order_id)
    if order.status != "review" or not order.cut_upload_id:
        raise HTTPException(409, "There is no delivered cut to review yet.")
    result = review_order(order, repo.get_upload(order.cut_upload_id), body.client_feedback)
    repo.save("orders", order.model_copy(update={"review": result}))
    return result


@router.post("/{order_id}/approve")
def approve(order_id: str) -> Order:
    order = escrow.transition(repo.get_order(order_id), "approve")
    order = order.model_copy(update={"payout": create_payout(order.total_usd)})
    repo.save("orders", order)
    return order
