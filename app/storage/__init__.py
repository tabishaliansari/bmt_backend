from functools import lru_cache

from app.config import get_settings
from app.storage.base import Storage


@lru_cache
def get_storage() -> Storage:
    settings = get_settings()
    if settings.storage == "gcs":
        if not settings.gcs_bucket:
            raise RuntimeError("STORAGE=gcs needs GCS_BUCKET")
        from app.storage.gcs import GcsStorage

        return GcsStorage(settings.gcs_bucket, settings.project_id)
    from app.storage.local import LocalStorage

    return LocalStorage(settings.data_dir / "uploads")
