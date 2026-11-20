"""Cloud Storage implementation of the Storage interface (cloud mode).

Playback: the file is cached once in the instance's /tmp and served with FileResponse, which
handles Range requests (seeking). Demo files are small (Cloud Run caps uploads at 32 MB), so
this avoids signed-URL key setup on Cloud Run.
"""

from pathlib import Path
from typing import BinaryIO

from google.cloud import storage
from starlette.responses import FileResponse, Response

CACHE_DIR = Path("/tmp/bmt-media")


class GcsStorage:
    def __init__(self, bucket: str, project: str) -> None:
        self.bucket_name = bucket
        self.bucket = storage.Client(project=project).bucket(bucket)

    def save(self, key: str, src: BinaryIO) -> str:
        src.seek(0)
        self.bucket.blob(key).upload_from_file(src)
        return key

    def read(self, storage_path: str) -> bytes:
        return self.bucket.blob(storage_path).download_as_bytes()

    def gcs_uri(self, storage_path: str) -> str:
        """For Gemini on Vertex AI, which reads gs:// files directly."""
        return f"gs://{self.bucket_name}/{storage_path}"

    def media_response(self, storage_path: str, mime: str) -> Response:
        cached = CACHE_DIR / storage_path
        if not cached.exists():
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            self.bucket.blob(storage_path).download_to_filename(cached)
        return FileResponse(cached, media_type=mime)

    def delete(self, storage_path: str) -> None:
        blob = self.bucket.blob(storage_path)
        if blob.exists():
            blob.delete()
        (CACHE_DIR / storage_path).unlink(missing_ok=True)
