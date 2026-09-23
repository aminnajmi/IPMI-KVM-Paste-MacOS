"""Global hotkeys implemented with pynput on macOS and Windows."""
from __future__ import annotations

import sys
from typing import Callable

from pynput import keyboard


class GlobalHotkeys:
    """Listen for Command+Shift+F8 (macOS) or Ctrl+Shift+F8 (Windows)."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        self._callback = callback
        self._listener: keyboard.Listener | None = None
        self._modifiers: set[object] = set()

    def start(self) -> None:
        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()

    def close(self) -> None:
        if self._listener:
            self._listener.stop()

    def _on_press(self, key: object) -> None:
        modifiers = (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r,
                     keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
                     keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r)
        if key in modifiers:
            self._modifiers.add(key)
            return
        shortcut_modifiers = modifiers[:3] if sys.platform == "darwin" else modifiers[3:6]
        command_or_control = any(modifier in self._modifiers for modifier in shortcut_modifiers)
        shift = any(modifier in self._modifiers for modifier in modifiers[6:])
        if key == keyboard.Key.f8 and command_or_control and shift: self._callback("start")
        elif key == keyboard.Key.f9: self._callback("pause")
        elif key == keyboard.Key.f10: self._callback("resume")
        elif key == keyboard.Key.f11: self._callback("stop")

    def _on_release(self, key: object) -> None:
        self._modifiers.discard(key)
