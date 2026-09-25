# Universal IPMI Paste

A macOS desktop utility that types text into the focused IPMI/KVM console where normal clipboard paste is unavailable. It sends hardware-style Quartz keyboard events, which work with many browser and Java console implementations.

## Run on macOS

```bash
cd /Users/aminm/Documents/projects/Github/IPMI-KVM-Paste
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

On first use, grant **Accessibility** permission to Terminal (when running from source) or to **Universal IPMI Paste** (when launching the packaged app): **System Settings → Privacy & Security → Accessibility**. Grant **Input Monitoring** too if you want global hotkeys. Quit and reopen the app after changing these permissions.

## Use

1. Enter or load text and choose the delay (milliseconds per character).
2. Select **Paste**, then focus the destination console during the countdown.
3. The application sends each character as a keyboard event; it never sends clipboard paste commands.

Global hotkeys are Command+Shift+F8 Start, F9 Pause, F10 Resume, and F11 Stop. They continue working when the app is minimized. On compact Mac keyboards, hold `fn` with F9–F11 if your function keys control media by default. Settings and activity logs are stored under `~/.ipmi_paste`.

## Package

After installing requirements, execute:

```bash
chmod +x build-macos.sh
./build-macos.sh
```

The app bundle is created at `dist/Universal IPMI Paste.app`. You can move that bundle into `/Applications`.

## Notes

This build uses the ANSI/US physical keyboard layout for ASCII characters. Non-ASCII characters are sent as macOS Unicode events; whether a remote KVM accepts those is determined by the KVM implementation.

## Powered by graphify for easier development
<img width="1395" height="957" alt="Screenshot 2026-09-25 at 20 10 58" src="https://github.com/user-attachments/assets/38c3cfa5-98af-48fc-968f-674f0394c665" />
