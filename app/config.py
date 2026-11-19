"""App settings, read from environment variables (and backend/.env when present)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # AI
    gemini_api_key: str = ""
    gemini_fast_model: str = ""
    gemini_pro_model: str = ""
    use_vertex: bool = False
    gcp_project: str = ""
    vertex_location: str = "us-central1"
    ai_timeout_sec: int = 90
    inline_video_max_mb: int = 15

    # Storage and database
    storage: Literal["local", "gcs"] = "local"
    db: Literal["sqlite", "firestore"] = "sqlite"
    gcs_bucket: str = ""
    data_dir: Path = BACKEND_DIR / "data"

    # Uploads, money
    max_upload_mb: int = 50
    platform_fee_pct: float = 15.0
    demo_fx_usd_inr: float = 84.10

    # Static frontend served at "/"
    frontend_dir: Path = BACKEND_DIR.parent / "frontend"

    @property
    def ai_mode(self) -> Literal["gemini-api", "vertex"]:
        return "vertex" if self.use_vertex else "gemini-api"


@lru_cache
def get_settings() -> Settings:
    return Settings()
