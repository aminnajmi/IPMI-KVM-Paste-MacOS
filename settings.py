"""Persistent, user-scoped application configuration."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class AppSettings:
    delay_ms: int = 20
    countdown_seconds: int = 5
    always_on_top: bool = False
    window_width: int = 720
    window_height: int = 560
    last_text: str = ""
    randomize_delay: bool = False


class SettingsStore:
    def __init__(self) -> None:
        self.path = Path.home() / ".ipmi_paste" / "settings.json"

    def load(self) -> AppSettings:
        try:
            values = json.loads(self.path.read_text(encoding="utf-8"))
            allowed = {key: values[key] for key in AppSettings.__annotations__ if key in values}
            return AppSettings(**allowed)
        except (OSError, json.JSONDecodeError, TypeError):
            return AppSettings()

    def save(self, settings: AppSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
