from fastapi import APIRouter

from app import repo
from app.db import get_db
from app.models import Catalog, Editor
from app.seed import CATALOG

router = APIRouter(tags=["editors"])


def matches_query(editor: Editor, q: str) -> bool:
    haystack = " ".join(
        [editor.name, editor.handle, editor.city, *editor.styles, *(p.title for p in editor.packages)]
    )
    return q.lower() in haystack.lower()


@router.get("/editors")
def list_editors(category: str | None = None, q: str | None = None) -> list[Editor]:
    editors = [Editor.model_validate(d) for d in get_db().list("editors")]
    if category:
        editors = [e for e in editors if category in e.categories]
    if q:
        editors = [e for e in editors if matches_query(e, q)]
    return editors


@router.get("/editors/recommended")
def recommended_editors(brief_id: str) -> list[Editor]:
    """Editors in the brief's recommended category, best rated first. Declared before /{editor_id}."""
    category = repo.get_brief(brief_id).result.recommended_package.category
    editors = list_editors(category=category)
    return sorted(editors, key=lambda e: (e.rating, e.rating_count), reverse=True)


@router.get("/editors/{editor_id}")
def get_editor(editor_id: str) -> Editor:
    return repo.get_editor(editor_id)


@router.get("/addons")
def get_catalog() -> Catalog:
    """Add-ons and the rush fee, so the UI shows the same prices the server charges."""
    return CATALOG
