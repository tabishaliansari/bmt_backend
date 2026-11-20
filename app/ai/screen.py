"""Gemma screens what people type (the client's note, review feedback) before it reaches Gemini.

Gemma on the Gemini API has no JSON mode or system instructions, so the prompt asks for a
single line ("ALLOW" or "BLOCK: <reason>") that is parsed here. Screening fails open: if Gemma
is unavailable, the text goes through and the failure is logged, so the demo path never breaks.
"""

import logging

from google.genai import types

from app.ai.errors import AIError
from app.ai.prompts import load_prompt
from app.ai.structured import call_gemini
from app.config import get_settings
from app.models import ScreenResult

log = logging.getLogger(__name__)


def parse_verdict(answer: str) -> ScreenResult:
    line = answer.strip().splitlines()[0].strip() if answer.strip() else ""
    if line.upper().startswith("BLOCK"):
        reason = line.split(":", 1)[1].strip() if ":" in line else ""
        return ScreenResult(allowed=False, reason=reason or "This text can't be used.")
    return ScreenResult(allowed=True)


def screen_text(text: str) -> tuple[ScreenResult, str | None]:
    """Returns the verdict and the Gemma model that produced it (None when not screened)."""
    model = get_settings().gemini_screen_model
    if not model or not text.strip():
        return ScreenResult(allowed=True), None
    contents = [types.Part.from_text(text=f"{load_prompt('screen')}\n\nText to check:\n{text.strip()}")]
    try:
        response = call_gemini(model, contents, types.GenerateContentConfig(temperature=0))
    except AIError as exc:
        log.warning("Gemma screening skipped: %s", type(exc).__name__)
        return ScreenResult(allowed=True), None
    return parse_verdict(response.text or ""), model
