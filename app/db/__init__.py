from functools import lru_cache

from app.config import get_settings
from app.db.base import Database


@lru_cache
def get_db() -> Database:
    settings = get_settings()
    if settings.db == "sqlite":
        from app.db.sqlite import SqliteDatabase

        return SqliteDatabase(settings.data_dir / "bmt.db")
    raise NotImplementedError("DB=firestore is not available yet (Phase 8)")
