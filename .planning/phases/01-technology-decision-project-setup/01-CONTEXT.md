# Phase 1: Technology Decision & Project Setup - Context

**Gathered:** 2026-03-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Evaluate whether to enhance the existing Python implementation or rebuild in Swift, then establish the development environment. This is a decision phase that enables all subsequent work.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion

User has delegated full decision-making authority for this phase. Claude should:

- Evaluate Python enhancement vs Swift rebuild based on technical merit
- Consider: native API access, maintainability, performance, development velocity
- Analyze existing codebase to identify root cause of arrangement preservation bug
- Choose appropriate development environment setup
- Document decision with clear rationale

</decisions>

<code_context>
## Existing Code Insights

### Current Implementation
- **Language:** Python 3.12
- **Framework:** rumps (menu bar app), pynput (global hotkeys)
- **Display control:** displayplacer CLI (Homebrew package)
- **Packaging:** py2app → .app bundle in dist/
- **Size:** ~750 lines, well-structured
- **Config:** JSON persistence at ~/.screen_rotator_config.json

### Key Features Working
- Display detection (built-in vs external)
- Rotation to 0°, 90°, 270° via menu or hotkeys
- Layout saving per orientation mode (portrait/landscape)
- Launch at login via LaunchAgent plist
- Hotkey recording and persistence

### Known Issues
- Display arrangement not preserved after rotation (Phase 3's primary goal)
- Relies on external displayplacer CLI (Homebrew dependency)

### Architecture Patterns
- Event-driven (rumps.App base class)
- Threaded hotkey listeners
- Subprocess calls to displayplacer
- Config read/write with error handling

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

Key consideration: The arrangement preservation bug is the primary driver for this project. The technology choice should optimize for solving that issue reliably.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-technology-decision-project-setup*
*Context gathered: 2026-03-01*
