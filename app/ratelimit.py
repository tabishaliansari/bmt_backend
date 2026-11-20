"""Per-user limit on Gemini calls, so a shared URL can't run up the bill.

In-memory and per instance: fine with Cloud Run --max-instances kept small for the demo.
"""

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException

from app.config import get_settings

WINDOW_SEC = 3600
_hits: dict[str, deque[float]] = defaultdict(deque)
_lock = threading.Lock()


def check_ai_quota(uid: str) -> None:
    limit = get_settings().ai_rate_limit_per_hour
    now = time.monotonic()
    with _lock:
        hits = _hits[uid]
        while hits and now - hits[0] > WINDOW_SEC:
            hits.popleft()
        if len(hits) >= limit:
            raise HTTPException(429, "You've reached the hourly limit for AI requests. Please try again later.")
        hits.append(now)
