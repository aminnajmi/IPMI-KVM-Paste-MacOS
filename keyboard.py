"""macOS keyboard injection for the currently focused application."""
from __future__ import annotations

from time import sleep

try:
    from ApplicationServices import (
        AXIsProcessTrusted,
        AXIsProcessTrustedWithOptions,
        kAXTrustedCheckOptionPrompt,
    )
    from AppKit import NSWorkspace
    import Quartz
except ImportError as exc:
    raise RuntimeError("macOS support requires PyObjC. Run `python3 -m pip install -r requirements.txt`.") from exc

# ANSI (US) Mac virtual-key codes. Physical events work better with remote KVM
# consoles than Unicode events, which are used only as a fallback.
_KEYS = {
    "a": 0, "s": 1, "d": 2, "f": 3, "h": 4, "g": 5, "z": 6, "x": 7, "c": 8, "v": 9,
    "b": 11, "q": 12, "w": 13, "e": 14, "r": 15, "y": 16, "t": 17, "1": 18, "2": 19,
    "3": 20, "4": 21, "6": 22, "5": 23, "=": 24, "9": 25, "7": 26, "-": 27, "8": 28,
    "0": 29, "]": 30, "o": 31, "u": 32, "[": 33, "i": 34, "p": 35, "l": 37, "j": 38,
    "'": 39, "k": 40, ";": 41, "\\": 42, ",": 43, "/": 44, "n": 45, "m": 46, ".": 47,
    " ": 49, "`": 50,
}
_SHIFTED = {"!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6", "&": "7", "*": "8", "(": "9", ")": "0", "_": "-", "+": "=", "{": "[", "}": "]", "|": "\\", ":": ";", '"': "'", "<": ",", ">": ".", "?": "/", "~": "`"}
_MODIFIER_KEYS = (56, 59, 58, 55)  # shift, control, option, command
_SHIFT_SETTLE_SECONDS = 0.01
_BROWSER_BUNDLE_IDS = {
    "com.apple.Safari",
    "com.google.Chrome",
    "org.mozilla.firefox",
    "com.microsoft.Edge",
    "com.brave.Browser",
    "com.operasoftware.Opera",
}


class KeyboardInjector:
    """Posts hardware-style keyboard events at the macOS HID event tap.

    macOS requires Accessibility permission before other apps can receive the
    events. Focus the target KVM window before the countdown reaches zero.
    """

    def __init__(self) -> None:
        if not AXIsProcessTrusted():
            AXIsProcessTrustedWithOptions({kAXTrustedCheckOptionPrompt: True})
            raise RuntimeError(
                "macOS blocked keyboard input. Enable Accessibility for this app "
                "in System Settings > Privacy & Security > Accessibility, then "
                "quit and reopen Universal IPMI Paste."
            )
        self._browser_target = False
        try:
            frontmost = NSWorkspace.sharedWorkspace().frontmostApplication()
            bundle_id = frontmost.bundleIdentifier() if frontmost else None
            self._browser_target = bundle_id in _BROWSER_BUNDLE_IDS
        except Exception:
            pass

    def _post(self, keycode: int, key_down: bool, flags: int = 0) -> None:
        event = Quartz.CGEventCreateKeyboardEvent(None, keycode, key_down)
        if flags:
            Quartz.CGEventSetFlags(event, flags)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def _tap(self, keycode: int) -> None:
        self._post(keycode, True); self._post(keycode, False)

    def _tap_with_shift(self, keycode: int) -> None:
        shift = Quartz.kCGEventFlagMaskShift
        self._post(56, True)
        sleep(_SHIFT_SETTLE_SECONDS)
        self._post(keycode, True, shift)
        self._post(keycode, False, shift)
        sleep(_SHIFT_SETTLE_SECONDS)
        self._post(56, False)

    def _type_unicode(self, char: str, keycode: int = 0) -> None:
        for key_down in (True, False):
            event = Quartz.CGEventCreateKeyboardEvent(None, keycode, key_down)
            Quartz.CGEventKeyboardSetUnicodeString(event, len(char), char)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    @staticmethod
    def _keycode_for_character(char: str) -> int:
        if char.isascii() and char.isalpha():
            return _KEYS[char.lower()]
        if char in _KEYS:
            return _KEYS[char]
        if char in _SHIFTED:
            return _KEYS[_SHIFTED[char]]
        return 0

    def type_character(self, char: str) -> None:
        if char == "\n": self._tap(36); return  # Return
        if char == "\t": self._tap(48); return  # Tab
        if char == "\r": return
        if self._browser_target and char.isprintable() and not char.isascii():
            self._type_unicode(char, self._keycode_for_character(char))
            return
        if char.isascii() and char.isalpha():
            self._tap_with_shift(_KEYS[char.lower()]) if char.isupper() else self._tap(_KEYS[char])
        elif char in _KEYS: self._tap(_KEYS[char])
        elif char in _SHIFTED: self._tap_with_shift(_KEYS[_SHIFTED[char]])
        else: self._type_unicode(char)

    def release_modifiers(self) -> None:
        for keycode in _MODIFIER_KEYS: self._post(keycode, False)
