"""Brief Builder: Gemini watches the client's raw clips and writes a structured brief."""

from google.genai import types

from app.ai.client import require_model
from app.ai.media import video_part
from app.ai.prompts import load_prompt
from app.ai.structured import generate_json
from app.config import get_settings
from app.models import BriefResult, Upload


def build_brief(uploads: list[Upload], client_note: str) -> BriefResult:
    model = require_model(get_settings().gemini_fast_model, "GEMINI_FAST_MODEL")
    contents: list[types.Part] = []
    for upload in uploads:
        contents.append(types.Part.from_text(text=f"Clip {upload.id} ({upload.filename})"))
        contents.append(video_part(upload))
    note = client_note.strip() or "(no note given)"
    contents.append(types.Part.from_text(text=f"Client note: {note}"))
    return generate_json(model, load_prompt("brief_builder"), contents, BriefResult, task="brief")
