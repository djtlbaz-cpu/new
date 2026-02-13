from __future__ import annotations

from pathlib import Path

from mido import Message, MidiFile, MidiTrack, MetaMessage

BPM = 140
TICKS_PER_BEAT = 480
DATASET_ROOT = Path(r"C:\Users\beata\Documents\Splice\Samples")


def beats_to_ticks(beats: float) -> int:
    return int(round(beats * TICKS_PER_BEAT))


def schedule_note(events: list[tuple[int, Message]], note: int, start_beats: float, duration_beats: float, velocity: int) -> None:
    start = beats_to_ticks(start_beats)
    end = beats_to_ticks(start_beats + duration_beats)
    events.append((start, Message("note_on", channel=9, note=note, velocity=velocity)))
    events.append((end, Message("note_off", channel=9, note=note, velocity=0)))


def build_track(pattern_definition: dict) -> MidiFile:
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    mid.tracks.append(track)
    tempo = int(60_000_000 / BPM)
    track.append(MetaMessage("set_tempo", tempo=tempo, time=0))
    track.append(MetaMessage("time_signature", numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))

    events: list[tuple[int, Message]] = []
    for note, hits in pattern_definition.items():
        for start, duration, velocity in hits:
            schedule_note(events, note, start, duration, velocity)

    events.sort(key=lambda item: item[0])
    last_tick = 0
    for tick, message in events:
        delta = tick - last_tick
        message.time = max(0, delta)
        track.append(message)
        last_tick = tick

    total_beats = max((beats_to_ticks(hit[0] + hit[1]) for hits in pattern_definition.values() for hit in hits), default=TICKS_PER_BEAT * 4)
    track.append(MetaMessage("end_of_track", time=max(0, total_beats - last_tick)))
    return mid


def main() -> None:
    DATASET_ROOT.mkdir(parents=True, exist_ok=True)

    patterns = {
        "trap_half_time.mid": {
            36: [(0.0, 0.25, 110), (2.0, 0.25, 112), (3.5, 0.25, 108)],
            38: [(1.0, 0.25, 118), (3.0, 0.25, 120)],
            42: [(i * 0.5, 0.25, 95) for i in range(8)],
        },
        "syncopated_drive.mid": {
            36: [(0.0, 0.25, 115), (1.5, 0.25, 113), (2.0, 0.25, 120), (2.75, 0.25, 110)],
            38: [(1.0, 0.25, 118), (2.5, 0.25, 122), (3.5, 0.25, 118)],
            42: [(i * 0.25, 0.125, 92) for i in range(16)],
        },
        "stutter_groove.mid": {
            36: [(0.0, 0.25, 110), (1.0, 0.25, 105), (2.5, 0.25, 112), (3.0, 0.25, 108)],
            38: [(1.5, 0.25, 120), (3.0, 0.25, 123)],
            42: [(i * 0.5, 0.25, 100) for i in range(8)] + [(i + 0.25, 0.25, 90) for i in [0.0, 1.0, 2.0, 3.0]],
        },
    }

    for filename, pattern in patterns.items():
        midi = build_track(pattern)
        output_path = DATASET_ROOT / filename
        midi.save(output_path)
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
