"""Reference material for the Brief Builder: clips the client uploaded and links they pasted.

Public YouTube links are watched by Gemini directly (first 90 seconds, to bound cost). Other
links (Instagram, TikTok, any page) can't be fetched by Gemini, so they go in as text only.
We never fetch a link ourselves (no server-side requests to user-supplied URLs)."""

from urllib.parse import parse_qs, urlparse

from google.genai import types

from app.ai.media import video_part
from app.models import Upload

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
MAX_WATCHED_LINKS = 2
WATCH_SECONDS = 90


def youtube_watch_url(link: str) -> str | None:
    """Canonical https://www.youtube.com/watch?v=ID for a YouTube link (watch, youtu.be, shorts), else None."""
    url = urlparse(link)
    if url.hostname not in YOUTUBE_HOSTS:
        return None
    if url.hostname == "youtu.be":
        video_id = url.path.lstrip("/").split("/")[0]
    elif url.path.startswith(("/shorts/", "/live/", "/embed/")):
        video_id = url.path.split("/")[2] if len(url.path.split("/")) > 2 else ""
    else:
        video_id = parse_qs(url.query).get("v", [""])[0]
    if not video_id.replace("-", "").replace("_", "").isalnum() or len(video_id) > 20:
        return None
    return f"https://www.youtube.com/watch?v={video_id}"


def reference_parts(ref_uploads: list[Upload], links: list[str], watch_links: bool = True) -> list[types.Part]:
    """Labelled parts: 'Reference 1', 'Reference 2', ... in the order clips then links."""
    parts: list[types.Part] = []
    n = 0
    for upload in ref_uploads:
        n += 1
        parts.append(types.Part.from_text(text=f"Reference {n}: a clip the client likes ({upload.filename})"))
        parts.append(video_part(upload))
    watched = 0
    for link in links:
        n += 1
        yt = youtube_watch_url(link)
        if yt and watch_links and watched < MAX_WATCHED_LINKS:
            watched += 1
            parts.append(types.Part.from_text(text=f"Reference {n}: a YouTube video the client likes ({link}). Watch it:"))
            parts.append(types.Part(
                file_data=types.FileData(file_uri=yt, mime_type="video/mp4"),
                video_metadata=types.VideoMetadata(start_offset="0s", end_offset=f"{WATCH_SECONDS}s"),
            ))
        else:
            parts.append(types.Part.from_text(text=(
                f"Reference {n}: a link the client likes ({link}). You can't open it; use only what the "
                "link itself and the client's note tell you, and don't guess its content."
            )))
    return parts


def has_watched_links(links: list[str]) -> bool:
    return any(youtube_watch_url(link) for link in links)
