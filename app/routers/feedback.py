from fastapi import APIRouter

from ..schemas import FeedbackPayload, MidiUploadPayload
from ..services.database import get_database_gateway

router = APIRouter()

database = get_database_gateway()


@router.post("/pattern")
async def pattern_feedback(payload: FeedbackPayload):
  eligible_for_training = payload.accepted and payload.user.opted_in
  if database.is_enabled():
    database.store_pattern_feedback({
      "pattern_id": payload.pattern_id,
      "style": payload.style,
      "accepted": payload.accepted,
      "metadata": payload.metadata,
      "user_id": payload.user.id,
      "opted_in": payload.user.opted_in,
      "eligible_for_training": eligible_for_training,
    })
  return {"success": True, "eligible_for_training": eligible_for_training}


@router.post("/midi")
async def upload_midi(payload: MidiUploadPayload):
  if database.is_enabled():
    database.store_midi_asset({
      "name": payload.name,
      "data": payload.data,
      "url": payload.url,
      "metadata": payload.metadata,
      "user_id": payload.user.id,
      "opted_in": payload.user.opted_in,
    })
  return {"success": True}
