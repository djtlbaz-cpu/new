from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

import numpy as np
from .dataset_config import DATASET_ROOT
from .drum_dataset import DrumDataset, LANE_NAMES

REPORT_PATH = Path(__file__).resolve().parent / "data" / "drum_report.json"


def _collect_statistics(dataset: DrumDataset) -> Dict[str, object]:
    if len(dataset) == 0:
        return {
            "patterns": 0,
            "message": "No drum patterns available. Add MIDI files first.",
        }

    lane_totals = np.zeros(len(LANE_NAMES), dtype=np.float64)
    step_totals = np.zeros(32, dtype=np.float64)
    hits_per_pattern: List[int] = []

    for idx in range(len(dataset)):
        tensor = dataset[idx].numpy()
        lane_totals += tensor.sum(axis=0)
        step_totals += tensor.sum(axis=1)
        hits_per_pattern.append(int(tensor.sum()))

    total_patterns = len(dataset)
    total_possible = total_patterns * 32 * len(LANE_NAMES)
    total_hits = sum(hits_per_pattern)

    density_per_lane = (lane_totals / (total_patterns * 32)).tolist()
    sparsity = 1.0 - (total_hits / total_possible if total_possible else 0.0)

    step_counter = Counter()
    for idx, count in enumerate(step_totals):
        step_counter[idx] = int(count)
    most_common_steps = step_counter.most_common(8)

    distribution = Counter(hits_per_pattern)

    return {
        "patterns": total_patterns,
        "density_per_lane": dict(zip(LANE_NAMES, density_per_lane)),
        "sparsity": sparsity,
        "most_common_steps": most_common_steps,
        "hits_per_pattern_distribution": dict(sorted(distribution.items())),
    }


def generate_report() -> Path:
    dataset = DrumDataset(root_path=DATASET_ROOT)
    stats = _collect_statistics(dataset)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2)
    print(f"[report_drums] Wrote {REPORT_PATH}")
    return REPORT_PATH


if __name__ == "__main__":
    generate_report()
