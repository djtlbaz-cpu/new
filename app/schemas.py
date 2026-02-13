from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


# ── Subscription Tiers ──────────────────────────────────────


class TierID(str, Enum):
    FREE = "free"
    STARTER = "starter"
    STUDIO = "studio"


class TierInfo(BaseModel):
    id: str
    name: str
    price_cents: int
    monthly_generations: int
    owns_creations: bool
    full_tool_access: bool
    description: Optional[str] = None


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"


class UserSubscription(BaseModel):
    id: Optional[str] = None
    user_id: str
    tier_id: str
    status: str = "active"
    started_at: Optional[str] = None
    expires_at: Optional[str] = None


class SubscribeRequest(BaseModel):
    user_id: str
    tier_id: TierID


class SubscriptionResponse(BaseModel):
    success: bool = True
    subscription: UserSubscription
    tier: TierInfo


# ── Add-ons ─────────────────────────────────────────────────


class AddonInfo(BaseModel):
    id: str
    name: str
    price_cents: int
    description: Optional[str] = None
    requires_tier: Optional[str] = None
    active: bool = True


class UserAddon(BaseModel):
    id: Optional[str] = None
    user_id: str
    addon_id: str
    status: str = "active"
    started_at: Optional[str] = None


class AddonSubscribeRequest(BaseModel):
    user_id: str
    addon_id: str


class AddonResponse(BaseModel):
    success: bool = True
    addon: UserAddon
    info: AddonInfo


# ── Generation Usage ────────────────────────────────────────


class UsageInfo(BaseModel):
    user_id: str
    period: str
    count: int
    limit: int
    remaining: int
    tier_id: str
    owns_creations: bool


# ── User Registration ───────────────────────────────────────


class RegisterRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None


class UserProfile(BaseModel):
    id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    tier: TierInfo
    addons: List[AddonInfo] = Field(default_factory=list)
    usage: Optional[UsageInfo] = None


class UserContext(BaseModel):
    id: str
    email: Optional[str] = None
    opted_in: bool = Field(default=False, alias="optedIn")
    license_tier: Optional[str] = Field(default="Phase0", alias="licenseTier")
    generation_limit: Optional[int] = Field(default=None, alias="generationLimit")
    generation_count: Optional[int] = Field(default=None, alias="generationCount")
    region: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class TrackPattern(BaseModel):
    name: str
    hits: List[int] = Field(default_factory=list)
    velocity: Optional[List[float]] = None
    notes: Optional[List[Dict[str, Any]]] = None
    length: Optional[int] = None
    offset: Optional[int] = None


class Clip(BaseModel):
    start: int = 0
    length: int = 4
    color: Optional[str] = None
    name: Optional[str] = None


class PatternPayload(BaseModel):
    pattern_id: str = Field(alias="patternId")
    section: str
    steps: int
    tracks: List[TrackPattern]
    clips: Optional[List[Clip]] = None

    model_config = ConfigDict(populate_by_name=True)


class GenerationRequest(BaseModel):
    style: str
    bpm: int = 128
    steps: int = 16
    temperature: float = 0.65
    seed: Optional[int] = None
    user: UserContext
    allow_learning: bool = Field(default=False, alias="allowLearning")
    metadata: Optional[Dict[str, Any]] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    sections: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(populate_by_name=True)


class PatternResponse(BaseModel):
    success: bool = True
    pattern: PatternPayload
    metadata: Dict[str, Any]


class ArrangementSection(BaseModel):
    label: str
    start: int
    length: int
    intent: Optional[str] = None


class ArrangementResponse(BaseModel):
    success: bool = True
    sections: List[ArrangementSection]
    metadata: Dict[str, Any]


class FeedbackPayload(BaseModel):
    pattern_id: str = Field(alias="patternId")
    accepted: bool
    style: str
    metadata: Optional[Dict[str, Any]] = None
    user: UserContext

    model_config = ConfigDict(populate_by_name=True)


class TrainingBatchPayload(BaseModel):
    timestamp: str
    user: UserContext
    metadata: Optional[Dict[str, Any]] = None


class PreferencePayload(BaseModel):
    style: str
    accepted: bool
    metadata: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    user: UserContext


class MidiUploadPayload(BaseModel):
    name: str
    data: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    user: UserContext
