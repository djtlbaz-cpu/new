from __future__ import annotations

from pathlib import Path

from mido import Message, MidiFile, MidiTrack, MetaMessage

BPM = 140
TICKS_PER_BEAT = 480
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "Samples" / "drums" / "test_pattern.mid"


def beats_to_ticks(beats: float) -> int:
    return int(round(beats * TICKS_PER_BEAT))


def schedule_note(events: list[tuple[int, Message]], start_beats: float, note: int, duration_beats: float, velocity: int) -> None:
    start_ticks = beats_to_ticks(start_beats)
    end_ticks = beats_to_ticks(start_beats + duration_beats)
    events.append((start_ticks, Message("note_on", channel=9, note=note, velocity=velocity)))
    events.append((end_ticks, Message("note_off", channel=9, note=note, velocity=0)))


def build_sequence() -> MidiFile:
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    mid.tracks.append(track)

    tempo = int(60_000_000 / BPM)
    track.append(MetaMessage("set_tempo", tempo=tempo, time=0))
    track.append(MetaMessage("time_signature", numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))

    events: list[tuple[int, Message]] = []

    # Kick on beats 1 and 3 (0 and 2 beats)
    for beat in (0.0, 2.0):
        schedule_note(events, beat, 36, duration_beats=0.25, velocity=110)

    # Snare on beats 2 and 4 (1 and 3 beats)
    for beat in (1.0, 3.0):
        schedule_note(events, beat, 38, duration_beats=0.25, velocity=115)

    # Closed hat on every 1/8 note (every 0.5 beats)
    eighth_points = [i * 0.5 for i in range(8)]
    for beat in eighth_points:
        schedule_note(events, beat, 42, duration_beats=0.25, velocity=96)

    events.sort(key=lambda item: item[0])

    last_tick = 0
    for tick, message in events:
        delta = tick - last_tick
        message.time = max(0, delta)
        track.append(message)
        last_tick = tick

    track.append(MetaMessage("end_of_track", time=beats_to_ticks(4.0) - last_tick if last_tick < beats_to_ticks(4.0) else 0))
    return mid


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    midi = build_sequence()
    midi.save(OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
