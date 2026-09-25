# Graph Report - IPMI-KVM-Paste-MacOS  (2026-09-24)

## Corpus Check
- 12 files · ~2,462 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .spec 1)

## Summary
- 112 nodes · 163 edges · 12 communities (5 shown, 7 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f8fcaf0d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Application Support
- Settings and Logging
- Main Window Workflow
- IPMI Console Concepts
- Keyboard Injection
- Typing Engine
- Global Hotkeys
- macOS Input APIs
- Packaging and Build
- Package Metadata
- Clipboard Concepts

## God Nodes (most connected - your core abstractions)
1. `MainWindow` - 23 edges
2. `TypingEngine` - 14 edges
3. `KeyboardInjector` - 13 edges
4. `Universal IPMI Paste` - 12 edges
5. `GlobalHotkeys` - 10 edges
6. `SettingsStore` - 7 edges
7. `AppSettings` - 6 edges
8. `SettingsDialog` - 5 edges
9. `Quartz keyboard events` - 5 edges
10. `create_logger()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `MainWindow` --uses--> `GlobalHotkeys`  [INFERRED]
  gui.py → hotkeys.py
- `MainWindow` --uses--> `SettingsStore`  [INFERRED]
  gui.py → settings.py
- `MainWindow` --uses--> `TypingEngine`  [INFERRED]
  gui.py → typing_engine.py
- `main()` --calls--> `MainWindow`  [EXTRACTED]
  main.py → gui.py
- `TypingEngine` --uses--> `KeyboardInjector`  [INFERRED]
  typing_engine.py → keyboard.py

## Import Cycles
- None detected.

## Communities (12 total, 7 thin omitted)

### Community 0 - "Application Support"
Cohesion: 0.12
Nodes (16): datetime, PySide6 user interface for IPMI Paste., Global hotkeys implemented with pynput on macOS and Windows., main(), Application entry point., pynput, pyside6_qtcore, pyside6_qtgui (+8 more)

### Community 1 - "Settings and Logging"
Cohesion: 0.13
Nodes (13): dataclasses, SettingsDialog, json, Logger, create_logger(), Application activity logging., logging, pathlib (+5 more)

### Community 2 - "Main Window Workflow"
Cohesion: 0.17
Nodes (4): MainWindow, Choose an action-button arrangement based on available width., QCloseEvent, QMainWindow

### Community 3 - "IPMI Console Concepts"
Cohesion: 0.20
Nodes (14): Accessibility permission, ANSI/US physical keyboard layout, Browser implementations, Global hotkeys, Input Monitoring, IPMI/KVM console, Java console implementations, macOS (+6 more)

### Community 7 - "macOS Input APIs"
Cohesion: 0.40
Nodes (4): appkit, applicationservices, macOS keyboard injection for the currently focused application., quartz

## Knowledge Gaps
- **8 isolated node(s):** `build-macos.sh script`, `PYINSTALLER_CONFIG_DIR`, `Clipboard paste`, `Accessibility permission`, `macOS` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 51 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MainWindow` connect `Main Window Workflow` to `Application Support`, `Settings and Logging`, `Typing Engine`, `Global Hotkeys`?**
  _High betweenness centrality (0.250) - this node is a cross-community bridge._
- **Why does `TypingEngine` connect `Typing Engine` to `Application Support`, `Settings and Logging`, `Main Window Workflow`, `Keyboard Injection`?**
  _High betweenness centrality (0.213) - this node is a cross-community bridge._
- **Why does `KeyboardInjector` connect `Keyboard Injection` to `Application Support`, `Typing Engine`, `macOS Input APIs`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `MainWindow` (e.g. with `GlobalHotkeys` and `SettingsStore`) actually correct?**
  _`MainWindow` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `TypingEngine` (e.g. with `MainWindow` and `KeyboardInjector`) actually correct?**
  _`TypingEngine` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Universal IPMI Paste` (e.g. with `pynput` and `PySide6`) actually correct?**
  _`Universal IPMI Paste` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `build-macos.sh script`, `PYINSTALLER_CONFIG_DIR`, `Clipboard paste` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._