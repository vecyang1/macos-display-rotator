# Requirements

## v1 Requirements

### Display Control

**REQ-DC-001: Auto-detect Second Screen**
- **Status**: Validated (existing)
- **Description**: Automatically detect and select the second (external) display as the rotation target
- **Acceptance**: System identifies external display on startup; falls back to first display if no external found
- **Notes**: Current implementation in `auto_select_target()` works reliably

**REQ-DC-002: Rotate Display on Command**
- **Status**: Validated (existing)
- **Description**: Rotate the target display to 0°, 90°, or 270° on user command
- **Acceptance**: Display rotates to specified angle within 2 seconds; visual confirmation via notification
- **Notes**: Current implementation uses displayplacer CLI tool

**REQ-DC-003: Preserve Display Arrangement**
- **Status**: Active (needs enhancement)
- **Description**: Maintain the relative position of displays in the arrangement after rotation
- **Acceptance**: After rotation, displays remain in the same spatial relationship (left/right/above/below); no manual re-arrangement needed
- **Notes**: Current implementation attempts this via layout saving/restoration but has bugs. This is the PRIMARY enhancement goal.
- **Technical**: Requires coordinate transformation after rotation; current approach saves full layout per orientation mode

**REQ-DC-004: Display Profiles**
- **Status**: Active (partial implementation)
- **Description**: Save and restore display configurations per orientation (landscape/portrait)
- **Acceptance**: System remembers last-used settings for each orientation; restores resolution, scaling, and arrangement when switching back
- **Notes**: Current implementation saves layouts per mode (landscape/portrait) but needs reliability improvements
- **Technical**: Currently stores in `~/.screen_rotator_config.json` under `layouts` key

### User Interface

**REQ-UI-001: Menu Bar Icon**
- **Status**: Validated (existing)
- **Description**: Provide menu bar icon with rotation controls
- **Acceptance**: Icon visible in menu bar; clicking shows menu with rotation options and settings
- **Notes**: Current implementation uses rumps framework with "SR" text icon

**REQ-UI-002: Global Hotkey**
- **Status**: Validated (existing)
- **Description**: Support customizable global keyboard shortcuts for rotation actions
- **Acceptance**: User can record shortcuts for toggle, 0°, 90°, 270° actions; shortcuts work system-wide even when app is in background
- **Notes**: Current implementation uses pynput with recording UI; supports modifiers + key combinations

**REQ-UI-003: Target Display Selection**
- **Status**: Validated (existing)
- **Description**: Allow manual selection of target display from menu
- **Acceptance**: Menu shows all connected displays with type (Built-in/External); selected display is marked; selection persists across restarts
- **Notes**: Current implementation lists displays with persistent IDs

### Reliability

**REQ-REL-001: Error Handling**
- **Status**: Active (needs enhancement)
- **Description**: Handle display disconnection, displayplacer failures, and invalid states gracefully
- **Acceptance**: App doesn't crash on display disconnect; shows user-friendly error messages; auto-recovers when display reconnects
- **Notes**: Current implementation has basic error handling but needs robustness improvements

**REQ-REL-002: Retry Logic**
- **Status**: Active (partial implementation)
- **Description**: Retry rotation commands if they fail initially
- **Acceptance**: System attempts rotation up to 3 times with 500ms delays; notifies user only if all attempts fail
- **Notes**: Current implementation has `wait_for_rotation()` with polling but no explicit retry on failure

**REQ-REL-003: Rotation Verification**
- **Status**: Validated (existing)
- **Description**: Verify rotation completed successfully before confirming to user
- **Acceptance**: System polls display state for up to 2 seconds; only shows success notification if rotation confirmed
- **Notes**: Current implementation uses `wait_for_rotation()` with 2-second timeout

## v2 Requirements (Deferred)

**REQ-V2-001: Multiple Display Rotation**
- **Description**: Support rotating multiple displays simultaneously
- **Rationale**: Deferred - focus on single display reliability first; rare use case

**REQ-V2-002: Rotation Animations**
- **Description**: Smooth visual transition during rotation
- **Rationale**: Deferred - instant rotation is acceptable; macOS doesn't provide animation APIs

**REQ-V2-003: Per-App Display Profiles**
- **Description**: Automatically switch display orientation based on active application
- **Rationale**: Deferred - complex automation; validate core functionality first

**REQ-V2-004: CLI Interface**
- **Description**: Command-line tool for scripting rotation
- **Rationale**: Deferred - menu bar + hotkeys cover primary use cases

**REQ-V2-005: Display Mirroring Control**
- **Description**: Toggle display mirroring from the app
- **Rationale**: Deferred - out of scope for rotation-focused tool

## Out of Scope

**OOS-001: Window Position Restoration**
- **Rationale**: macOS handles window management; preserving display arrangement is sufficient; window restoration is unreliable and fragile

**OOS-002: Custom Rotation Angles**
- **Rationale**: macOS only supports 0°, 90°, 180°, 270°; arbitrary angles not possible via CoreGraphics

**OOS-003: Primary Display Rotation**
- **Rationale**: Focus on second display only; rotating primary display causes system UI issues

**OOS-004: Display Color Calibration**
- **Rationale**: Separate concern; macOS System Settings handles this

**OOS-005: HDR/Brightness Control**
- **Rationale**: Not related to rotation; separate tool domain

## Technology Decision

**DECISION REQUIRED**: Python (existing) vs Swift (recommended by research)

**Current State**: Existing implementation is Python-based using:
- rumps (menu bar framework)
- pynput (keyboard shortcuts)
- displayplacer (external CLI tool for display control)

**Research Recommendation**: Swift + AppKit + CoreGraphics
- Native macOS integration
- Direct CoreGraphics Display Services API (no external dependencies)
- Better performance and reliability
- Modern development stack

**Options**:
1. **Enhance Python version**: Fix arrangement preservation bugs, improve error handling, keep existing architecture
2. **Rebuild in Swift**: Start fresh with native APIs, eliminate displayplacer dependency, modern codebase

**Recommendation**: Defer to Phase 1 planning. Evaluate:
- Effort to fix Python bugs vs rebuild cost
- Whether displayplacer limitations are causing arrangement issues
- User preference for maintenance vs modernization

## Traceability

| Requirement | Phase | Plan | Status |
|-------------|-------|------|--------|
| (To be populated during roadmap creation) | | | |

---
*Last updated: 2026-03-01 during new-project workflow*
