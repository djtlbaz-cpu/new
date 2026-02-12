from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pretty_midi

from .dataset_config import DATASET_ROOT

_DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data" / "drums"
DATASET_ROOT_PATH = Path(DATASET_ROOT)
if DATASET_ROOT_PATH == _DEFAULT_DATA_DIR:
  DATASET_ROOT_PATH.mkdir(parents=True, exist_ok=True)

ALLOWED_PITCHES = {36, 38, 42, 46, 39, 48}
STEP_COUNT = 32


def _iter_midi_files() -> Iterable[Path]:
  if not DATASET_ROOT_PATH.exists():
    print(f"[normalize_drums] Dataset root {DATASET_ROOT_PATH} does not exist.")
    return []
  for dirpath, _, filenames in os.walk(DATASET_ROOT_PATH):
    for filename in filenames:
      candidate = Path(dirpath) / filename
      if candidate.suffix.lower() in {".mid", ".midi"}:
        yield candidate


def normalize_midi(path: Path) -> bool:
  try:
    midi = pretty_midi.PrettyMIDI(str(path))
  except Exception as exc:  # noqa: BLE001
    print(f"[normalize_drums] Failed to load {path.name}: {exc}")
    return False

  total_time = midi.get_end_time() or 1.0
  step_duration = total_time / STEP_COUNT
  changed = False

  for instrument in midi.instruments:
    if not instrument.is_drum:
      if instrument.notes:
        instrument.notes = []
        changed = True
      continue

    filtered = []
    seen = set()
    for note in instrument.notes:
      if note.pitch not in ALLOWED_PITCHES:
        changed = True
        continue
      step = int(round(note.start / step_duration)) if step_duration > 0 else 0
      step = max(0, min(STEP_COUNT - 1, step))
      key = (note.pitch, step)
      if key in seen:
        changed = True
        continue
      seen.add(key)
      new_start = step * step_duration
      new_end = new_start + max(step_duration * 0.5, 0.05)
      note.start = new_start
      note.end = new_end
      note.velocity = max(30, min(110, note.velocity))
      filtered.append(note)
    if len(filtered) != len(instrument.notes):
      changed = True
    instrument.notes = filtered

  if changed:
    midi.write(str(path))
    print(f"[normalize_drums] Normalized {path}")
  return True


def batch_normalize() -> None:
  for midi_file in _iter_midi_files():
    normalize_midi(midi_file)


if __name__ == "__main__":
  batch_normalize()
