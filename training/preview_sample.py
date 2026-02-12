from __future__ import annotations

from typing import Iterable

from .dataset_config import DATASET_ROOT
from .drum_dataset import DrumDataset, LANE_NAMES


def _format_row(step_idx: int, values: Iterable[float]) -> str:
    binary = ["1" if v >= 0.5 else "0" for v in values]
    return f"step {step_idx:02d}: [" + " ".join(binary) + "]"


def preview_samples(count: int = 3) -> None:
    dataset = DrumDataset(root_path=DATASET_ROOT)
    total = min(count, len(dataset))
    if total == 0:
        print("[preview_sample] No samples available. Add MIDI files first.")
        return

    header = "       [" + " ".join(LANE_NAMES) + "]"
    print(header)
    for idx in range(total):
        pattern = dataset[idx].numpy()
        print(f"\nPattern #{idx + 1}")
        for step_idx in range(pattern.shape[0]):
            print(_format_row(step_idx, pattern[step_idx]))


if __name__ == "__main__":
    preview_samples()
