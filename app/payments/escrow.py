"""Simulated escrow: the only place an order's status changes.

funded -> in_progress (editor accepts) -> review (cut delivered) -> approved (payout created)
review -> in_progress -> review (client asked for changes)
funded -> refunded (editor declines; or a missed deadline, simulated)
"""

from datetime import UTC, datetime
from typing import Literal

from fastapi import HTTPException

from app.models import Order, OrderStatus, TimelineEvent

Action = Literal["accept", "decline", "cancel", "deliver", "request_changes", "approve", "refund"]

TRANSITIONS: dict[Action, tuple[set[OrderStatus], OrderStatus]] = {
    "accept": ({"funded"}, "in_progress"),
    "decline": ({"funded"}, "refunded"),
    "cancel": ({"funded"}, "refunded"),  # client, only before the editor accepts
    "deliver": ({"funded", "in_progress"}, "review"),
    "request_changes": ({"review"}, "in_progress"),
    "approve": ({"review"}, "approved"),
    "refund": ({"funded", "in_progress"}, "refunded"),
}

LABELS: dict[str, str] = {
    "funded": "Payment held safely",
    "accept": "Editor accepted and started editing",
    "decline": "Editor declined, payment refunded to you",
    "cancel": "You cancelled, payment refunded to you",
    "deliver": "Cut delivered for your review",
    "request_changes": "Editor is working on your notes",
    "approve": "Approved, payment released to the editor",
    "refund": "Refunded to you",
}

CODES: dict[str, str] = {
    "funded": "funded", "accept": "accepted", "decline": "declined", "cancel": "cancelled", "deliver": "delivered",
    "request_changes": "changes", "approve": "approved", "refund": "refunded",
}


def event(key: str, status: OrderStatus) -> TimelineEvent:
    return TimelineEvent(status=status, at=datetime.now(UTC), label=LABELS[key], code=CODES[key])


def funded_event() -> TimelineEvent:
    return event("funded", "funded")


def is_accepted(order: Order) -> bool:
    return any(e.code == "accepted" for e in order.timeline)


def transition(order: Order, action: Action) -> Order:
    allowed_from, to = TRANSITIONS[action]
    if order.status not in allowed_from:
        raise HTTPException(409, f"Can't {action.replace('_', ' ')} an order that is '{order.status}'.")
    update: dict = {"status": to, "timeline": [*order.timeline, event(action, to)]}
    if order.payment and action in ("decline", "cancel", "refund"):
        update["payment"] = order.payment.model_copy(update={"status": "refunded"})
    if order.payment and action == "approve":
        update["payment"] = order.payment.model_copy(update={"status": "released"})
    return order.model_copy(update=update)
