"""Nano Banana drafts a thumbnail concept from the brief (image generation, no structured output)."""

import logging

from google.genai import types

from app.ai.client import require_model
from app.ai.errors import AIError
from app.ai.prompts import load_prompt
from app.ai.structured import call_gemini
from app.config import get_settings
from app.models import BriefResult

log = logging.getLogger(__name__)

VERTICAL_FORMATS = {"reel", "shorts", "podcast_clips"}

# Second try when the first comes back without an image (usually a safety filter on people):
# no people at all, and allow a text part alongside the image.
SAFER = (
    "\n- Show no people at all: no faces, hands or bodies. Use the place, food, product or object "
    "from the hook instead, as a stylised illustration."
)


def first_image(response: types.GenerateContentResponse) -> tuple[bytes, str] | None:
    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else None) or []:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data, part.inline_data.mime_type or "image/png"
    return None


def why_no_image(response: types.GenerateContentResponse) -> str:
    """Finish/block reasons only (no prompt or user text in the logs)."""
    finish = [str(c.finish_reason) for c in response.candidates or []]
    blocked = response.prompt_feedback.block_reason if response.prompt_feedback else None
    has_text = bool((response.text or "").strip()) if response.candidates else False
    return f"finish={finish} block={blocked} text_only={has_text}"


def draft_thumbnail(result: BriefResult) -> tuple[bytes, str]:
    """Returns (image bytes, mime type)."""
    model = require_model(get_settings().gemini_image_model, "GEMINI_IMAGE_MODEL")
    vertical = result.format in VERTICAL_FORMATS
    prompt = load_prompt("thumbnail").format(
        title=result.title, format=result.format, hook=result.hook_idea, style=result.style_notes,
        must_include=", ".join(result.must_include) or "nothing specific",
        aspect="Vertical 9:16" if vertical else "Horizontal 16:9",
    )
    image_config = types.ImageConfig(aspect_ratio="9:16" if vertical else "16:9")
    attempts = [(prompt, ["IMAGE"]), (prompt + SAFER, ["TEXT", "IMAGE"])]
    for text, modalities in attempts:
        config = types.GenerateContentConfig(response_modalities=modalities, image_config=image_config)
        response = call_gemini(model, [types.Part.from_text(text=text)], config)
        image = first_image(response)
        if image:
            return image
        log.warning("Nano Banana returned no image: %s", why_no_image(response))
    raise AIError("Nano Banana didn't return an image this time. Please try again.")
