# Technology Decision Analysis

## Executive Summary

**Root Cause Identified**: Display arrangement preservation bug is caused by incomplete displayplacer command at line 467 of screen_rotator.py - the rotation command only includes `id`, `res`, and `degree` parameters but omits the critical `origin:(<x>,<y>)` parameter that displayplacer supports.

**Recommendation**: Enhance existing Python implementation. The fix is straightforward, low-risk, and preserves the working 750-line codebase.

**Effort Estimate**: 2-4 hours for Python fix vs 40-60 hours for Swift rebuild.

---

## Task 01: Root Cause Analysis

### Bug Location

**File**: `screen_rotator.py`
**Method**: `set_rotation()` (lines 416-474)
**Critical Line**: Line 467

```python
command_arg = (
    f"id:{self.target_display_persistent_id} "
    f"res:{target_resolution} degree:{target_degree}"
)
```

### The Problem

The rotation command is **incomplete**. It only specifies:
- `id:<screenId>` - which display to rotate
- `res:<width>x<height>` - target resolution
- `degree:<0/90/270>` - target rotation

But displayplacer **requires** the `origin:(<x>,<y>)` parameter to preserve display position in the arrangement.

### Why This Happens

1. **Lines 434-435**: The code correctly saves the current layout before rotation:
   ```python
   self.save_current_layout(current_mode)
   ```

2. **Lines 436-446**: The code attempts to restore a saved layout if one exists for the target mode (portrait/landscape), which would include origin coordinates.

3. **Lines 463-467**: However, when no saved layout exists or the saved layout is stale, the code falls back to a **minimal rotation command** that lacks origin coordinates.

4. **Result**: macOS resets the display to default position (0,0) or an arbitrary location because no origin was specified.

### Displayplacer Capabilities Confirmed

From `displayplacer --help`:
```
Apply screen config: displayplacer "id:<screenId> res:<width>x<height> ... origin:(<x>,<y>) degree:<0/90/180/270>"
```

The `origin:(<x>,<y>)` parameter is **fully supported** and is the standard way to preserve display arrangement.

---

## Task 02: Python Fix Effort Estimate

### Required Changes

**1. Capture current origin before rotation** (lines 425-428)
```python
display_info = self.get_display_info(self.target_display_persistent_id)
# Need to also capture origin coordinates from displayplacer list output
```

**2. Modify `get_display_info()` to extract origin** (lines 361-379)
- Add regex to parse `Origin: (x,y)` from displayplacer list output
- Return origin as part of display_info dict

**3. Update rotation command to include origin** (line 467)
```python
command_arg = (
    f"id:{self.target_display_persistent_id} "
    f"res:{target_resolution} origin:({origin_x},{origin_y}) degree:{target_degree}"
)
```

### Effort Breakdown

| Task | Estimated Time | Complexity |
|------|---------------|------------|
| Modify `get_display_info()` to extract origin | 30 min | Low - simple regex addition |
| Update `set_rotation()` to use origin | 15 min | Low - add parameter to command string |
| Test with single external display | 30 min | Low - verify origin preserved |
| Test with multiple displays | 45 min | Medium - verify no side effects |
| Handle edge cases (display unplugged, etc.) | 30 min | Low - existing error handling sufficient |
| **Total** | **2.5 hours** | **Low** |

### Risk Assessment

**Low Risk**:
- Change is localized to 2 methods
- displayplacer already supports origin parameter (confirmed in help output)
- Existing save/restore logic already captures full layout including origin
- No architectural changes required
- Backward compatible (origin parameter is optional in displayplacer)

**Potential Issues**:
- Coordinate transformation complexity when rotating (width/height swap affects relative positions)
  - **Mitigation**: Use absolute origin coordinates from current layout, no transformation needed
- displayplacer reliability with origin parameter
  - **Mitigation**: Already using displayplacer successfully for rotation, origin is just an additional parameter

---

## Task 03: Swift Rebuild Comparison

### Swift Approach Overview

**APIs Required**:
1. **CoreGraphics Display Services** - Display control
   - `CGGetActiveDisplayList()` - Enumerate displays
   - `CGDisplayCopyDisplayMode()` - Get current mode
   - `CGDisplaySetDisplayMode()` - Set rotation
   - `CGDisplayBounds()` - Get display position
   - `CGConfigureDisplayOrigin()` - Set display position
   - `CGBeginDisplayConfiguration()` / `CGCompleteDisplayConfiguration()` - Atomic transaction

2. **AppKit** - Menu bar and UI
   - `NSStatusBar` - Menu bar item
   - `NSMenu` - Menu structure
   - `NSMenuItem` - Menu items

3. **Carbon/Cocoa** - Global hotkeys
   - `RegisterEventHotKey()` (Carbon) or `NSEvent.addGlobalMonitorForEvents()` (Cocoa)

### Swift Rebuild Effort Estimate

| Component | Estimated Time | Complexity |
|-----------|---------------|------------|
| CoreGraphics display enumeration | 4 hours | Medium - C API bridging |
| Rotation with origin preservation | 6 hours | High - transaction management, coordinate math |
| Menu bar UI | 8 hours | Medium - AppKit learning curve |
| Global hotkey system | 6 hours | High - Carbon API or Cocoa event monitoring |
| Display selection logic | 3 hours | Low - similar to Python |
| Configuration persistence | 3 hours | Low - UserDefaults or JSON |
| Launch at login | 2 hours | Low - SMLoginItemSetEnabled |
| Testing and debugging | 8 hours | Medium - native API edge cases |
| **Total** | **40 hours** | **High** |

### Swift Advantages

1. **Native API Access**: Direct CoreGraphics calls, no CLI dependency
2. **Atomic Transactions**: `CGBeginDisplayConfiguration()` ensures rotation + origin in single operation
3. **Better Error Handling**: Direct API return codes vs parsing CLI output
4. **Performance**: No subprocess overhead
5. **Long-term Maintainability**: Native macOS development, no third-party CLI tool dependency

### Swift Disadvantages

1. **High Initial Effort**: 40 hours vs 2.5 hours for Python fix
2. **Learning Curve**: CoreGraphics C API, AppKit, Carbon hotkeys
3. **Throws Away Working Code**: 750 lines of functional Python code
4. **No Immediate Benefit**: Python fix solves the primary bug just as effectively
5. **Risk**: Native API has same macOS quirks (race conditions, display ID changes)

---

## Comparison Table

| Factor | Python Enhancement | Swift Rebuild |
|--------|-------------------|---------------|
| **Effort** | 2.5 hours | 40 hours |
| **Risk** | Low | Medium-High |
| **Fixes Primary Bug** | Yes | Yes |
| **Code Reuse** | 100% | 0% |
| **Native Integration** | No (CLI dependency) | Yes |
| **Maintenance Burden** | Medium (displayplacer dependency) | Low (native APIs) |
| **Time to Working Solution** | Same day | 1-2 weeks |
| **User Disruption** | None | Complete rewrite |

---

## Recommendation

**Enhance the existing Python implementation.**

### Rationale

1. **Proportional Response**: The bug is a simple missing parameter, not an architectural flaw. A 2.5-hour fix is appropriate; a 40-hour rebuild is not.

2. **Risk vs Reward**: Python fix is low-risk with immediate payoff. Swift rebuild is high-risk with no additional benefit for the primary use case.

3. **Proven Foundation**: The existing Python code works well for all other features (menu bar, hotkeys, display selection, auto-detect). Throwing away 750 lines of working code is wasteful.

4. **displayplacer is Reliable**: The tool is actively maintained (Homebrew formula, GitHub repo), widely used, and the origin parameter is documented and supported.

5. **Future Optionality**: If displayplacer becomes problematic later (unlikely), we can still rebuild in Swift. But there's no evidence of issues now.

### When to Reconsider Swift

Consider Swift rebuild if:
- displayplacer development stops or becomes unmaintained
- macOS API changes break displayplacer compatibility
- Need features displayplacer cannot support (e.g., display color calibration, HDR control)
- User explicitly prefers native solution for philosophical reasons

None of these conditions currently apply.

---

## Next Steps (Plan 02)

1. Set up Python development environment
2. Implement origin parameter fix
3. Test with single and multiple display configurations
4. Verify arrangement preservation works reliably
5. Document any edge cases discovered during testing

---

## Final Decision (Plan 02)

**Decision**: Enhance existing Python implementation by adding origin parameter to displayplacer command.

**Primary Rationale**: The arrangement preservation bug is caused by a missing parameter (origin coordinates) in the rotation command at line 467 of screen_rotator.py. This is a simple, localized fix requiring modification of 2 methods (get_display_info and set_rotation) with an estimated effort of 2.5 hours. A Swift rebuild would take 40 hours and discard 750 lines of working code without providing additional benefit for the core use case.

**Trade-offs Accepted**:
- **CLI Dependency**: Continues reliance on displayplacer (external tool). Mitigation: displayplacer is actively maintained, widely used, and has proven reliable.
- **Not Native**: Uses subprocess calls rather than direct CoreGraphics API. Mitigation: Performance overhead is negligible for user-initiated rotation actions.
- **Future Maintenance**: If displayplacer becomes unmaintained, will need to reconsider Swift rebuild. Mitigation: displayplacer has active community and Homebrew support.

**Risk Mitigation**:
1. **Coordinate transformation complexity**: Use absolute origin coordinates from current layout - no transformation needed when rotating
2. **displayplacer reliability**: Already using displayplacer successfully for rotation; origin is just an additional parameter
3. **Edge cases**: Existing error handling and retry logic sufficient; will test with display unplugging scenarios
4. **Backward compatibility**: origin parameter is optional in displayplacer, so change is non-breaking

**Decision Enables Phase 2+ Planning**: With Python enhancement confirmed, Phase 2 can proceed with core engine improvements (origin parameter fix, error handling, retry logic) without architectural changes.

---

*Analysis completed: 2026-03-01*
*Final decision documented: 2026-03-01*
