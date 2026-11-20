from fastapi import APIRouter

from app import repo
from app.auth import UserId
from app.db import get_db
from app.models import Catalog, Editor
from app.seed import CATALOG, EDITORS

router = APIRouter(tags=["editors"])

SEED_ORDER = {e.id: i for i, e in enumerate(EDITORS)}


def matches_query(editor: Editor, q: str) -> bool:
    haystack = " ".join(
        [editor.name, editor.handle, editor.city, *editor.styles, *(p.title for p in editor.packages)]
    )
    return q.lower() in haystack.lower()


@router.get("/editors")
def list_editors(category: str | None = None, q: str | None = None) -> list[Editor]:
    """Public. Ordered as seeded (the database itself has no order)."""
    editors = [Editor.model_validate(d) for d in get_db().list("editors")]
    editors.sort(key=lambda e: SEED_ORDER.get(e.id, len(SEED_ORDER)))
    if category:
        editors = [e for e in editors if category in e.categories]
    if q:
        editors = [e for e in editors if matches_query(e, q)]
    return editors


@router.get("/editors/recommended")
def recommended_editors(brief_id: str, uid: UserId) -> list[Editor]:
    """Editors in the brief's recommended category: featured first, then best rated.
    Declared before /{editor_id}."""
    category = repo.get_brief(brief_id, owner=uid).result.recommended_package.category
    editors = list_editors(category=category)
    return sorted(editors, key=lambda e: (e.featured, e.rating, e.rating_count), reverse=True)


@router.get("/editors/{editor_id}")
def get_editor(editor_id: str) -> Editor:
    return repo.get_editor(editor_id)


@router.get("/addons")
def get_catalog() -> Catalog:
    """Add-ons and the rush fee, so the UI shows the same prices the server charges."""
    return CATALOG
