from __future__ import annotations

from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader

from .check_readiness import check_readiness
from .dataset_config import DATASET_ROOT
from .drum_dataset import DrumDataset
from models.drum_model import DrumModel

BATCH_SIZE = 16
EPOCHS = 50
LEARNING_RATE = 1e-3


def _get_device() -> torch.device:
  return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def train() -> None:
  if not check_readiness(verbose=False):
    print("Dataset not ready. Run check_readiness.py for details.")
    return

  device = _get_device()
  dataset = DrumDataset(root_path=Path(DATASET_ROOT))
  dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, drop_last=False)

  model = DrumModel().to(device)
  criterion = nn.BCELoss()
  optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

  for epoch in range(EPOCHS):
    epoch_loss = 0.0
    for batch in dataloader:
      batch = batch.to(device)
      optimizer.zero_grad()
      outputs = model(batch)
      loss = criterion(outputs, batch)
      loss.backward()
      optimizer.step()
      epoch_loss += loss.item()

    avg_loss = epoch_loss / max(1, len(dataloader))
    print(f"[train_drums] Epoch {epoch + 1}/{EPOCHS} - loss={avg_loss:.4f}")

  checkpoint_dir = Path(__file__).resolve().parent.parent / "models" / "checkpoints" / "drums"
  checkpoint_dir.mkdir(parents=True, exist_ok=True)
  ckpt_path = checkpoint_dir / "drums.pt"
  torch.save(model.state_dict(), ckpt_path)
  print(f"[train_drums] Saved checkpoint to {ckpt_path}")


if __name__ == "__main__":
  train()
