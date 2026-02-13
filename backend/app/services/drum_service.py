from __future__ import annotations

from inference.generate_drums import generate_drum_pattern


def create_drum_pattern() -> list[dict[str, bool | int]]:
    """Wrapper used by FastAPI endpoints to generate drum sequences."""
    return generate_drum_pattern()

__all__ = ["create_drum_pattern"]
