from __future__ import annotations

from pathlib import Path
from typing import List, Dict

import torch

from models.drum_model import DrumModel
from training.drum_dataset import LANE_NAMES

_CHECKPOINT_PATH = Path(__file__).resolve().parent.parent / "models" / "checkpoints" / "drums" / "drums.pt"


def _load_model(checkpoint_path: Path | None = None) -> DrumModel:
  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  model = DrumModel().to(device)
  model.eval()
  ckpt_path = checkpoint_path or _CHECKPOINT_PATH
  if ckpt_path.exists():
    state = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(state)
  else:
    print(f"[generate_drums] Checkpoint not found at {ckpt_path}. Using untrained weights.")
  return model


def generate_drum_pattern(threshold: float = 0.5, checkpoint_path: Path | None = None) -> List[Dict[str, bool | int]]:
  model = _load_model(checkpoint_path)
  device = next(model.parameters()).device
  seed = torch.zeros((1, 32, len(LANE_NAMES)), dtype=torch.float32, device=device)
  with torch.no_grad():
    output = model(seed)
  grid = (output.squeeze(0).cpu().numpy() >= threshold)
  pattern: List[Dict[str, bool | int]] = []
  for step_index, lane_state in enumerate(grid):
    step_payload: Dict[str, bool | int] = {"step": int(step_index)}
    for lane_name, active in zip(LANE_NAMES, lane_state):
      step_payload[lane_name] = bool(active)
    pattern.append(step_payload)
  return pattern

__all__ = ["generate_drum_pattern"]
