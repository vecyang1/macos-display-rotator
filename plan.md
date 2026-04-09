# 📐 ScreenRotator - Technical Plan

> Reverse-engineered from current codebase baseline.

## 1. Technology Stack
- **Language**: Python 3.x
- **GUI Framework**: `rumps` (Cocoa wrapper for macOS menu bar)
- **Keyboard Listener**: `pynput` (for Global Hotkeys intercept without focused context)
- **Display Engine**: `displayplacer` CLI via brew (used via Python `subprocess`)

## 2. Architecture & Data Flow

### 2.1 The Application Core (`screen_rotator.py`)
Provides the runtime orchestrator tracking active displays, hotkey states, and executing the main Loop.

### 2.2 Concurrency & Subprocesses
- Since `displayplacer` execution can be heavy and take hundreds of milliseconds or seconds, all `subprocess.run` executions **MUST** be offloaded to a designated Python `threading.Thread`.
- A global `threading.Lock()` must ensure multiple rapid rotations do not overlap and crash the windowserver.

### 2.3 Data Models
- **Shortcuts Record**: Stored locally (often in JSON or memory dict depending on implementation) linking `{action_id: key_combo_array}`.
- **Display Metadata**: Parsed dynamically from `displayplacer list`. Look up active dimensions and current degree values.

### 2.4 Extensibility
- Custom presets are managed. Future improvements should rely on extending the dict serialization of `pynput` bindings rather than hard-coding classes.

## 3. Contracts
- `GET /system/displays`: Parsed by scraping stdout of `displayplacer list`. Expected text blocks map `id:` to display tokens.
- `EXEC /system/displays`: Called via `displayplacer "id=<ID> degree=<DEG> origin=(x,y)"`.
