"""Threaded, interruptible typing engine."""
from __future__ import annotations

from threading import Condition, Event, Thread
from time import monotonic
from typing import Callable

from keyboard import KeyboardInjector


class TypingEngine:
    """Types text sequentially without blocking the Qt event loop."""

    def __init__(self, on_progress: Callable[[int, int, float], None],
                 on_finished: Callable[[str, str | None], None]) -> None:
        self._on_progress = on_progress
        self._on_finished = on_finished
        self._pause_condition = Condition()
        self._paused = False
        self._stop = Event()
        self._thread: Thread | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self, text: str, delay_ms: int) -> None:
        if self.running:
            raise RuntimeError("Typing is already in progress")
        self._stop.clear()
        self._paused = False
        self._thread = Thread(target=self._run, args=(text, delay_ms), daemon=True)
        self._thread.start()

    def pause(self) -> None:
        with self._pause_condition:
            self._paused = True

    def resume(self) -> None:
        with self._pause_condition:
            self._paused = False
            self._pause_condition.notify_all()

    def stop(self) -> None:
        self._stop.set()
        self.resume()

    def _wait_if_paused(self) -> bool:
        with self._pause_condition:
            while self._paused and not self._stop.is_set():
                self._pause_condition.wait(timeout=0.15)
        return not self._stop.is_set()

    def _run(self, text: str, delay_ms: int) -> None:
        injector: KeyboardInjector | None = None
        started = monotonic()
        try:
            injector = KeyboardInjector()
            total = len(text)
            for index, char in enumerate(text, start=1):
                if not self._wait_if_paused():
                    self._on_finished("Stopped", None)
                    return
                injector.type_character(char)
                elapsed = max(monotonic() - started, 0.001)
                self._on_progress(index, total, elapsed)
                if self._stop.wait(delay_ms / 1000):
                    self._on_finished("Stopped", None)
                    return
            self._on_finished("Completed", None)
        except Exception as exc:  # Surface unexpected API failures safely.
            self._on_finished("Error", str(exc))
        finally:
            try:
                if injector is not None:
                    injector.release_modifiers()
            except OSError:
                pass
