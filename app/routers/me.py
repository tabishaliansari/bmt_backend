"""The signed-in user's profile: role (client or editor), which intros they've seen, display settings."""

from datetime import UTC, datetime

from fastapi import APIRouter

from app import repo
from app.auth import CurrentIdentity
from app.config import get_settings
from app.db import get_db
from app.models import ProfileUpdate, UserProfile

router = APIRouter(prefix="/me", tags=["me"])


def load_profile(identity: CurrentIdentity) -> UserProfile:
    """Created on first sight. The editor link always follows EDITOR_ACCOUNTS (server config)."""
    data = get_db().get("users", identity.uid)
    profile = (
        UserProfile.model_validate(data) if data
        else UserProfile(id=identity.uid, created_at=datetime.now(UTC))
    )
    editor_id = get_settings().editor_for_email(identity.email) if identity.email else None
    return profile.model_copy(update={
        "email": identity.email or profile.email, "name": identity.name or profile.name, "editor_id": editor_id,
    })


@router.get("")
def get_me(identity: CurrentIdentity) -> UserProfile:
    profile = load_profile(identity)
    repo.save("users", profile)
    return profile


@router.put("")
def update_me(body: ProfileUpdate, identity: CurrentIdentity) -> UserProfile:
    profile = load_profile(identity)
    update: dict = {}
    if body.role:
        update["role"] = body.role
    if body.onboarded_role:
        update["onboarded"] = {**profile.onboarded, body.onboarded_role: True}
    if body.a11y:
        update["a11y"] = body.a11y
    profile = profile.model_copy(update=update)
    repo.save("users", profile)
    return profile
