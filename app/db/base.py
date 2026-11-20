"""Database interface: JSON documents grouped into collections (maps 1:1 to Firestore)."""

from typing import Protocol


class Database(Protocol):
    def put(self, collection: str, doc_id: str, data: dict) -> None:
        """Insert or replace a document."""

    def get(self, collection: str, doc_id: str) -> dict | None:
        """Return the document, or None if it does not exist."""

    def list(self, collection: str, **equals: str) -> list[dict]:
        """Return the collection's documents whose fields equal the given values.
        Order is not guaranteed; callers sort what they show."""

    def delete_all(self, collection: str) -> int:
        """Delete every document in the collection (demo reset). Returns how many."""
