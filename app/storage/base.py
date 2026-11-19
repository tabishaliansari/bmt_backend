"""Storage interface for uploaded videos (local disk now, Cloud Storage later)."""

from typing import BinaryIO, Protocol


class Storage(Protocol):
    def save(self, key: str, src: BinaryIO) -> str:
        """Store the stream under `key` and return its storage path."""

    def read(self, storage_path: str) -> bytes:
        """Return the stored file's bytes."""
