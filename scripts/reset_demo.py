"""Restore the clean demo state: no orders, briefs or uploads; editors freshly seeded.

Works against whatever .env points at (SQLite or Firestore, local disk or Cloud Storage).
Run from backend/:  .venv/bin/python scripts/reset_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.db import get_db  # noqa: E402
from app.seed import seed  # noqa: E402
from app.storage import get_storage  # noqa: E402


def main() -> None:
    settings = get_settings()
    db, storage = get_db(), get_storage()
    files = 0
    for upload in db.list("uploads"):
        storage.delete(upload["storage_path"])
        files += 1
    # Profiles (roles, seen intros) are kept on purpose: a reset shouldn't sign anyone out.
    counts = {name: db.delete_all(name) for name in ("orders", "briefs", "uploads", "editors")}
    seed(db)
    print(f"Reset {settings.db}/{settings.storage}: removed {counts} and {files} stored files; editors re-seeded.")


if __name__ == "__main__":
    main()
