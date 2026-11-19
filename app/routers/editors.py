from fastapi import APIRouter, HTTPException

from app.db import get_db
from app.models import Editor

router = APIRouter(prefix="/editors", tags=["editors"])


def matches_query(editor: Editor, q: str) -> bool:
    haystack = " ".join(
        [editor.name, editor.handle, editor.city, *editor.styles, *(p.title for p in editor.packages)]
    )
    return q.lower() in haystack.lower()


@router.get("")
def list_editors(category: str | None = None, q: str | None = None) -> list[Editor]:
    editors = [Editor.model_validate(d) for d in get_db().list("editors")]
    if category:
        editors = [e for e in editors if category in e.categories]
    if q:
        editors = [e for e in editors if matches_query(e, q)]
    return editors


@router.get("/{editor_id}")
def get_editor(editor_id: str) -> Editor:
    data = get_db().get("editors", editor_id)
    if data is None:
        raise HTTPException(404, f"No editor with id '{editor_id}'")
    return Editor.model_validate(data)
