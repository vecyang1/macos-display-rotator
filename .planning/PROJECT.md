# Screen Rotate

## What This Is

A macOS utility that rotates the second display with a single click or global hotkey. Preserves the screen's position in the display arrangement and provides both menu bar and keyboard control. Replaces the existing buggy implementation in this folder.

## Core Value

One-click rotation of the second screen that works reliably every time, without breaking the display arrangement.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Auto-detect second screen and rotate it on command
- [ ] Preserve screen position in display arrangement after rotation
- [ ] Global hotkey trigger (customizable)
- [ ] Menu bar icon for manual control
- [ ] Stable rotation without bugs or crashes

### Out of Scope

- Window position restoration — macOS handles window management, we only preserve display arrangement
- Multi-screen rotation — focus on second screen only
- Rotation animations — instant rotation is fine

## Context

- Existing implementation in this folder has design issues and bugs
- User frequently needs to rotate second display for different tasks
- Current macOS System Preferences workflow is too slow (multiple clicks)
- Display arrangement (relative position of screens) must stay intact after rotation

## Constraints

- **Platform**: macOS only
- **Target**: Second display (auto-detected, not primary)
- **Reliability**: Must work consistently without requiring restarts or manual fixes

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Auto-detect second screen | User wants one-click operation without manual selection | — Pending |
| Preserve arrangement only | Window positions are macOS responsibility, focus on display arrangement | — Pending |
| Menu bar + hotkey | Flexibility for different workflows | — Pending |

---
*Last updated: 2026-03-01 after initialization*
