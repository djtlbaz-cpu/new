from __future__ import annotations

import random
from pathlib import Path

import torch


def resolve_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def seed_everything(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def save_checkpoint(model: torch.nn.Module, checkpoint_dir: Path, tag: str) -> Path:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    path = checkpoint_dir / f"{tag}.pt"
    torch.save({"state_dict": model.state_dict()}, path)
    return path
