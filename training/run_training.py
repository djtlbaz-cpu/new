from __future__ import annotations

import argparse
from pathlib import Path

from .trainer import TrainingConfig, train


def main() -> None:
  parser = argparse.ArgumentParser(description="Run local Beat Addicts training loop")
  parser.add_argument("--data-dir", type=Path, default=Path("training/data"))
  parser.add_argument("--epochs", type=int, default=2)
  parser.add_argument("--batch-size", type=int, default=32)
  parser.add_argument("--learning-rate", type=float, default=1e-4)
  args = parser.parse_args()

  config = TrainingConfig(
    data_dir=args.data_dir,
    epochs=args.epochs,
    batch_size=args.batch_size,
    learning_rate=args.learning_rate,
  )
  checkpoint = train(config)
  print(f"Saved checkpoint to {checkpoint}")


if __name__ == "__main__":
  main()
