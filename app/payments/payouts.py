"""Simulated Ramp payout to the editor in INR, at a fixed demo FX rate."""

from datetime import UTC, datetime

from app.config import get_settings
from app.models import Payout


def create_payout(total_usd: float) -> Payout:
    settings = get_settings()
    amount_usd = round(total_usd * (1 - settings.platform_fee_pct / 100), 2)
    return Payout(
        amount_usd=amount_usd,
        fx_rate=settings.demo_fx_usd_inr,
        amount_inr=round(amount_usd * settings.demo_fx_usd_inr, 2),
        at=datetime.now(UTC),
    )
