from fastapi import APIRouter, BackgroundTasks

from ..schemas import TrainingBatchPayload
from ..services.database import get_database_gateway

router = APIRouter()

database = get_database_gateway()


@router.post("/batch")
async def submit_training_batch(payload: TrainingBatchPayload):
  eligible = bool(payload.user.opted_in)
  record = {
    "timestamp": payload.timestamp,
    "user_id": payload.user.id,
    "metadata": payload.metadata,
    "eligible_for_training": eligible,
  }
  if database.is_enabled():
    database.store_training_batch(record)
  return {"success": True, "eligible_for_training": eligible}


@router.post("/run")
async def run_training_job(task: BackgroundTasks):
  from ...training.trainer import schedule_training_job

  task.add_task(schedule_training_job)
  return {"success": True, "status": "scheduled"}
