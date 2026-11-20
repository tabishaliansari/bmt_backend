"""Turns a stored upload into a Gemini Part: inline for small clips, Files API for larger ones."""

import io
import time

from google.genai import types

from app.ai.client import get_client
from app.ai.errors import AIError
from app.config import get_settings
from app.models import Upload
from app.storage import get_storage

FILE_POLL_SEC = 2


def video_part(upload: Upload) -> types.Part:
    """Small clips inline; larger ones as gs:// on Vertex, or via the Files API otherwise."""
    settings = get_settings()
    storage = get_storage()
    if upload.size > settings.inline_video_max_mb * 1024 * 1024:
        if settings.use_vertex:
            gcs_uri = getattr(storage, "gcs_uri", None)
            if gcs_uri is None:
                raise AIError("This clip is too large to send inline. Try a shorter clip.")
            return types.Part.from_uri(file_uri=gcs_uri(upload.storage_path), mime_type=upload.mime)
        return uploaded_file_part(storage.read(upload.storage_path), upload.mime)
    return types.Part.from_bytes(data=storage.read(upload.storage_path), mime_type=upload.mime)


def uploaded_file_part(data: bytes, mime: str) -> types.Part:
    """Upload to the Gemini Files API and wait until the file is ready to use."""
    client = get_client()
    file = client.files.upload(file=io.BytesIO(data), config=types.UploadFileConfig(mime_type=mime))
    deadline = time.monotonic() + get_settings().ai_timeout_sec
    while file.state == types.FileState.PROCESSING:
        if time.monotonic() > deadline:
            raise AIError("Gemini took too long to process this clip. Try a shorter one.")
        time.sleep(FILE_POLL_SEC)
        file = client.files.get(name=file.name)
    if file.state != types.FileState.ACTIVE:
        raise AIError("Gemini couldn't read this clip. Try a shorter MP4 under 50 MB.")
    return types.Part.from_uri(file_uri=file.uri, mime_type=file.mime_type or mime)
