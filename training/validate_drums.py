from __future__ import annotations

import os
from pathlib import Path
from shutil import move
from typing import Iterable

import pretty_midi

from .dataset_config import DATASET_ROOT

_DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data" / "drums"
DATASET_ROOT_PATH = Path(DATASET_ROOT)
if DATASET_ROOT_PATH == _DEFAULT_DATA_DIR:
  DATASET_ROOT_PATH.mkdir(parents=True, exist_ok=True)

INVALID_DIR = DATASET_ROOT_PATH.parent / "invalid"
REQUIRED_PITCHES = {36, 38, 42, 46, 39, 48}


def _iter_midi_files() -> Iterable[Path]:
  if not DATASET_ROOT_PATH.exists():
    print(f"[validate_drums] Dataset root {DATASET_ROOT_PATH} does not exist.")
    return []
  for dirpath, _, filenames in os.walk(DATASET_ROOT_PATH):
    for filename in filenames:
      candidate = Path(dirpath) / filename
      if candidate.suffix.lower() in {".mid", ".midi"}:
        yield candidate


def _has_required_pitches(midi: pretty_midi.PrettyMIDI) -> bool:
  for instrument in midi.instruments:
    if not instrument.is_drum:
      continue
    for note in instrument.notes:
      if note.pitch in REQUIRED_PITCHES:
        return True
  return False


def validate_dataset(move_invalid: bool = True) -> None:
  total = 0
  valid = 0
  invalid = []
  missing_required = []

  for midi_path in _iter_midi_files():
    total += 1
    try:
      midi = pretty_midi.PrettyMIDI(str(midi_path))
    except Exception as exc:  # noqa: BLE001
      print(f"[validate_drums] Invalid MIDI {midi_path.name}: {exc}")
      invalid.append(midi_path)
      continue

    if _has_required_pitches(midi):
      valid += 1
    else:
      missing_required.append(midi_path)

  if move_invalid:
    INVALID_DIR.mkdir(parents=True, exist_ok=True)
    for bad in invalid + missing_required:
      destination = INVALID_DIR / bad.name
      print(f"[validate_drums] Moving {bad.name} → {destination}")
      move(str(bad), destination)

  print("\n[validate_drums] Summary")
  print(f"  Total files: {total}")
  print(f"  Valid files: {valid}")
  print(f"  Invalid files: {len(invalid)}")
  print(f"  Missing required pitches: {len(missing_required)}")


if __name__ == "__main__":
  validate_dataset()
