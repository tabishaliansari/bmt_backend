class AIError(Exception):
    """Gemini failed or returned something unusable. The message is safe to show users."""


class AITimeout(AIError):
    """Gemini did not answer within AI_TIMEOUT_SEC."""
