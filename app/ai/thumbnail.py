"""Nano Banana drafts a thumbnail concept from the brief (image generation, no structured output)."""

from google.genai import types

from app.ai.client import require_model
from app.ai.errors import AIError
from app.ai.prompts import load_prompt
from app.ai.structured import call_gemini
from app.config import get_settings
from app.models import BriefResult

VERTICAL_FORMATS = {"reel", "shorts", "podcast_clips"}


def draft_thumbnail(result: BriefResult) -> tuple[bytes, str]:
    """Returns (image bytes, mime type)."""
    model = require_model(get_settings().gemini_image_model, "GEMINI_IMAGE_MODEL")
    vertical = result.format in VERTICAL_FORMATS
    prompt = load_prompt("thumbnail").format(
        title=result.title, format=result.format, hook=result.hook_idea, style=result.style_notes,
        must_include=", ".join(result.must_include) or "nothing specific",
        aspect="Vertical 9:16" if vertical else "Horizontal 16:9",
    )
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="9:16" if vertical else "16:9"),
    )
    response = call_gemini(model, [types.Part.from_text(text=prompt)], config)
    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else None) or []:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data, part.inline_data.mime_type or "image/png"
    raise AIError("Nano Banana didn't return an image this time. Please try again.")
