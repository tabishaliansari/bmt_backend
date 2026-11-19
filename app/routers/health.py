from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict:
    settings = get_settings()
    return {
        "ok": True,
        "mode": {"ai": settings.ai_mode, "storage": settings.storage, "db": settings.db},
    }
