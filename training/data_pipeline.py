from __future__ import annotations

from pathlib import Path
from typing import Iterator, Tuple

import numpy as np
import torch


class DataPipeline:
    """Loads MIDI or JSON pattern files and converts them into tensors."""

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def dataset(self) -> Iterator[Tuple[torch.Tensor, torch.Tensor]]:
        for file_path in self.data_dir.glob("**/*.npy"):
            array = np.load(file_path)
            yield torch.tensor(array[:-1], dtype=torch.float32), torch.tensor(array[1:], dtype=torch.float32)

    def __len__(self) -> int:
        return sum(1 for _ in self.data_dir.glob("**/*.npy"))
