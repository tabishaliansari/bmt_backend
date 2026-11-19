"""SQLite implementation of the Database interface (local mode)."""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS docs (
    collection TEXT NOT NULL,
    id         TEXT NOT NULL,
    data       TEXT NOT NULL,
    PRIMARY KEY (collection, id)
)
"""


class SqliteDatabase:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def put(self, collection: str, doc_id: str, data: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO docs (collection, id, data) VALUES (?, ?, ?) "
                "ON CONFLICT (collection, id) DO UPDATE SET data = excluded.data",
                (collection, doc_id, json.dumps(data)),
            )

    def get(self, collection: str, doc_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT data FROM docs WHERE collection = ? AND id = ?", (collection, doc_id)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def list(self, collection: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT data FROM docs WHERE collection = ? ORDER BY rowid", (collection,)
            ).fetchall()
        return [json.loads(r[0]) for r in rows]
