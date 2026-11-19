"""Pydantic models shared by the API, the database and (later) the AI layer."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Package(BaseModel):
    id: str
    editor_id: str
    title: str
    desc: str
    price_inr: float
    price_usd: float
    eta_hours: int
    tag: Literal["try", "best"] | None = None
    g: int  # thumbnail gradient index (UI only)


class Credit(BaseModel):
    g: int
    title: str
    channel: str
    views: str
    date: str
    len: str
    confirmed: bool = True


class Review(BaseModel):
    name: str
    av: int
    stars: int
    text: str
    item: str
    when: str


class Editor(BaseModel):
    id: str
    name: str
    initials: str
    av: int
    handle: str
    city: str
    styles: list[str]
    categories: list[str]
    cover: int
    rating: float
    rating_count: int
    credits: int
    channels: int
    views: str
    on_time: int
    reply: str
    from_inr: float
    days: str
    packages: list[Package]
    credit_list: list[Credit]
    reviews: list[Review]
    work: list[int]


Category = Literal["reels", "youtube", "podcasts", "ads", "weddings", "gaming"]
BriefFormat = Literal["reel", "shorts", "youtube", "podcast_clips", "ad", "other"]


class BestMoment(BaseModel):
    upload_id: str = Field(description="Id of the clip this moment is in, exactly as labelled")
    start: str = Field(description="Start time in the clip, MM:SS")
    end: str = Field(description="End time in the clip, MM:SS")
    why: str = Field(description="Why this moment is worth using, one short sentence")


class RecommendedPackage(BaseModel):
    category: Category
    package_title: str = Field(description="Short name of the kind of package, e.g. Instagram Reel")
    reason: str = Field(description="Why this package fits, one short sentence")


class BriefResult(BaseModel):
    title: str
    format: BriefFormat
    target_length_sec: int
    hook_idea: str
    best_moments: list[BestMoment]
    style_notes: str
    must_include: list[str]
    questions_for_client: list[str]
    recommended_package: RecommendedPackage


class BriefUpdate(BaseModel):
    result: BriefResult


class BriefRequest(BaseModel):
    upload_ids: list[str] = Field(min_length=1, max_length=3)
    client_note: str = Field(default="", max_length=1000)


class Brief(BaseModel):
    id: str
    upload_ids: list[str]
    client_note: str
    result: BriefResult
    created_at: datetime


UploadKind = Literal["raw", "cut"]


class UploadOut(BaseModel):
    id: str
    kind: UploadKind
    filename: str
    mime: str
    size: int


class Upload(UploadOut):
    storage_path: str
    created_at: datetime


# ---------------------------------------------------------------- pricing


class Addon(BaseModel):
    id: str
    icon: str
    title: str
    sub: str
    price_inr: float
    price_usd: float


class Catalog(BaseModel):
    addons: list[Addon]
    rush_fee_inr: float
    rush_fee_usd: float


# ---------------------------------------------------------------- review


Severity = Literal["low", "medium", "high"]


class ChecklistItem(BaseModel):
    item: str = Field(description="One requirement from the brief, short")
    met: bool


class ReviewNoteAI(BaseModel):
    timestamp_sec: int = Field(description="Second in the cut where the note applies")
    issue: str = Field(description="What is wrong or missing, one short sentence")
    suggestion: str = Field(description="What the editor should do, concrete and actionable")
    severity: Severity


class ReviewNote(ReviewNoteAI):
    source: Literal["ai", "client"]


class ReviewAI(BaseModel):
    overall_match: int = Field(ge=0, le=100, description="How well the cut matches the brief, 0-100")
    summary: str = Field(description="One sentence verdict")
    checklist: list[ChecklistItem]
    notes: list[ReviewNoteAI]


class FeedbackAI(BaseModel):
    notes: list[ReviewNoteAI]


class ReviewResult(BaseModel):
    overall_match: int
    summary: str
    checklist: list[ChecklistItem]
    notes: list[ReviewNote]


class ReviewRequest(BaseModel):
    client_feedback: str | None = Field(default=None, max_length=1000)


# ---------------------------------------------------------------- orders


OrderStatus = Literal["funded", "in_progress", "review", "approved", "refunded"]


class TimelineEvent(BaseModel):
    status: OrderStatus
    at: datetime
    label: str


class Payout(BaseModel):
    amount_usd: float
    fx_rate: float
    amount_inr: float
    rail: Literal["ramp"] = "ramp"
    status: Literal["simulated"] = "simulated"
    at: datetime


class ClientNote(BaseModel):
    t: int = Field(ge=0, description="Seconds into the cut")
    text: str = Field(min_length=1, max_length=500)


class OrderRequest(BaseModel):
    editor_id: str
    package_id: str
    brief_id: str | None = None
    addons: list[str] = []
    rush: bool = False
    note: str = Field(default="", max_length=2000)


class DeliverRequest(BaseModel):
    cut_upload_id: str


class Order(BaseModel):
    id: str
    editor_id: str
    package_id: str
    brief_id: str | None
    brief: BriefResult | None
    title: str
    g: int
    addons: list[str]
    rush: bool
    note: str
    total_usd: float
    total_inr: float
    status: OrderStatus
    revisions_left: int
    due_at: datetime
    cut_upload_id: str | None = None
    review: ReviewResult | None = None
    client_notes: list[ClientNote] = []
    payout: Payout | None = None
    timeline: list[TimelineEvent]
    created_at: datetime
