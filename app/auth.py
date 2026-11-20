"""Firebase Authentication: verifies the ID token on each request and returns the user's uid.

With AUTH=off (local development only) every request is the same fixed local user.
"""

import logging
from functools import lru_cache
from typing import Annotated

import firebase_admin
from fastapi import Depends, Header, HTTPException
from firebase_admin import auth as fb_auth

from app.config import get_settings

log = logging.getLogger(__name__)

LOCAL_USER = "local-dev"


@lru_cache
def firebase_app() -> firebase_admin.App:
    return firebase_admin.initialize_app(options={"projectId": get_settings().project_id})


def current_user(authorization: str | None = Header(default=None)) -> str:
    if get_settings().auth == "off":
        return LOCAL_USER
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Please sign in to continue.")
    try:
        claims = fb_auth.verify_id_token(authorization.removeprefix("Bearer "), app=firebase_app())
    except Exception as exc:  # any verification failure means "not signed in"
        log.info("Rejected ID token: %s", type(exc).__name__)
        raise HTTPException(401, "Your sign-in has expired. Please sign in again.") from exc
    return claims["uid"]


UserId = Annotated[str, Depends(current_user)]
