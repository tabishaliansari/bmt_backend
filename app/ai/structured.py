"""One Gemini call that must return JSON matching a Pydantic model."""

import importlib
import logging
import time
from typing import TypeVar

from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

from app.ai.client import get_client
from app.ai.errors import AIError, AITimeout

log = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

ATTEMPTS = 2  # first try + one retry on invalid JSON
OVERLOAD_RETRY_SEC = 3  # wait before retrying a 503 "high demand"


def http_timeout_errors() -> tuple[type[Exception], ...]:
    """Timeout errors of whichever HTTP library google-genai uses (httpx2 in 3.x, else httpx)."""
    found = []
    for name in ("httpx2", "httpx"):
        try:
            found.append(importlib.import_module(name).TimeoutException)
        except ImportError:
            continue
    return tuple(found)


TIMEOUT_ERRORS = http_timeout_errors()


def generate_json(
    model: str, system_prompt: str, contents: list[types.Part], schema: type[T], task: str
) -> T:
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        response_schema=schema,
    )
    for attempt in range(1, ATTEMPTS + 1):
        started = time.monotonic()
        response = call_gemini(model, contents, config)
        log.info("%s: %s answered in %.1fs (attempt %d)", task, model, time.monotonic() - started, attempt)
        try:
            return parse(response, schema)
        except (ValidationError, ValueError):
            log.warning("%s: invalid JSON from %s (attempt %d)", task, model, attempt)
    raise AIError("Gemini returned an answer we couldn't read. Please try again.")


def call_gemini(
    model: str, contents: list[types.Part], config: types.GenerateContentConfig,
    client: genai.Client | None = None,
) -> types.GenerateContentResponse:
    for attempt in range(2):
        try:
            return (client or get_client()).models.generate_content(model=model, contents=contents, config=config)
        except TIMEOUT_ERRORS as exc:
            raise AITimeout("Gemini took too long to answer. Try a shorter clip.") from exc
        except errors.APIError as exc:
            log.warning("Gemini API error %s: %s", exc.code, exc.message)
            if exc.code == 503 and attempt == 0:
                time.sleep(OVERLOAD_RETRY_SEC)  # "high demand" spikes are usually brief: one retry
                continue
            if exc.code in (429, 503):
                raise AIError("Gemini is busy right now. Please try again in a minute.") from exc
            raise AIError(f"Gemini couldn't process this request ({exc.code}). Try a shorter MP4 under 50 MB.") from exc
    raise AssertionError("unreachable")


def parse(response: types.GenerateContentResponse, schema: type[T]) -> T:
    if isinstance(response.parsed, schema):
        return response.parsed
    if not response.text:
        raise ValueError("empty response")
    return schema.model_validate_json(response.text)
