from fastapi import HTTPException

from ..schemas import UserContext
from .subscriptions import check_generation_allowed, increment_usage, record_ownership


def _ensure_user(user: UserContext | None) -> UserContext:
    if user is None:
        raise HTTPException(status_code=400, detail="User context is required for AI operations.")
    return user


def guard_inference_request(user: UserContext | None) -> dict:
    """Check tier-based generation limits and increment usage.

    Returns a dict with ownership and usage info to attach to the response.
    """
    user = _ensure_user(user)

    # Tier-based limit check (raises 429 if exhausted)
    check_generation_allowed(user.id)

    # Increment the counter
    updated = increment_usage(user.id)

    return {
        "tier_id": updated.tier_id,
        "owns_creation": updated.owns_creations,
        "generations_remaining": updated.remaining,
    }


def record_generation_ownership(user_id: str, generation_id: str) -> bool:
    """Record content ownership based on the user's current tier."""
    return record_ownership(user_id, generation_id)


def guard_training_submission(user: UserContext | None, allow_learning: bool) -> None:
    user = _ensure_user(user)
    if allow_learning and not user.opted_in:
        raise HTTPException(status_code=403, detail="User did not opt into AI learning; training payload rejected.")
