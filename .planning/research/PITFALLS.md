# Pitfalls: macOS Display Rotation Utilities

## Critical Mistakes

### 1. Display Rotation Crashes System Preferences
**Severity:** HIGH
**Warning Signs:** System Preferences pane freezes after rotation attempt
**Prevention:** Use CGDisplayConfigRef transaction pattern properly, always call CGCompleteDisplayConfiguration
**Phase:** Phase 1 (Core Rotation)

### 2. Display Arrangement Lost After Rotation
**Severity:** HIGH  
**Warning Signs:** Screens jump to different positions after rotation
**Prevention:** Capture CGDisplayBounds before rotation, restore with CGConfigureDisplayOrigin
**Phase:** Phase 2 (Arrangement Preservation)

### 3. Race Conditions on Display Wake/Sleep
**Severity:** MEDIUM
**Warning Signs:** Rotation fails intermittently after display wake
**Prevention:** Listen for display reconfiguration notifications, defer rotation until stable
**Phase:** Phase 3 (Error Handling)

### 4. Missing Rotation Support Detection
**Severity:** MEDIUM
**Warning Signs:** App crashes when display doesn't support requested rotation
**Prevention:** Query available display modes before attempting rotation
**Phase:** Phase 1 (Core Rotation)

### 5. Global Hotkey Conflicts
**Severity:** LOW
**Warning Signs:** Hotkey doesn't work or triggers other apps
**Prevention:** Use KeyboardShortcuts library with conflict detection
**Phase:** Phase 4 (Hotkey Integration)

---
*Research completed with partial data due to context limits*
