"""Review Copilot: compares a delivered cut with the brief, and turns vague client feedback
into timestamped notes."""

from google.genai import types

from app.ai.client import require_model
from app.ai.media import video_part
from app.ai.prompts import load_prompt
from app.ai.structured import generate_json
from app.config import get_settings
from app.models import FeedbackAI, Order, ReviewAI, ReviewNote, ReviewNoteAI, ReviewResult, Upload


def brief_context(order: Order) -> str:
    if order.brief:
        return "Brief:\n" + order.brief.model_dump_json(indent=2)
    note = order.note.strip() or "(none)"
    return f"No written brief. Package ordered: {order.title}. Client's note to the editor: {note}"


def cut_parts(order: Order, cut: Upload) -> list[types.Part]:
    return [
        types.Part.from_text(text=brief_context(order)),
        types.Part.from_text(text=f"The editor's cut ({cut.filename}):"),
        video_part(cut),
    ]


def tagged(notes: list[ReviewNoteAI], source: str) -> list[ReviewNote]:
    return [ReviewNote(**n.model_dump(), source=source) for n in notes]


def by_time(notes: list[ReviewNote]) -> list[ReviewNote]:
    return sorted(notes, key=lambda n: n.timestamp_sec)


def fresh_review(order: Order, cut: Upload, keep: list[ReviewNote]) -> ReviewResult:
    model = require_model(get_settings().gemini_pro_model, "GEMINI_PRO_MODEL")
    ai = generate_json(model, load_prompt("review_copilot"), cut_parts(order, cut), ReviewAI, task="review")
    return ReviewResult(
        overall_match=ai.overall_match, summary=ai.summary, checklist=ai.checklist,
        notes=by_time([*tagged(ai.notes, "ai"), *keep]),
    )


def add_feedback_notes(order: Order, cut: Upload, review: ReviewResult, feedback: str) -> ReviewResult:
    model = require_model(get_settings().gemini_fast_model, "GEMINI_FAST_MODEL")
    contents = [
        *cut_parts(order, cut),
        types.Part.from_text(text="Notes already on the cut:\n" + review.model_dump_json(include={"notes"})),
        types.Part.from_text(text=f"Client feedback: {feedback.strip()}"),
    ]
    ai = generate_json(model, load_prompt("feedback_rewriter"), contents, FeedbackAI, task="feedback")
    return review.model_copy(update={"notes": by_time([*review.notes, *tagged(ai.notes, "client")])})


def review_order(order: Order, cut: Upload, feedback: str | None) -> ReviewResult:
    """No feedback: (re)run the AI review, keeping notes that came from the client.
    Feedback: rewrite it into notes, running the AI review first if there is none yet."""
    review = order.review
    if review is None or not feedback:
        keep = [n for n in review.notes if n.source == "client"] if review else []
        review = fresh_review(order, cut, keep)
    if feedback and feedback.strip():
        review = add_feedback_notes(order, cut, review, feedback)
    return review
