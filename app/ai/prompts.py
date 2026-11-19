"""Loads prompts from backend/prompts/*.md at call time, so they can be tuned without a restart."""

from app.config import BACKEND_DIR

PROMPTS_DIR = BACKEND_DIR / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
