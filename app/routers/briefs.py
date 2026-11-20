import io
import secrets
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from app import repo
from app.ai.brief_builder import build_brief
from app.ai.screen import screen_text
from app.ai.thumbnail import draft_thumbnail
from app.auth import UserId
from app.models import Brief, BriefRequest, BriefUpdate, Upload
from app.ratelimit import check_ai_quota
from app.routers.uploads import store_upload

router = APIRouter(prefix="/briefs", tags=["briefs"])

IMAGE_EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


def load_uploads(upload_ids: list[str], uid: str, kind: str) -> list[Upload]:
    uploads = [repo.get_upload(upload_id, owner=uid) for upload_id in upload_ids]
    for upload in uploads:
        if upload.kind != kind:
            raise HTTPException(422, f"Upload '{upload.id}' is not a {kind} clip.")
    return uploads


@router.post("", status_code=201)
def create_brief(body: BriefRequest, uid: UserId) -> Brief:
    uploads = load_uploads(body.upload_ids, uid, "raw")
    refs = load_uploads(body.reference_upload_ids, uid, "ref")
    check_ai_quota(uid)
    # Gemma screens what the client typed, links included (they're user text too).
    verdict, screened_by = screen_text(" ".join([body.client_note, *body.reference_links]).strip())
    if not verdict.allowed:
        raise HTTPException(422, f"Please rephrase your note: {verdict.reason}")
    result = build_brief(uploads, body.client_note, refs, body.reference_links)
    brief = Brief(
        id=f"br_{secrets.token_hex(8)}", owner=uid, upload_ids=body.upload_ids,
        client_note=body.client_note, reference_upload_ids=body.reference_upload_ids,
        reference_links=body.reference_links, result=result, screened_by=screened_by,
        created_at=datetime.now(UTC),
    )
    repo.save("briefs", brief)
    return brief


@router.get("/{brief_id}")
def get_brief(brief_id: str, uid: UserId) -> Brief:
    return repo.get_brief(brief_id, owner=uid)


@router.put("/{brief_id}")
def update_brief(brief_id: str, body: BriefUpdate, uid: UserId) -> Brief:
    """The client edits the brief inline before ordering."""
    brief = repo.get_brief(brief_id, owner=uid).model_copy(update={"result": body.result})
    repo.save("briefs", brief)
    return brief


@router.post("/{brief_id}/thumbnail")
def create_thumbnail(brief_id: str, uid: UserId) -> Brief:
    """Nano Banana drafts a thumbnail concept from the brief; replaces any earlier draft."""
    brief = repo.get_brief(brief_id, owner=uid)
    check_ai_quota(uid)
    data, mime = draft_thumbnail(brief.result)
    image = store_upload(uid, "thumb", "thumbnail" + IMAGE_EXT.get(mime, ".png"), mime, io.BytesIO(data), len(data))
    brief = brief.model_copy(update={"thumbnail_upload_id": image.id})
    repo.save("briefs", brief)
    return brief
