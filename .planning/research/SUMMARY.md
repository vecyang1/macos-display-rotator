# Project Research Summary

**Project:** macOS Display Rotation Utility
**Domain:** System Utility / Display Management
**Researched:** 2026-03-01
**Confidence:** MEDIUM-HIGH

## Executive Summary

This is a macOS menu bar utility for rotating external displays with one click. The core challenge is not rotation itself (CoreGraphics provides native APIs), but preserving display arrangement after rotation—macOS frequently forgets display positions when orientation changes. Expert implementations use Swift + AppKit for menu bar integration, CoreGraphics for display management, and implement arrangement preservation by capturing display bounds before rotation and restoring them within the same configuration transaction.

The recommended approach is a focused MVP: menu bar icon, auto-detect second display, rotation control with arrangement preservation, and global hotkey. This addresses the primary pain point (lost arrangements) while keeping complexity manageable. The stack is straightforward—Swift 6 + AppKit + CoreGraphics with KeyboardShortcuts library for hotkeys—all native macOS technologies with high reliability.

Key risks are display arrangement preservation reliability (macOS sometimes resets positions despite correct API usage) and race conditions during display wake/sleep events. Mitigation: implement retry logic, verify arrangement after rotation, and defer rotation attempts until display configuration is stable.

## Key Findings

### Recommended Stack

Swift 6 + AppKit provides the most direct path for macOS menu bar utilities. CoreGraphics (Quartz Display Services) is the only API for programmatic display rotation. The stack is mature and well-documented with proven reference implementations.

**Core technologies:**
- **Swift 6.0+**: Native macOS language with modern concurrency and type safety
- **AppKit (macOS 15+)**: NSStatusBar for menu bar integration, more appropriate than SwiftUI for system utilities
- **CoreGraphics**: CGDisplay* APIs for rotation and arrangement management—only way to control displays programmatically
- **KeyboardShortcuts 2.x**: Sandbox-compatible global hotkey library, wraps Carbon APIs cleanly

**Critical version requirements:** Xcode 16.4+ for Swift 6, macOS 13+ for LaunchAtLogin-Modern (optional feature).

### Expected Features

**Must have (table stakes):**
- Menu bar icon—standard for macOS utilities, all competitors have this
- Auto-detect second display—users expect "just works" behavior
- Rotation control (90°, 180°, 270°, standard)—core functionality
- Preserve display arrangement—key differentiator, solves major pain point
- Global hotkey—faster than menu bar clicking
- Basic error handling—prevents crashes on unsupported displays

**Should have (competitive):**
- Display-specific settings—remember rotation per display
- Profile switching—save/restore multiple rotation configs
- CLI interface—power users and automation
- Notification feedback—confirm rotation completed

**Defer (v2+):**
- Auto-rotation triggers—complex, defer until profiles validated
- Multi-display rotation—exponentially complex arrangement preservation
- Rotation animation—anti-feature unless proven valuable

### Architecture Approach

Standard menu bar agent app architecture with three layers: UI (NSStatusItem + MenuBarExtra), business logic (DisplayManager coordinating detection/rotation/hotkeys), and system API layer (CoreGraphics + Carbon). DisplayManager acts as coordinator, delegating to specialized components (DisplayDetector, RotationController, HotkeyManager).

**Major components:**
1. **DisplayManager**—core coordinator, orchestrates detection, rotation, and arrangement preservation
2. **RotationController**—executes rotation via CGDisplayConfigRef transaction pattern, captures/restores display bounds
3. **DisplayDetector**—enumerates displays via CGGetActiveDisplayList, identifies second screen automatically
4. **HotkeyManager**—registers global shortcuts via KeyboardShortcuts library
5. **MenuBarView**—SwiftUI interface for manual rotation trigger

**Critical pattern:** Display configuration transaction (begin/apply/commit) wraps all rotation and arrangement changes atomically. Must capture display origin before rotation and restore within same transaction.

### Critical Pitfalls

1. **Display arrangement lost after rotation**—macOS resets display positions despite correct API usage. Prevention: capture CGDisplayBounds before rotation, restore with CGConfigureDisplayOrigin in same transaction, implement verification and retry logic.

2. **Display rotation crashes System Preferences**—improper transaction handling. Prevention: always use CGDisplayConfigRef transaction pattern, call CGCompleteDisplayConfiguration, handle errors gracefully.

3. **Race conditions on display wake/sleep**—rotation fails intermittently after display wake. Prevention: listen for display reconfiguration notifications (CGDisplayRegisterReconfigurationCallback), defer rotation until configuration is stable.

4. **Missing rotation support detection**—app crashes when display doesn't support requested rotation. Prevention: query available display modes via CGDisplayCopyAllDisplayModes before attempting rotation.

5. **Global hotkey conflicts**—hotkey doesn't work or triggers other apps. Prevention: use KeyboardShortcuts library with conflict detection, make hotkey customizable.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Core Rotation Engine
**Rationale:** Foundation for all features. Must be rock-solid before adding UI or convenience features.
**Delivers:** Display detection, rotation execution, basic error handling
**Addresses:** Auto-detect displays, rotation control, error handling (FEATURES.md)
**Avoids:** Missing rotation support detection, display crashes (PITFALLS.md)
**Research flag:** Standard patterns, skip research-phase

### Phase 2: Arrangement Preservation
**Rationale:** Key differentiator, but depends on Phase 1 rotation working reliably. Complex coordinate recalculation.
**Delivers:** Capture/restore display bounds, arrangement verification
**Addresses:** Preserve display arrangement (FEATURES.md—primary value prop)
**Avoids:** Display arrangement lost after rotation (PITFALLS.md—highest severity)
**Research flag:** Needs research-phase—complex geometry, macOS quirks

### Phase 3: Menu Bar Interface
**Rationale:** User-facing layer, depends on Phases 1-2 working. Straightforward AppKit implementation.
**Delivers:** NSStatusItem, menu bar popover, manual rotation trigger
**Addresses:** Menu bar icon (FEATURES.md—table stakes)
**Avoids:** Blocking main thread during rotation (PITFALLS.md)
**Research flag:** Standard patterns, skip research-phase

### Phase 4: Global Hotkey
**Rationale:** Enhances Phase 3 UI, independent of core rotation logic. KeyboardShortcuts library simplifies implementation.
**Delivers:** Global keyboard shortcut registration, hotkey handler
**Addresses:** Global hotkey (FEATURES.md—differentiator)
**Avoids:** Hotkey conflicts (PITFALLS.md)
**Research flag:** Standard patterns, skip research-phase

### Phase 5: Polish & Error Handling
**Rationale:** Final hardening after core features work. Addresses edge cases discovered during testing.
**Delivers:** Retry logic, display wake/sleep handling, user feedback
**Addresses:** Notification feedback (FEATURES.md)
**Avoids:** Race conditions on wake/sleep (PITFALLS.md)
**Research flag:** Needs research-phase—macOS display event system

### Phase Ordering Rationale

- **Phase 1 first:** Core rotation must work before arrangement preservation can be tested
- **Phase 2 before UI:** Arrangement preservation is the key differentiator; validate it works before building UI
- **Phase 3 before hotkey:** Menu bar interface is table stakes; hotkey enhances it
- **Phase 5 last:** Polish requires real-world testing of Phases 1-4 to identify edge cases

This ordering minimizes rework—each phase builds on validated foundations. Arrangement preservation (Phase 2) is isolated as highest-risk component.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (Arrangement Preservation):** Complex coordinate geometry, macOS-specific quirks, sparse documentation on edge cases
- **Phase 5 (Error Handling):** Display event system poorly documented, need to research CGDisplayRegisterReconfigurationCallback patterns

Phases with standard patterns (skip research-phase):
- **Phase 1 (Core Rotation):** Well-documented CoreGraphics APIs, proven reference implementations (displayplacer)
- **Phase 3 (Menu Bar Interface):** Standard AppKit patterns, extensive documentation
- **Phase 4 (Global Hotkey):** KeyboardShortcuts library handles complexity, straightforward integration

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Official Apple APIs, proven reference implementations, mature libraries |
| Features | MEDIUM | Competitor analysis solid, but user validation needed for prioritization |
| Architecture | MEDIUM | Standard patterns identified, but arrangement preservation complexity not fully explored |
| Pitfalls | MEDIUM | Top issues identified from community discussions, but edge cases likely exist |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Arrangement preservation edge cases:** Research identified the problem and general solution, but specific coordinate recalculation logic for all rotation angles needs validation during Phase 2 planning
- **Display wake/sleep event handling:** CGDisplayRegisterReconfigurationCallback mentioned but implementation pattern unclear—needs deeper research in Phase 5
- **Multi-display scenarios:** Research focused on single second display; behavior with 3+ displays undefined—defer to post-MVP
- **macOS version compatibility:** Research assumes macOS 15+; older version quirks not explored—acceptable for new project

## Sources

### Primary (HIGH confidence)
- [Apple Developer: CoreGraphics Display Services](https://developer.apple.com/documentation/coregraphics/quartz_display_services) — Official API documentation
- [jakehilborn/displayplacer](https://github.com/jakehilborn/displayplacer) — Proven reference implementation
- [sindresorhus/KeyboardShortcuts](https://github.com/sindresorhus/KeyboardShortcuts) — Official library documentation
- [nonstrict.eu: Display reconfigurations on macOS](https://nonstrict.eu/blog/2023/display-reconfigurations-on-macos) — CoreGraphics patterns

### Secondary (MEDIUM confidence)
- [Building a MacOS Menu Bar App with Swift](https://bytegoblin.io/blog/building-a-macos-menu-bar-app-with-swift) — Architecture patterns
- [nilcoalescing.com: Build a macOS menu bar utility](https://nilcoalescing.com/blog/BuildAMacOSMenuBarUtilityInSwiftUI) — MenuBarExtra implementation
- [Apple Discussions: Display arrangement issues](https://discussions.apple.com/thread/253841249) — User pain points
- Competitor analysis: Display Rotation Menu, displayplacer, SwitchResX, BetterDisplay

### Tertiary (LOW confidence)
- Web search results on Swift Package Manager best practices
- Community discussions on rotation workflows

---
*Research completed: 2026-03-01*
*Ready for roadmap: yes*
