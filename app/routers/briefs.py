import secrets
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from app import repo
from app.ai.brief_builder import build_brief
from app.models import Brief, BriefRequest, BriefUpdate, Upload

router = APIRouter(prefix="/briefs", tags=["briefs"])


def load_raw_uploads(upload_ids: list[str]) -> list[Upload]:
    uploads = [repo.get_upload(upload_id) for upload_id in upload_ids]
    for upload in uploads:
        if upload.kind != "raw":
            raise HTTPException(422, f"Upload '{upload.id}' is an editor's cut, not raw footage.")
    return uploads


@router.post("", status_code=201)
def create_brief(body: BriefRequest) -> Brief:
    uploads = load_raw_uploads(body.upload_ids)
    result = build_brief(uploads, body.client_note)
    brief = Brief(
        id=f"br_{secrets.token_hex(4)}", upload_ids=body.upload_ids,
        client_note=body.client_note, result=result, created_at=datetime.now(UTC),
    )
    repo.save("briefs", brief)
    return brief


@router.get("/{brief_id}")
def get_brief(brief_id: str) -> Brief:
    return repo.get_brief(brief_id)


@router.put("/{brief_id}")
def update_brief(brief_id: str, body: BriefUpdate) -> Brief:
    """The client edits the brief inline before ordering."""
    brief = repo.get_brief(brief_id).model_copy(update={"result": body.result})
    repo.save("briefs", brief)
    return brief
