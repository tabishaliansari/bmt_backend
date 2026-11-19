"""Server-side pricing. The client never sends a price; totals are computed here."""

from fastapi import HTTPException

from app.models import Editor, Package
from app.seed import CATALOG


def find_package(editor: Editor, package_id: str) -> Package:
    for package in editor.packages:
        if package.id == package_id:
            return package
    raise HTTPException(404, f"{editor.name} has no package '{package_id}'")


def quote(package: Package, addon_ids: list[str], rush: bool) -> tuple[float, float]:
    """Total as (usd, inr) for a package plus add-ons and the optional rush fee."""
    by_id = {a.id: a for a in CATALOG.addons}
    unknown = [a for a in addon_ids if a not in by_id]
    if unknown:
        raise HTTPException(422, f"Unknown add-on: {', '.join(unknown)}")
    chosen = [by_id[a] for a in dict.fromkeys(addon_ids)]
    usd = package.price_usd + sum(a.price_usd for a in chosen)
    inr = package.price_inr + sum(a.price_inr for a in chosen)
    if rush:
        usd += CATALOG.rush_fee_usd
        inr += CATALOG.rush_fee_inr
    return round(usd, 2), round(inr, 2)
