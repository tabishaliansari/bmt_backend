import mimetypes
import secrets
from datetime import UTC, datetime
from pathlib import PurePath
from typing import BinaryIO, Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.responses import Response

from app import links, repo
from app.auth import UserId
from app.config import get_settings
from app.models import Upload, UploadKind, UploadOut
from app.storage import get_storage

router = APIRouter(prefix="/uploads", tags=["uploads"])


def video_mime(file: UploadFile) -> str:
    """The file's video MIME type, from the request or its extension; 415 if not a video."""
    mime = file.content_type or ""
    if not mime.startswith("video/"):
        mime = mimetypes.guess_type(file.filename or "")[0] or ""
    if not mime.startswith("video/"):
        raise HTTPException(415, "Only video files can be uploaded (for example MP4 or MOV).")
    return mime


def measured_size(src: BinaryIO) -> int:
    """Size from the received bytes themselves, never trusted from the request."""
    src.seek(0, 2)
    size = src.tell()
    src.seek(0)
    return size


def store_upload(owner: str, kind: UploadKind, filename: str, mime: str, src: BinaryIO, size: int) -> Upload:
    upload_id = f"up_{secrets.token_hex(8)}"
    storage_path = get_storage().save(upload_id + PurePath(filename).suffix.lower(), src)
    upload = Upload(
        id=upload_id, owner=owner, kind=kind, filename=filename, mime=mime, size=size,
        storage_path=storage_path, created_at=datetime.now(UTC),
    )
    repo.save("uploads", upload)
    return upload


@router.post("", status_code=201)
def create_upload(
    uid: UserId, file: UploadFile = File(...), kind: Literal["raw", "cut"] = Form(...)
) -> UploadOut:
    max_mb = get_settings().max_upload_mb
    mime = video_mime(file)
    size = measured_size(file.file)
    if size > max_mb * 1024 * 1024:
        raise HTTPException(413, f"File is too large. The limit is {max_mb} MB.")
    filename = PurePath(file.filename or "video").name
    upload = store_upload(uid, kind, filename, mime, file.file, size)
    return UploadOut.model_validate(upload.model_dump())


@router.get("/{upload_id}/url")
def get_media_url(upload_id: str, uid: UserId) -> dict:
    """A short-lived link the owner's browser can put straight into <video> or <img>."""
    repo.get_upload(upload_id, owner=uid)
    return {"url": links.media_url(upload_id)}


@router.get("/{upload_id}/content")
def get_upload_content(upload_id: str, exp: int = 0, sig: str = "") -> Response:
    """Streams the file (supports Range for seeking). Needs a valid signed link."""
    if not links.is_valid(upload_id, exp, sig):
        raise HTTPException(403, "This media link has expired. Reload the page to get a new one.")
    upload = repo.get_upload(upload_id, owner=None)
    return get_storage().media_response(upload.storage_path, upload.mime)
