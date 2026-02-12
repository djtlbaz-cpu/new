from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from ..services.drum_service import create_drum_pattern
from ..services.subscriptions import check_generation_allowed, increment_usage

router = APIRouter()


class DrumGenerateRequest(BaseModel):
    user_id: Optional[str] = None


@router.post("/generate/drums")
async def generate_drums(request: DrumGenerateRequest = DrumGenerateRequest()) -> dict:
    tier_meta = {}
    if request.user_id:
        check_generation_allowed(request.user_id)
        updated = increment_usage(request.user_id)
        tier_meta = {
            "tier_id": updated.tier_id,
            "owns_creation": updated.owns_creations,
            "generations_remaining": updated.remaining,
        }

    pattern = create_drum_pattern()
    return {"success": True, "pattern": pattern, **tier_meta}

SUPABASE_SERVICE_KEY = "eyJhbGciOi...your-full-key-here..."
