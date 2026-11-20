"""Brief Builder: Gemini watches the client's raw clips (and any references) and writes a structured brief."""

import logging

from google.genai import types

from app.ai.client import require_model
from app.ai.errors import AIConfigError, AIError, AITimeout
from app.ai.media import video_part
from app.ai.prompts import load_prompt
from app.ai.references import has_watched_links, reference_parts
from app.ai.structured import generate_json
from app.config import get_settings
from app.models import BriefResult, Upload

log = logging.getLogger(__name__)


def brief_contents(uploads: list[Upload], client_note: str, refs: list[types.Part]) -> list[types.Part]:
    contents: list[types.Part] = []
    for upload in uploads:
        contents.append(types.Part.from_text(text=f"Clip {upload.id} ({upload.filename})"))
        contents.append(video_part(upload))
    contents.extend(refs)
    note = client_note.strip() or "(no note given)"
    contents.append(types.Part.from_text(text=f"Client note: {note}"))
    return contents


def build_brief(
    uploads: list[Upload], client_note: str, ref_uploads: list[Upload] | None = None, links: list[str] | None = None,
) -> BriefResult:
    model = require_model(get_settings().gemini_fast_model, "GEMINI_FAST_MODEL")
    ref_uploads, links = ref_uploads or [], links or []
    prompt = load_prompt("brief_builder")

    def run(watch_links: bool) -> BriefResult:
        refs = reference_parts(ref_uploads, links, watch_links=watch_links)
        return generate_json(model, prompt, brief_contents(uploads, client_note, refs), BriefResult, task="brief")

    try:
        return run(watch_links=True)
    except (AITimeout, AIConfigError):
        raise
    except AIError as err:
        status = getattr(err.__cause__, "code", None)
        if not has_watched_links(links) or not isinstance(status, int) or status >= 500:
            raise  # overloaded or unreadable output: not the link's fault, so don't retry without it
        # A private, removed or region-locked YouTube video fails the whole call: retry with links as text.
        log.warning("brief with watched YouTube references failed; retrying with links as text")
        return run(watch_links=False)
