"""Local-disk implementation of the Storage interface."""

import shutil
from pathlib import Path
from typing import BinaryIO

from starlette.responses import FileResponse, Response


class LocalStorage:
    def __init__(self, root: Path) -> None:
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, src: BinaryIO) -> str:
        with open(self.root / key, "wb") as dst:
            shutil.copyfileobj(src, dst)
        return key

    def read(self, storage_path: str) -> bytes:
        return (self.root / storage_path).read_bytes()

    def media_response(self, storage_path: str, mime: str) -> Response:
        return FileResponse(self.root / storage_path, media_type=mime)

    def delete(self, storage_path: str) -> None:
        (self.root / storage_path).unlink(missing_ok=True)
