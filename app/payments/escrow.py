"""Simulated escrow: the only place an order's status changes.

funded -> review -> approved (payout created)
review -> in_progress -> review (client asked for changes)
funded | in_progress -> refunded (missed deadline, simulated)
"""

from datetime import UTC, datetime
from typing import Literal

from fastapi import HTTPException

from app.models import Order, OrderStatus, TimelineEvent

Action = Literal["deliver", "request_changes", "approve", "refund"]

TRANSITIONS: dict[Action, tuple[set[OrderStatus], OrderStatus]] = {
    "deliver": ({"funded", "in_progress"}, "review"),
    "request_changes": ({"review"}, "in_progress"),
    "approve": ({"review"}, "approved"),
    "refund": ({"funded", "in_progress"}, "refunded"),
}

LABELS: dict[OrderStatus, str] = {
    "funded": "Payment held safely",
    "in_progress": "Editor is working on your notes",
    "review": "Cut delivered for your review",
    "approved": "Approved, payment released to the editor",
    "refunded": "Refunded to you",
}


def event(status: OrderStatus) -> TimelineEvent:
    return TimelineEvent(status=status, at=datetime.now(UTC), label=LABELS[status])


def transition(order: Order, action: Action) -> Order:
    allowed_from, to = TRANSITIONS[action]
    if order.status not in allowed_from:
        raise HTTPException(409, f"Can't {action.replace('_', ' ')} an order that is '{order.status}'.")
    return order.model_copy(update={"status": to, "timeline": [*order.timeline, event(to)]})
