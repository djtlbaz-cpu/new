from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List

from ..config import settings
from ..schemas import GenerationRequest
from ..services.database import get_database_gateway
from ..services.legal import guard_inference_request
from models import ModelRegistry


class InferenceEngine:
  def __init__(self, model_dir: str | Path):
    self.model_dir = Path(model_dir)
    self.registry = ModelRegistry(self.model_dir)
    self.loaded = False
    self.database = get_database_gateway()

  async def ensure_loaded(self) -> None:
    if not self.loaded:
      self.registry.load_latest()
      self.loaded = True

  async def generate_pattern(self, section: str, request: GenerationRequest) -> Dict[str, Any]:
    await self.ensure_loaded()
    guard_inference_request(request.user)

    steps = request.steps or settings.default_steps
    seed_value = request.seed or random.randint(0, 10**6)
    rng = random.Random(seed_value)
    pattern_id = f"{section}-{rng.randint(1, 10**9)}"
    tracks = self._build_tracks(section, steps, rng)

    payload = {
      "success": True,
      "pattern": {
        "pattern_id": pattern_id,
        "section": section,
        "steps": steps,
        "tracks": tracks,
        "clips": self._build_clips(section, tracks, rng),
      },
      "metadata": {
        "seed": seed_value,
        "workflow": "pulse-local-v1",
        "style": request.style,
        "bpm": request.bpm,
      },
    }

    if self.database.is_enabled():
      self.database.log_generation({
        "pattern_id": pattern_id,
        "section": section,
        "style": request.style,
        "bpm": request.bpm,
        "user_id": request.user.id,
        "opted_in": request.user.opted_in,
      })

    return payload

  async def generate_arrangement(self, request: GenerationRequest, summary: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    await self.ensure_loaded()
    guard_inference_request(request.user)

    seed_value = request.seed or random.randint(0, 10**6)
    rng = random.Random(seed_value)
    cursor = 0
    slots = ["Intro", "Drop", "Verse", "Bridge", "Outro"]
    sections = []
    for label in slots:
      length = rng.choice([4, 8, 16])
      sections.append({
        "label": label,
        "start": cursor,
        "length": length,
        "intent": f"{request.style} energy",
      })
      cursor += length

    return {
      "success": True,
      "sections": sections,
      "metadata": {
        "arrangement_id": f"arr-{rng.randint(1, 10**9)}",
        "style": request.style,
        "seed": seed_value,
        "summary": summary or [],
      },
    }

  def _build_tracks(self, section: str, steps: int, rng: random.Random) -> List[Dict[str, Any]]:
    if section == "drums":
      blueprint = {
        "Kick": 0.8,
        "Snare": 0.5,
        "Hi-Hat": 0.9,
        "Open Hat": 0.2,
        "Crash": 0.1,
        "Ride": 0.2,
        "Clap": 0.3,
        "Perc": 0.4,
      }
    else:
      blueprint = {section.title(): 0.6}

    tracks = []
    for name, density in blueprint.items():
      hits = self._generate_hits(steps, density, rng)
      tracks.append({
        "name": name,
        "hits": hits,
        "velocity": [round(rng.uniform(0.6, 1.0), 2) for _ in hits],
        "length": 4,
        "offset": 0,
      })
    return tracks

  def _build_clips(self, section: str, tracks: List[Dict[str, Any]], rng: random.Random) -> List[Dict[str, Any]]:
    color_palette = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
    clips = []
    for index, track in enumerate(tracks):
      clips.append({
        "start": index * 4,
        "length": track.get("length", 4),
        "color": color_palette[index % len(color_palette)],
        "name": f"{section.title()} {track['name']}",
      })
    return clips

  def _generate_hits(self, steps: int, density: float, rng: random.Random) -> List[int]:
    hits = []
    for step in range(steps):
      if rng.random() < density:
        hits.append(step)
    if not hits:
      hits.append(rng.randrange(steps))
    return hits


_engine: InferenceEngine | None = None


def get_inference_engine() -> InferenceEngine:
  global _engine  # noqa: PLW0603
  if _engine is None:
    _engine = InferenceEngine(settings.model_dir)
  return _engine
