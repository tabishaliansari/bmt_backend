"""Pydantic models shared by the API, the database and (later) the AI layer."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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
    featured: bool = False  # demo: the founder's real profile is listed first when it matches
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
    owner: str = ""
    upload_ids: list[str]
    client_note: str
    result: BriefResult
    screened_by: str | None = None  # Gemma model that checked the client's note
    thumbnail_upload_id: str | None = None  # Nano Banana thumbnail concept
    created_at: datetime


class ScreenResult(BaseModel):
    allowed: bool
    reason: str = ""


UploadKind = Literal["raw", "cut", "thumb"]


class UploadOut(BaseModel):
    id: str
    kind: UploadKind
    filename: str
    mime: str
    size: int


class Upload(UploadOut):
    owner: str = ""
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


A11yCheckName = Literal["captions", "caption_readability", "text_contrast", "flashing", "audio_clarity"]


class AccessibilityCheck(BaseModel):
    check: A11yCheckName
    passed: bool
    detail: str = Field(description="What you saw or heard, one short sentence")
    timestamp_sec: int | None = Field(default=None, description="Second where the problem is, if it fails")


class ReviewAI(BaseModel):
    overall_match: int = Field(ge=0, le=100, description="How well the cut matches the brief, 0-100")
    summary: str = Field(description="One sentence verdict")
    checklist: list[ChecklistItem]
    notes: list[ReviewNoteAI]
    accessibility: list[AccessibilityCheck] = Field(description="One entry per accessibility check")


class FeedbackAI(BaseModel):
    notes: list[ReviewNoteAI]


class ReviewResult(BaseModel):
    overall_match: int
    summary: str
    checklist: list[ChecklistItem]
    notes: list[ReviewNote]
    accessibility: list[AccessibilityCheck] = []


class ReviewRequest(BaseModel):
    client_feedback: str | None = Field(default=None, max_length=1000)


# ---------------------------------------------------------------- users

Role = Literal["client", "editor"]


class A11yPrefs(BaseModel):
    """Display settings that follow the account across devices."""
    model_config = ConfigDict(extra="forbid")
    large_text: bool = False
    high_contrast: bool = False
    readable_font: bool = False
    reduce_motion: bool = False


class UserProfile(BaseModel):
    id: str  # Firebase uid
    email: str = ""
    name: str = ""
    role: Role | None = None
    editor_id: str | None = None  # set only for Google accounts linked to a real editor profile
    onboarded: dict[str, bool] = {}  # role -> has seen (or skipped) the intro
    a11y: A11yPrefs = A11yPrefs()
    created_at: datetime


class ProfileUpdate(BaseModel):
    role: Role | None = None
    onboarded_role: Role | None = None  # mark this role's intro as seen
    a11y: A11yPrefs | None = None


# ---------------------------------------------------------------- orders


OrderStatus = Literal["funded", "in_progress", "review", "approved", "refunded"]


class TimelineEvent(BaseModel):
    status: OrderStatus
    at: datetime
    label: str
    code: str = ""  # stable action name: funded, accepted, declined, delivered, changes, approved


class Payout(BaseModel):
    """Simulated Ramp payout to the editor, in INR."""
    amount_usd: float
    fx_rate: float
    amount_inr: float
    gross_usd: float = 0  # what the client paid
    fee_usd: float = 0  # BMT platform fee kept on approval
    fee_pct: float = 0
    transfer_id: str = ""  # simulated Ramp transfer reference
    eta: str = "About 1 business day"
    rail: Literal["ramp"] = "ramp"
    status: Literal["simulated"] = "simulated"
    at: datetime


class Payment(BaseModel):
    """Simulated client payment that funds escrow. No card data is ever collected."""
    method: str  # display label, e.g. "Test card ending 4242"
    amount_usd: float
    amount_inr: float
    reference: str  # simulated processor reference
    status: Literal["held", "released", "refunded"] = "held"
    simulated: bool = True
    at: datetime


class ClientNote(BaseModel):
    t: int = Field(ge=0, description="Seconds into the cut")
    text: str = Field(min_length=1, max_length=500)


class OrderRequest(BaseModel):
    editor_id: str
    package_id: str
    brief_id: str | None = None
    addons: list[str] = Field(default=[], max_length=10)
    rush: bool = False
    note: str = Field(default="", max_length=2000)
    payment_method: Literal["demo_card", "demo_upi"] = "demo_card"


class DeliverRequest(BaseModel):
    cut_upload_id: str


class Order(BaseModel):
    id: str
    owner: str = ""
    client_name: str = ""  # shown to the editor; never the client's email
    editor_id: str
    package_id: str
    brief_id: str | None
    brief: BriefResult | None
    thumbnail_upload_id: str | None = None
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
    payment: Payment | None = None
    payout: Payout | None = None
    timeline: list[TimelineEvent]
    created_at: datetime
