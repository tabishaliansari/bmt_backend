import socket
from functools import lru_cache

from app.config import get_settings
from app.db.base import Database


def require_emulator(host_port: str) -> None:
    """Fail fast with a clear message instead of a 60 s gRPC retry when the emulator is down."""
    host, _, port = host_port.rpartition(":")
    try:
        socket.create_connection((host or "127.0.0.1", int(port)), timeout=2).close()
    except OSError:
        raise SystemExit(
            f"Firestore emulator isn't running on {host_port}. "
            "Start the app with `bash scripts/dev.sh` (it starts the emulators first), "
            "or set DB=sqlite in .env."
        ) from None


@lru_cache
def get_db() -> Database:
    settings = get_settings()
    if settings.db == "firestore":
        from app.db.firestore import FirestoreDatabase

        if settings.firestore_emulator_host:
            require_emulator(settings.firestore_emulator_host)
        return FirestoreDatabase(settings.project_id)
    from app.db.sqlite import SqliteDatabase

    return SqliteDatabase(settings.data_dir / "bmt.db")
