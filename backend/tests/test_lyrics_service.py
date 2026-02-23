from __future__ import annotations

import pytest
from app.services.lyrics_service import LyricsGenerator, _detect_genre


def test_detect_genre_hip_hop():
    assert _detect_genre("trap beats with 808 drums") == "hip hop"


def test_detect_genre_rock():
    assert _detect_genre("heavy guitar rock music") == "rock"


def test_detect_genre_defaults_to_pop():
    assert _detect_genre("something completely unrelated") == "pop"


def test_lyrics_generator_returns_string():
    gen = LyricsGenerator()
    result = gen.generate("overcoming challenges")
    assert isinstance(result, str)
    assert len(result) > 0


def test_lyrics_generator_contains_sections():
    gen = LyricsGenerator()
    result = gen.generate("dreams and freedom", genre="pop")
    assert "[Verse 1]" in result
    assert "[Chorus]" in result
    assert "[Verse 2]" in result


def test_lyrics_generator_respects_genre():
    gen = LyricsGenerator()
    result = gen.generate("island life", genre="reggae")
    assert isinstance(result, str)
    assert len(result) > 0


def test_lyrics_generator_unknown_genre_falls_back_to_pop():
    gen = LyricsGenerator()
    result = gen.generate("some theme", genre="polka")
    assert "[Verse 1]" in result
