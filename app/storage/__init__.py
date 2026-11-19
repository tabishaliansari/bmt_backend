from functools import lru_cache

from app.config import get_settings
from app.storage.base import Storage


@lru_cache
def get_storage() -> Storage:
    settings = get_settings()
    if settings.storage == "local":
        from app.storage.local import LocalStorage

        return LocalStorage(settings.data_dir / "uploads")
    raise NotImplementedError("STORAGE=gcs is not available yet (Phase 8)")
