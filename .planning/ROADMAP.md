# Roadmap

**Project:** Screen Rotate
**Created:** 2026-03-01
**Depth:** Comprehensive
**Mode:** YOLO

## Phases

- [x] **Phase 1: Technology Decision & Project Setup** - Evaluate Python enhancement vs Swift rebuild and establish development foundation
- [x] **Phase 2: Core Rotation Engine** - Ensure reliable display detection and rotation execution
- [x] **Phase 3: Arrangement Preservation** - Fix display position preservation after rotation (primary value)
- [x] **Phase 4: Display Profiles** - Save and restore configurations per orientation
- [x] **Phase 5: Error Handling & Reliability** - Implement retry logic, verification, and edge case handling
- [x] **Phase 6: UI Polish & Integration** - Refine menu bar, hotkey, and display selection features

## Phase Details

### Phase 1: Technology Decision & Project Setup
**Goal**: Establish whether to enhance Python implementation or rebuild in Swift, and set up development environment

**Depends on**: Nothing (first phase)

**Requirements**: (Decision phase - enables all other requirements)

**Success Criteria** (what must be TRUE):
1. Technology choice documented with clear rationale (Python enhancement vs Swift rebuild)
2. Development environment configured and verified working
3. Build/test workflow established (can compile and run the app)
4. Existing codebase analyzed with specific bugs and enhancement points identified

**Plans**:
- [x] Plan 01: Analyze Existing Python Implementation (Wave 1) - ✅ Complete (3/3 tasks)
- [x] Plan 02: Make Technology Decision and Document (Wave 2) - ✅ Complete (3/3 tasks)

---

### Phase 2: Core Rotation Engine
**Goal**: Users can reliably rotate the second display to any supported angle

**Depends on**: Phase 1

**Requirements**: REQ-DC-001, REQ-DC-002, REQ-REL-003

**Success Criteria** (what must be TRUE):
1. System automatically detects second (external) display on startup
2. User can rotate display to 0°, 90°, 180°, or 270° via menu command
3. Rotation completes within 2 seconds with visual confirmation
4. System verifies rotation completed successfully before confirming to user
5. Unsupported displays are detected and handled gracefully (no crashes)

**Plans**: TBD

---

### Phase 3: Arrangement Preservation
**Goal**: Display arrangement (relative position of screens) remains intact after rotation

**Depends on**: Phase 2

**Requirements**: REQ-DC-003

**Success Criteria** (what must be TRUE):
1. After rotating second display, it remains in the same spatial relationship to primary display (left/right/above/below)
2. User does not need to manually re-arrange displays in System Settings after rotation
3. Arrangement preservation works for all rotation angles (0°, 90°, 180°, 270°)
4. System verifies arrangement after rotation and retries if position was lost

**Plans**: TBD

---

### Phase 4: Display Profiles
**Goal**: System remembers and restores display settings per orientation mode

**Depends on**: Phase 3

**Requirements**: REQ-DC-004

**Success Criteria** (what must be TRUE):
1. System saves display configuration (resolution, scaling, arrangement) when user rotates to landscape
2. System saves display configuration when user rotates to portrait
3. When switching back to previously-used orientation, system restores saved configuration automatically
4. Profiles persist across app restarts

**Plans**: TBD

---

### Phase 5: Error Handling & Reliability
**Goal**: App handles edge cases and failures gracefully without crashes

**Depends on**: Phase 2, Phase 3

**Requirements**: REQ-REL-001, REQ-REL-002

**Success Criteria** (what must be TRUE):
1. App continues running when display is disconnected (no crash)
2. App shows user-friendly error messages for rotation failures
3. System retries failed rotation commands up to 3 times before reporting failure
4. App auto-recovers when disconnected display reconnects
5. Display wake/sleep events don't cause rotation failures or race conditions

**Plans**: TBD

---

### Phase 6: UI Polish & Integration
**Goal**: Menu bar interface, hotkeys, and display selection work seamlessly

**Depends on**: Phase 2, Phase 4, Phase 5

**Requirements**: REQ-UI-001, REQ-UI-002, REQ-UI-003

**Success Criteria** (what must be TRUE):
1. Menu bar icon is visible and clickable with rotation options
2. User can record and use custom global hotkeys for rotation actions
3. Hotkeys work system-wide even when app is in background
4. User can manually select target display from menu if auto-detection fails
5. Selected display persists across app restarts
6. All UI actions provide immediate feedback (notifications or visual updates)

**Plans**: TBD

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Technology Decision & Project Setup | 2/2 | ✅ Complete | 2026-03-01 |
| 2. Core Rotation Engine | 1/1 | ✅ Complete | 2026-03-08 |
| 3. Arrangement Preservation | 1/1 | ✅ Complete | 2026-03-08 |
| 4. Display Profiles | 1/1 | ✅ Complete | 2026-03-08 |
| 5. Error Handling & Reliability | 1/1 | ✅ Complete | 2026-03-08 |
| 6. UI Polish & Integration | 1/1 | ✅ Complete | 2026-03-08 |

---
*Last updated: 2026-03-01*
