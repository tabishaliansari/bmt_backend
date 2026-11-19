import mimetypes
import secrets
from datetime import UTC, datetime
from pathlib import PurePath

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.responses import Response

from app import repo
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


@router.post("", status_code=201)
def create_upload(file: UploadFile = File(...), kind: UploadKind = Form(...)) -> UploadOut:
    max_mb = get_settings().max_upload_mb
    mime = video_mime(file)
    if file.size is not None and file.size > max_mb * 1024 * 1024:
        raise HTTPException(413, f"File is too large. The limit is {max_mb} MB.")

    upload_id = f"up_{secrets.token_hex(4)}"
    filename = PurePath(file.filename or "video").name
    storage_path = get_storage().save(upload_id + PurePath(filename).suffix.lower(), file.file)
    upload = Upload(
        id=upload_id, kind=kind, filename=filename, mime=mime, size=file.size or 0,
        storage_path=storage_path, created_at=datetime.now(UTC),
    )
    repo.save("uploads", upload)
    return UploadOut.model_validate(upload.model_dump())


@router.get("/{upload_id}/content")
def get_upload_content(upload_id: str) -> Response:
    """Streams the video so the review player can play and seek it."""
    upload = repo.get_upload(upload_id)
    return get_storage().media_response(upload.storage_path, upload.mime)
