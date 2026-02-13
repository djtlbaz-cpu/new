from __future__ import annotations

from pathlib import Path

import torch

from ..models.registry import ModelRegistry


def evaluate(checkpoint_dir: Path, samples: torch.Tensor) -> float:
    registry = ModelRegistry(checkpoint_dir.parent)
    registry.load_latest()
    model = registry.get_model().eval()
    with torch.no_grad():
        outputs = model(samples)
        return torch.mean((outputs - samples) ** 2).item()
