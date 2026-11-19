"""Database interface: JSON documents grouped into collections (maps 1:1 to Firestore)."""

from typing import Protocol


class Database(Protocol):
    def put(self, collection: str, doc_id: str, data: dict) -> None:
        """Insert or replace a document."""

    def get(self, collection: str, doc_id: str) -> dict | None:
        """Return the document, or None if it does not exist."""

    def list(self, collection: str) -> list[dict]:
        """Return every document in the collection, oldest first."""
