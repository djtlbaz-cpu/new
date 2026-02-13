from __future__ import annotations

from pathlib import Path
from typing import List

import pretty_midi

from .dataset_config import DATASET_ROOT
from .drum_dataset import DrumDataset

_MIDI_EXTENSIONS = {".mid", ".midi"}


def _discover_midi_files(root: Path) -> List[Path]:
    files: List[Path] = []
    if not root.exists():
        return files
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in _MIDI_EXTENSIONS:
            files.append(path)
    return files


def check_readiness(verbose: bool = True) -> bool:
    root = Path(DATASET_ROOT)
    issues: List[str] = []

    if not root.exists():
        issues.append(f"Dataset root not found: {root}")

    midi_files = _discover_midi_files(root)
    if not midi_files:
        issues.append("No MIDI files found after recursive scan.")

    encodable = False
    if midi_files:
        dataset = DrumDataset(root_path=root)
        if not dataset.files:
            issues.append("Dataset loader could not index any MIDI files.")
        else:
            last_error: str | None = None
            for midi_path in dataset.files:
                try:
                    pretty_midi.PrettyMIDI(str(midi_path))
                    _ = dataset[0]  # ensure encoding path works
                    encodable = True
                    break
                except (OSError, EOFError, ValueError, KeyError) as exc:
                    last_error = f"{midi_path.name}: {exc}"
            if not encodable:
                issues.append("Dataset loader failed to encode the available MIDI files.")
                if last_error:
                    issues.append(f"Last error: {last_error}")

    ready = len(issues) == 0

    if verbose:
        if ready:
            print("READY FOR TRAINING")
            print(f"    Dataset root: {root}")
            print(f"    MIDI files detected: {len(midi_files)}")
        else:
            print("Dataset not ready. Missing requirements:")
            for issue in issues:
                print(f"    - {issue}")

    return ready


if __name__ == "__main__":
    check_readiness(verbose=True)
