"""Local-disk implementation of the Storage interface."""

import shutil
from pathlib import Path
from typing import BinaryIO


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
