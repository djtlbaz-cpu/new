from __future__ import annotations

from pathlib import Path
from typing import Optional

import torch

from .base_model import GrooveTransformer


class ModelRegistry:
  def __init__(self, model_dir: Path | str):
    self.model_dir = Path(model_dir)
    self.checkpoint_dir = self.model_dir / "checkpoints"
    self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    self.model = GrooveTransformer()
    self.loaded_checkpoint: Optional[Path] = None

  def load_latest(self) -> None:
    checkpoint = self._latest_checkpoint()
    if checkpoint is None:
      self._warm_start()
      return

    state_dict = torch.load(checkpoint, map_location="cpu")
    if isinstance(state_dict, dict) and "state_dict" in state_dict:
      state_dict = state_dict["state_dict"]
    self.model.load_state_dict(state_dict)
    self.loaded_checkpoint = checkpoint

  def _latest_checkpoint(self) -> Optional[Path]:
    checkpoints = sorted(self.checkpoint_dir.glob("*.pt"), reverse=True)
    return checkpoints[0] if checkpoints else None

  def _warm_start(self) -> None:
    def init_weights(module):
      if isinstance(module, torch.nn.Linear):
        torch.nn.init.xavier_uniform_(module.weight)
        if module.bias is not None:
          torch.nn.init.zeros_(module.bias)

    self.model.apply(init_weights)
    self.loaded_checkpoint = None

  def get_model(self) -> GrooveTransformer:
    return self.model
