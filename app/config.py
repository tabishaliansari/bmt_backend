"""App settings, read from environment variables (and backend/.env when present)."""

import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEMO_PROJECT = "demo-bmt"  # emulator-only project id; "demo-" projects never touch real GCP


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
    gemini_screen_model: str = ""  # Gemma: screens what people type; empty = no screening
    gemini_image_model: str = ""  # Nano Banana: thumbnail concepts; empty = feature off
    use_vertex: bool = False
    gcp_project: str = ""
    vertex_location: str = "us-central1"
    ai_timeout_sec: int = 90
    inline_video_max_mb: int = 15
    ai_rate_limit_per_hour: int = 30  # Gemini calls per signed-in user per hour

    # Storage and database
    storage: Literal["local", "gcs"] = "local"
    db: Literal["sqlite", "firestore"] = "sqlite"
    gcs_bucket: str = ""
    data_dir: Path = BACKEND_DIR / "data"
    firestore_emulator_host: str = ""  # e.g. localhost:8081; empty = real Firestore

    # Auth (Firebase Authentication, Google sign-in)
    auth: Literal["firebase", "off"] = "firebase"
    firebase_api_key: str = ""  # web API key from the Firebase console; any value with the emulator
    firebase_auth_domain: str = ""  # defaults to <project>.firebaseapp.com
    firebase_auth_emulator_host: str = ""  # e.g. localhost:9099; empty = real Firebase Auth

    # Uploads, money, media links
    max_upload_mb: int = 50
    platform_fee_pct: float = 15.0
    demo_fx_usd_inr: float = 84.10
    media_signing_key: str = Field(default_factory=lambda: secrets.token_hex(32))
    media_url_ttl_sec: int = 3600

    # Static frontend served at "/"
    frontend_dir: Path = BACKEND_DIR.parent / "frontend"

    @property
    def ai_mode(self) -> Literal["gemini-api", "vertex"]:
        return "vertex" if self.use_vertex else "gemini-api"

    @property
    def project_id(self) -> str:
        return self.gcp_project or DEMO_PROJECT

    @property
    def auth_domain(self) -> str:
        return self.firebase_auth_domain or f"{self.project_id}.firebaseapp.com"

    def export_emulator_env(self) -> None:
        """Google client libraries read emulator hosts from the process environment."""
        if self.firestore_emulator_host:
            os.environ.setdefault("FIRESTORE_EMULATOR_HOST", self.firestore_emulator_host)
        if self.firebase_auth_emulator_host:
            os.environ.setdefault("FIREBASE_AUTH_EMULATOR_HOST", self.firebase_auth_emulator_host)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.export_emulator_env()
    return settings
