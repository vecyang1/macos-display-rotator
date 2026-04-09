# 📜 ScreenRotator Project Constitution

These are the immutable principles governing this project's development. All features and architectural decisions must align with these rules.

## 1. Local & Privacy First 🛡️
- No usage telemetry, tracking, or network callbacks are permitted.
- Execution must happen 100% locally.

## 2. Zero-Latency Concurrency ⚡
- UI events and background tasks must be strictly decoupled.
- Complex operations (e.g., executing `displayplacer` subprocesses) must run in isolated thread-locks to prevent macOS "beachball" hangs.
- Timeout limits (max 10 seconds) must be enforced on all subprocess calls.

## 3. macOS Native Adherence 🖥️
- Utilize `rumps` for native Cocoa integration, maintaining the standard macOS Menu Bar paradigm.
- Prefer system observers where possible. State synchronization must read from the system, not just expect the system to conform to app state.

## 4. Operational Stability 🧱
- Hotkeys must register globally through `pynput` while checking for Accessibility permissions gracefully.
- Do not let duplicate keys crash the listener map. Error handling must fail gracefully with UI-level warnings.
