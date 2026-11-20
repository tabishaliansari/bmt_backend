class AIError(Exception):
    """Gemini failed or returned something unusable. The message is safe to show users."""


class AITimeout(AIError):
    """Gemini did not answer within AI_TIMEOUT_SEC."""


class AIConfigError(AIError):
    """The server is missing AI configuration. The message is for the server log only;
    users get a generic message so env var names and file paths never leak."""
