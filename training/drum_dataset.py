from __future__ import annotations

import os
import random
from pathlib import Path
from typing import List, Sequence

import numpy as np
import pretty_midi
import torch
from torch.utils.data import Dataset

LANE_NAMES: Sequence[str] = (
  "kick",
  "snare",
  "hihat_closed",
  "hihat_open",
  "clap",
  "perc",
)

_LANE_TO_INDEX = {name: idx for idx, name in enumerate(LANE_NAMES)}
_PITCH_TO_LANE = {
  36: "kick",
  38: "snare",
  42: "hihat_closed",
  46: "hihat_open",
  39: "clap",
  48: "perc",
}

_DEFAULT_DATA_ROOT = Path(__file__).resolve().parent / "data" / "drums"


class DrumDataset(Dataset[torch.Tensor]):
  """Loads drum-ready MIDI clips and snaps them to a 32x6 grid."""

  def __init__(self, root_path: Path | str | None = None) -> None:
    resolved_root = Path(root_path) if root_path else _DEFAULT_DATA_ROOT
    self.data_root = resolved_root
    if not self.data_root.exists():
      if self.data_root == _DEFAULT_DATA_ROOT:
        self.data_root.mkdir(parents=True, exist_ok=True)
      else:
        print(f"[DrumDataset] Dataset root {self.data_root} does not exist.")
    self.files = self._discover_files()
    if not self.files:
      print("[DrumDataset] No MIDI files found. Training will use synthetic noise samples.")

  def __len__(self) -> int:
    return max(len(self.files), 1)

  def __getitem__(self, index: int) -> torch.Tensor:
    if not self.files:
      return self._synthetic_pattern()
    midi_path = self.files[index % len(self.files)]
    grid = self._encode_file(midi_path)
    return torch.from_numpy(grid)

  def _discover_files(self) -> List[Path]:
    midi_files: List[Path] = []
    if not self.data_root.exists():
      return midi_files
    for dirpath, _, filenames in os.walk(self.data_root):
      for filename in filenames:
        if Path(filename).suffix.lower() in {".mid", ".midi"}:
          midi_files.append(Path(dirpath) / filename)
    return sorted(midi_files)

  def _synthetic_pattern(self) -> torch.Tensor:
    grid = np.zeros((32, len(LANE_NAMES)), dtype=np.float32)
    rng = random.Random()
    for lane_idx in range(len(LANE_NAMES)):
      hits = rng.sample(range(32), k=rng.randint(2, 6))
      grid[hits, lane_idx] = 1.0
    return torch.from_numpy(grid)

  def _encode_file(self, midi_path: Path) -> np.ndarray:
    grid = np.zeros((32, len(LANE_NAMES)), dtype=np.float32)
    try:
      midi = pretty_midi.PrettyMIDI(str(midi_path))
    except Exception as exc:  # noqa: BLE001
      print(f"[DrumDataset] Failed to parse {midi_path}: {exc}")
      return grid

    total_time = midi.get_end_time()
    step_duration = total_time / 32 if total_time > 0 else 0.5
    if step_duration == 0:
      step_duration = 0.5

    for instrument in midi.instruments:
      if not instrument.is_drum:
        continue
      for note in instrument.notes:
        lane_name = _PITCH_TO_LANE.get(note.pitch)
        if lane_name is None:
          continue
        lane_idx = _LANE_TO_INDEX[lane_name]
        step_index = self._quantize_step(note.start, step_duration)
        grid[step_index, lane_idx] = 1.0

    return grid

  @staticmethod
  def _quantize_step(note_start: float, step_duration: float) -> int:
    if step_duration <= 0:
      return 0
    step = int(note_start / step_duration)
    return max(0, min(31, step))

__all__ = ["DrumDataset", "LANE_NAMES"]
