from fastapi import APIRouter, Depends

from ..schemas import GenerationRequest
from ..services.inference import get_inference_engine, InferenceEngine

router = APIRouter()


async def _generate_section(section: str, request: GenerationRequest, engine: InferenceEngine) -> dict:
  return await engine.generate_pattern(section, request)


@router.post("/bassline")
async def generate_bassline(request: GenerationRequest, engine: InferenceEngine = Depends(get_inference_engine)):
  return await _generate_section("bassline", request, engine)


@router.post("/melody")
async def generate_melody(request: GenerationRequest, engine: InferenceEngine = Depends(get_inference_engine)):
  return await _generate_section("melody", request, engine)


@router.post("/chords")
async def generate_chords(request: GenerationRequest, engine: InferenceEngine = Depends(get_inference_engine)):
  return await _generate_section("chords", request, engine)


@router.post("/arrangement")
async def generate_arrangement(request: GenerationRequest, engine: InferenceEngine = Depends(get_inference_engine)):
  summary = request.sections or (request.metadata.get("sections") if request.metadata else None)
  return await engine.generate_arrangement(request, summary)
