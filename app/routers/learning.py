from fastapi import APIRouter

from ..schemas import PreferencePayload
from ..services.database import get_database_gateway

router = APIRouter()

database = get_database_gateway()


@router.post("/preferences")
async def sync_preferences(payload: PreferencePayload):
  synced = False
  if payload.user.opted_in and database.is_enabled():
    synced = database.store_preference_profile({
      "style": payload.style,
      "accepted": payload.accepted,
      "metadata": payload.metadata,
      "preferences": payload.preferences,
      "user_id": payload.user.id,
    })

  return {"success": True, "synced": synced}
