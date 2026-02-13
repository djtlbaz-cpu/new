from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path

import torch
from torch.optim import AdamW

from ..models.registry import ModelRegistry
from .data_pipeline import DataPipeline
from .utils import resolve_device, save_checkpoint, seed_everything


@dataclass
class TrainingConfig:
    data_dir: Path = Path("training/data")
    checkpoint_dir: Path = Path("models/checkpoints")
    epochs: int = 2
    batch_size: int = 32
    learning_rate: float = 1e-4
    seed: int = 42


def train(config: TrainingConfig) -> Path:
    seed_everything(config.seed)
    device = resolve_device()

    registry = ModelRegistry(config.checkpoint_dir.parent)
    registry.load_latest()
    model = registry.get_model().to(device)
    pipeline = DataPipeline(config.data_dir)
    optimizer = AdamW(model.parameters(), lr=config.learning_rate)
    loss_fn = torch.nn.MSELoss()

    for _epoch in range(config.epochs):
        for inputs, targets in pipeline.dataset():
            inputs = inputs.to(device)
            targets = targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = loss_fn(outputs, targets)
            loss.backward()
            optimizer.step()

    tag = dt.datetime.utcnow().strftime("ckpt-%Y%m%d-%H%M%S")
    return save_checkpoint(model.cpu(), config.checkpoint_dir, tag)


def schedule_training_job() -> None:
    config = TrainingConfig()
    train(config)
