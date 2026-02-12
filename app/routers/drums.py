from __future__ import annotations

from fastapi import APIRouter

from ..services.drum_service import create_drum_pattern

router = APIRouter()


@router.post("/generate/drums")
async def generate_drums() -> dict:
  pattern = create_drum_pattern()
  return {"success": True, "pattern": pattern}
