from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


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
