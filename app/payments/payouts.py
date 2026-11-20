"""Simulated money movement: the client's payment into escrow, and the Ramp payout to the
editor in INR at a fixed demo FX rate. Nothing here touches real money or card data."""

import secrets
from datetime import UTC, datetime

from app.config import get_settings
from app.models import Payment, Payout

PAYMENT_METHODS = {"demo_card": "Test card ending 4242", "demo_upi": "Test UPI (demo@bmt)"}


def reference(prefix: str) -> str:
    return f"{prefix}-SIM-{secrets.token_hex(4).upper()}"


def create_payment(method: str, total_usd: float, total_inr: float) -> Payment:
    return Payment(
        method=PAYMENT_METHODS[method], amount_usd=total_usd, amount_inr=total_inr,
        reference=reference("PAY"), at=datetime.now(UTC),
    )


def create_payout(total_usd: float) -> Payout:
    settings = get_settings()
    fee_usd = round(total_usd * settings.platform_fee_pct / 100, 2)
    amount_usd = round(total_usd - fee_usd, 2)
    return Payout(
        amount_usd=amount_usd,
        fx_rate=settings.demo_fx_usd_inr,
        amount_inr=round(amount_usd * settings.demo_fx_usd_inr, 2),
        gross_usd=total_usd, fee_usd=fee_usd, fee_pct=settings.platform_fee_pct,
        transfer_id=reference("RAMP"),
        at=datetime.now(UTC),
    )
