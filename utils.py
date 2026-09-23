"""Small shared presentation helpers."""
from __future__ import annotations


def format_remaining(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d} remaining"
