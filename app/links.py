"""Signed, expiring links to stored media. A <video> or <img> tag can't send an auth header,
so the owner asks for a link (authenticated) and the link itself carries the proof."""

import hashlib
import hmac
import time

from app.config import get_settings


def _signature(upload_id: str, expires: int) -> str:
    key = get_settings().media_signing_key.encode()
    return hmac.new(key, f"{upload_id}:{expires}".encode(), hashlib.sha256).hexdigest()[:32]


def media_url(upload_id: str) -> str:
    expires = int(time.time()) + get_settings().media_url_ttl_sec
    return f"/api/v1/uploads/{upload_id}/content?exp={expires}&sig={_signature(upload_id, expires)}"


def is_valid(upload_id: str, expires: int, sig: str) -> bool:
    return expires >= time.time() and hmac.compare_digest(sig, _signature(upload_id, expires))
