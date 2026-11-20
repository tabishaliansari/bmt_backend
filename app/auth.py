"""Firebase Authentication: verifies the ID token on each request and returns the user's uid.

With AUTH=off (local development only) every request is the same fixed local user.
"""

import logging
from functools import lru_cache
from typing import Annotated

import firebase_admin
from fastapi import Depends, Header, HTTPException
from firebase_admin import auth as fb_auth
from pydantic import BaseModel

from app.config import get_settings

log = logging.getLogger(__name__)

LOCAL_USER = "local-dev"


@lru_cache
def firebase_app() -> firebase_admin.App:
    return firebase_admin.initialize_app(options={"projectId": get_settings().project_id})


class Identity(BaseModel):
    uid: str
    email: str = ""
    name: str = ""


def current_identity(authorization: str | None = Header(default=None)) -> Identity:
    if get_settings().auth == "off":
        return Identity(uid=LOCAL_USER, name="Local user")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Please sign in to continue.")
    try:
        claims = fb_auth.verify_id_token(authorization.removeprefix("Bearer "), app=firebase_app())
    except Exception as exc:  # any verification failure means "not signed in"
        log.info("Rejected ID token: %s", type(exc).__name__)
        raise HTTPException(401, "Your sign-in has expired. Please sign in again.") from exc
    return Identity(uid=claims["uid"], email=claims.get("email", ""), name=claims.get("name", ""))


def current_user(identity: Annotated[Identity, Depends(current_identity)]) -> str:
    return identity.uid


UserId = Annotated[str, Depends(current_user)]
CurrentIdentity = Annotated[Identity, Depends(current_identity)]
