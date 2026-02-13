from __future__ import annotations

import torch
import pretty_midi

from training.drum_dataset import DrumDataset, LANE_NAMES


def _write_dummy_midi(path, pitch=36, start=0.0, end=0.5):
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0, is_drum=True)
    instrument.notes.append(
        pretty_midi.Note(velocity=100, pitch=pitch, start=start, end=end)
    )
    midi.instruments.append(instrument)
    midi.write(str(path))


def test_dataset_uses_custom_root(tmp_path):
    dataset = DrumDataset(root_path=tmp_path)
    assert dataset.data_root == tmp_path


def test_dataset_synthetic_pattern_shape(tmp_path):
    dataset = DrumDataset(root_path=tmp_path)
    sample = dataset[0]
    assert sample.shape == (32, len(LANE_NAMES))
    assert sample.dtype == torch.float32
    unique_values = sample.unique().tolist()
    assert all(value in (0.0, 1.0) for value in unique_values)


def test_dataset_discovers_nested_midis(tmp_path):
    nested = tmp_path / "samples" / "kits"
    nested.mkdir(parents=True)
    midi_one = tmp_path / "kick.mid"
    midi_two = nested / "snare.midi"
    _write_dummy_midi(midi_one, pitch=36)
    _write_dummy_midi(midi_two, pitch=38)
    (tmp_path / "ignore.txt").write_text("noise")

    dataset = DrumDataset(root_path=tmp_path)

    assert len(dataset.files) == 2
    assert len(dataset) == 2


def test_dataset_encodes_known_pitch(tmp_path):
    midi_path = tmp_path / "pattern.mid"
    _write_dummy_midi(midi_path, pitch=36)

    dataset = DrumDataset(root_path=tmp_path)
    tensor = dataset[0]

    assert tensor.shape == (32, len(LANE_NAMES))
    assert tensor[0, 0].item() == 1.0
    hits = tensor.sum().item()
    assert hits == 1.0


def test_dataset_len_defaults_to_one_when_empty(tmp_path):
    missing_root = tmp_path / "does_not_exist"
    dataset = DrumDataset(root_path=missing_root)

    assert len(dataset.files) == 0
    assert len(dataset) == 1
