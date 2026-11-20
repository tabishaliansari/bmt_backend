from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict:
    """Shows judges what is running: the mode of each service and which model does which job."""
    s = get_settings()
    return {
        "ok": True,
        "mode": {"ai": s.ai_mode, "storage": s.storage, "db": s.db, "auth": s.auth},
        "models": {
            "brief": s.gemini_fast_model or None,
            "review": s.gemini_pro_model or None,
            "feedback": s.gemini_fast_model or None,
            "screening": s.gemini_screen_model or None,
            "thumbnail": s.gemini_image_model or None,
        },
    }


@router.get("/config")
def public_config() -> dict:
    """What the browser needs to start Firebase sign-in. All of it is public by design."""
    s = get_settings()
    emulator = s.firebase_auth_emulator_host
    return {
        "auth": s.auth,
        "firebase": {"apiKey": s.firebase_api_key or "demo-key", "authDomain": s.auth_domain, "projectId": s.project_id},
        "authEmulator": f"http://{emulator}" if emulator else None,
        "features": {"thumbnail": bool(s.gemini_image_model), "screening": bool(s.gemini_screen_model)},
    }
