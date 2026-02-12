from fastapi import HTTPException

from ..config import settings
from ..schemas import UserContext


def _ensure_user(user: UserContext | None) -> UserContext:
    if user is None:
        raise HTTPException(status_code=400, detail="User context is required for AI operations.")
    return user


def guard_inference_request(user: UserContext | None) -> None:
    user = _ensure_user(user)
    limit = user.generation_limit or settings.legal_generation_limit
    usage = user.generation_count or 0
    if usage >= limit:
        raise HTTPException(status_code=429, detail="Generation limit reached under Phase 0 compliance policy.")


def guard_training_submission(user: UserContext | None, allow_learning: bool) -> None:
    user = _ensure_user(user)
    if allow_learning and not user.opted_in:
        raise HTTPException(status_code=403, detail="User did not opt into AI learning; training payload rejected.")
