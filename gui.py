"""PySide6 user interface for IPMI Paste."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from time import monotonic

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout,
    QGridLayout, QHBoxLayout, QLabel, QMainWindow, QMenu, QMessageBox,
    QPlainTextEdit, QProgressBar, QPushButton, QSizePolicy, QSpinBox,
    QStatusBar, QSystemTrayIcon, QVBoxLayout, QWidget,
)

from hotkeys import GlobalHotkeys
from logger import create_logger
from settings import AppSettings, SettingsStore
from typing_engine import TypingEngine
from utils import format_remaining

DARK_STYLE = """
QWidget { background: #1e2127; color: #e5e7eb; }
QPlainTextEdit, QComboBox, QSpinBox { background: #282c34; border: 1px solid #444b57; border-radius: 5px; padding: 5px; }
QPushButton { background: #303744; border: 1px solid #4a5568; border-radius: 5px; padding: 6px 8px; }
QPushButton:hover { background: #3b4556; } QPushButton:disabled { color: #77808c; }
QProgressBar { border: 1px solid #444b57; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background: #3b82f6; border-radius: 3px; }
"""


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        layout = QFormLayout(self)
        self.countdown = QSpinBox(); self.countdown.setRange(0, 30); self.countdown.setValue(settings.countdown_seconds)
        self.topmost = QCheckBox("Keep this window above others"); self.topmost.setChecked(settings.always_on_top)
        layout.addRow("Countdown (seconds)", self.countdown)
        layout.addRow("Always on top", self.topmost)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        layout.addRow(buttons)


class MainWindow(QMainWindow):
    progress_signal = Signal(int, int, float)
    finished_signal = Signal(str, object)
    hotkey_signal = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.store = SettingsStore()
        self.settings = self.store.load()
        self.log = create_logger()
        self._countdown = self.settings.countdown_seconds
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._countdown_tick)
        self._started_at = 0.0
        self._typed_text = ""
        self._typed_count = 0
        self._line_ending = "\r\n"
        self.engine = TypingEngine(self.progress_signal.emit, self.finished_signal.emit)
        self.hotkeys = GlobalHotkeys(self.hotkey_signal.emit)
        self._build_ui()
        if self.settings.always_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.progress_signal.connect(self._update_progress)
        self.finished_signal.connect(self._finished)
        self.hotkey_signal.connect(self._handle_hotkey)
        self.hotkeys.start()

    def _build_ui(self) -> None:
        self.setWindowTitle("Universal IPMI Paste")
        self.resize(self.settings.window_width, self.settings.window_height)
        self.setMinimumSize(320, 360)
        self.setStyleSheet(DARK_STYLE)
        root = QWidget(); layout = QVBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 10); layout.setSpacing(6)
        layout.addWidget(QLabel("Text to type into the focused console"))
        self.editor = QPlainTextEdit(); self.editor.setPlainText(self.settings.last_text)
        self.editor.setPlaceholderText("Paste or type text here. Line breaks and tabs are preserved.")
        self.editor.setMinimumHeight(150)
        self.editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.editor, 1)
        controls = QVBoxLayout(); controls.setSpacing(4)
        speed_row = QHBoxLayout(); speed_row.setSpacing(4)
        self.speed = QComboBox()
        for label, value in (("Very Fast (5 ms)", 5), ("Fast (10 ms)", 10), ("Normal (20 ms)", 20), ("Slow (50 ms)", 50), ("Very Slow (100 ms)", 100)):
            self.speed.addItem(label, value)
        self.custom_delay = QSpinBox(); self.custom_delay.setRange(1, 5000); self.custom_delay.setSuffix(" ms")
        self.custom_delay.setValue(self.settings.delay_ms)
        index = self.speed.findData(self.settings.delay_ms)
        if index >= 0: self.speed.setCurrentIndex(index)
        self.speed.currentIndexChanged.connect(lambda: self.custom_delay.setValue(int(self.speed.currentData())))
        speed_row.addWidget(QLabel("Speed")); speed_row.addWidget(self.speed); speed_row.addWidget(self.custom_delay)
        speed_row.addStretch()
        controls.addLayout(speed_row)
        shortcut = "⌘⇧F8" if sys.platform == "darwin" else "Ctrl+Shift+F8"
        self.paste_button = QPushButton(f"Paste ({shortcut})"); self.stop_button = QPushButton("Stop (F11)")
        self.clear_button = QPushButton("Clear"); self.load_button = QPushButton("Load from File"); self.save_button = QPushButton("Save Text"); self.settings_button = QPushButton("Settings")
        self.action_buttons = (self.paste_button, self.stop_button, self.clear_button,
                               self.load_button, self.save_button, self.settings_button)
        for button in self.action_buttons:
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.more_button = QPushButton("More ▾")
        self.more_menu = QMenu(self)
        self.more_button.setMenu(self.more_menu)
        self.more_menu.addAction("Stop", self.stop)
        self.more_menu.addAction("Clear", self.editor.clear)
        self.more_menu.addAction("Load from File", self.load_file)
        self.more_menu.addAction("Save Text", self.save_file)
        self.more_menu.addAction("Settings", self.open_settings)
        self.actions_host = QWidget()
        self.actions_layout = QGridLayout(self.actions_host)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setSpacing(4)
        self._action_mode = ""
        controls.addWidget(self.actions_host)
        layout.addLayout(controls)
        self.progress = QProgressBar(); self.progress.setRange(0, 100); layout.addWidget(self.progress)
        self.details = QLabel("0 / 0 characters")
        self.details.setMinimumWidth(0)
        self.details.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.status = QStatusBar(); self.status.addWidget(self.details); self.status.showMessage("Ready")
        self.setStatusBar(self.status); self.setCentralWidget(root)
        self.paste_button.clicked.connect(self.begin_countdown); self.stop_button.clicked.connect(self.stop)
        self.clear_button.clicked.connect(self.editor.clear); self.load_button.clicked.connect(self.load_file); self.save_button.clicked.connect(self.save_file); self.settings_button.clicked.connect(self.open_settings)
        self._update_action_layout()
        self._create_tray()

    def _update_action_layout(self) -> None:
        """Choose an action-button arrangement based on available width."""
        available_width = self.actions_host.width()
        if available_width <= 0:
            return
        spacing = self.actions_layout.spacing()
        button_widths = [button.sizeHint().width() for button in self.action_buttons]
        large_width = sum(button_widths) + spacing * (len(button_widths) - 1)
        medium_width = max(
            sum(button_widths[:3]),
            sum(button_widths[3:]),
            max(button_widths) * 3,
        ) + spacing * 2
        if available_width >= large_width:
            mode = "large"
        elif available_width >= medium_width:
            mode = "medium"
        else:
            mode = "compact"
        if mode == self._action_mode:
            return
        while self.actions_layout.count():
            self.actions_layout.takeAt(0)
        for button in (*self.action_buttons, self.more_button):
            button.hide()
        if mode == "large":
            for column, button in enumerate(self.action_buttons):
                self.actions_layout.addWidget(button, 0, column)
                self.actions_layout.setColumnStretch(column, 1)
                button.show()
        elif mode == "medium":
            for index, button in enumerate(self.action_buttons):
                row, column = divmod(index, 3)
                self.actions_layout.addWidget(button, row, column)
                self.actions_layout.setColumnStretch(column, 1)
                button.show()
        else:
            self.actions_layout.addWidget(self.paste_button, 0, 0)
            self.actions_layout.addWidget(self.more_button, 0, 1)
            self.actions_layout.setColumnStretch(0, 1)
            self.paste_button.show()
            self.more_button.show()
        self._action_mode = mode

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_action_layout)

    def _create_tray(self) -> None:
        tray = QSystemTrayIcon(self)
        menu = tray.contextMenu() or None
        # A tray without an icon is not useful on all systems; keep application behavior simple.
        self.tray = tray

    def begin_countdown(self) -> None:
        if self.engine.running or self._countdown_timer.isActive(): return
        if not self.editor.toPlainText():
            QMessageBox.information(self, "No text", "Enter or load text before starting."); return
        self._countdown = self.settings.countdown_seconds
        if not self._countdown: self._start_typing(); return
        self.status.showMessage(f"Focus your IPMI window — starting in {self._countdown}")
        self.paste_button.setEnabled(False); self._countdown_timer.start(1000)

    def _countdown_tick(self) -> None:
        self._countdown -= 1
        if self._countdown <= 0:
            self._countdown_timer.stop(); self._start_typing()
        else: self.status.showMessage(f"Focus your IPMI window — starting in {self._countdown}")

    def _start_typing(self) -> None:
        self._typed_text = self.editor.toPlainText()
        self._typed_count = 0
        self._started_at = monotonic(); self.progress.setValue(0)
        self.paste_button.setEnabled(False); self.status.showMessage("Typing...")
        delay = self.custom_delay.value()
        self.log.info("Start: characters=%d delay_ms=%d", len(self._typed_text), delay)
        try: self.engine.start(self._typed_text, delay)
        except Exception as exc: self._finished("Error", str(exc))

    def stop(self) -> None:
        if self._countdown_timer.isActive():
            self._countdown_timer.stop(); self.paste_button.setEnabled(True); self.status.showMessage("Stopped")
        elif self.engine.running:
            self.engine.stop(); self.status.showMessage("Stopping...")

    def _update_progress(self, current: int, total: int, elapsed: float) -> None:
        self._typed_count = current
        percent = int(current * 100 / total) if total else 0
        rate = current / elapsed
        remaining = (total - current) / rate if rate else 0
        self.progress.setValue(percent)
        self.details.setText(f"{current:,} / {total:,} characters • {rate:.1f} chars/s • {format_remaining(remaining)}")

    def _finished(self, state: str, error: object) -> None:
        duration = monotonic() - self._started_at
        self.paste_button.setEnabled(True); self.status.showMessage(state)
        self.log.info("Finish: state=%s characters=%d duration=%.2fs error=%s", state, self._typed_count, duration, error)
        if error: QMessageBox.critical(self, "Typing error", str(error))

    def _handle_hotkey(self, action: str) -> None:
        if action == "start": self.begin_countdown()
        elif action == "pause" and self.engine.running: self.engine.pause(); self.status.showMessage("Paused")
        elif action == "resume" and self.engine.running: self.engine.resume(); self.status.showMessage("Typing...")
        elif action == "stop": self.stop()

    def load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load text", "", "Text files (*.txt);;All files (*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8", newline="") as file:
                    content = file.read()
                self._line_ending = "\r\n" if "\r\n" in content else "\r" if "\r" in content else "\n"
                self.editor.setPlainText(content)
            except OSError as exc: QMessageBox.critical(self, "Load failed", str(exc))

    def save_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save text", "paste.txt", "Text files (*.txt)")
        if path:
            try:
                text = self.editor.toPlainText().replace("\n", self._line_ending)
                with open(path, "w", encoding="utf-8", newline="") as file: file.write(text)
            except OSError as exc: QMessageBox.critical(self, "Save failed", str(exc))

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            self.settings.countdown_seconds = dialog.countdown.value(); self.settings.always_on_top = dialog.topmost.isChecked()
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.settings.always_on_top); self.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.settings.delay_ms = self.custom_delay.value(); self.settings.window_width = self.width(); self.settings.window_height = self.height(); self.settings.last_text = self.editor.toPlainText()
        self.store.save(self.settings); self.hotkeys.close(); event.accept()
