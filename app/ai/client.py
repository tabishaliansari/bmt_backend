"""Gemini client factory: Developer API (local) or Vertex AI (cloud), chosen by USE_VERTEX."""

from functools import lru_cache

from google import genai
from google.genai import types

from app.ai.errors import AIConfigError
from app.config import get_settings


@lru_cache
def get_client() -> genai.Client:
    settings = get_settings()
    http_options = types.HttpOptions(timeout=settings.ai_timeout_sec * 1000)
    if settings.use_vertex:
        if not settings.gcp_project:
            raise AIConfigError("GCP_PROJECT is not set, so Vertex AI can't be used.")
        return genai.Client(
            vertexai=True, project=settings.gcp_project,
            location=settings.vertex_location, http_options=http_options,
        )
    if not settings.gemini_api_key:
        raise AIConfigError("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=settings.gemini_api_key, http_options=http_options)


def require_model(model: str, env_name: str) -> str:
    if not model:
        raise AIConfigError(f"{env_name} is not set.")
    return model
