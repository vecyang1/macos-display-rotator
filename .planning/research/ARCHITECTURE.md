# Architecture Research

**Domain:** macOS Display Rotation Utility
**Researched:** 2026-03-01
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Layer (Menu Bar)                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Status  │  │ Popover │  │ Hotkey  │  │ Settings│        │
│  │  Item   │  │  View   │  │ Handler │  │  View   │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │              │
├───────┴────────────┴────────────┴────────────┴──────────────┤
│                   Business Logic Layer                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Display Manager (Core Logic)              │    │
│  │  • Display Detection                                │    │
│  │  • Rotation Control                                 │    │
│  │  • Arrangement Preservation                         │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                   System API Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │CoreGraphics│ │  Carbon  │  │ IOKit    │                   │
│  │  (Quartz)  │ │ EventHotKey│ │(Optional)│                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **NSStatusItem** | Menu bar icon presence and click handling | AppKit NSStatusBar API, manages icon and menu |
| **MenuBarExtra/Popover** | UI for manual rotation trigger | SwiftUI MenuBarExtra or NSPopover with SwiftUI content |
| **Hotkey Manager** | Global keyboard shortcut registration | Carbon EventHotKey API or wrapper library (HotKey, KeyboardShortcuts) |
| **Display Manager** | Core rotation logic and display detection | CoreGraphics CGDisplay* APIs, manages display state |
| **Display Detector** | Identify second screen automatically | CGGetActiveDisplayList, CGMainDisplayID |
| **Rotation Controller** | Execute rotation and preserve arrangement | CGDisplayConfigRef, CGSConfigureDisplayMode (private) |
| **Settings Manager** | Store user preferences (hotkey, behavior) | UserDefaults or property list |

## Recommended Project Structure

```
ScreenRotate/
├── App/
│   ├── ScreenRotateApp.swift      # App entry point, MenuBarExtra setup
│   └── AppDelegate.swift          # Lifecycle management, force activation
├── UI/
│   ├── MenuBarView.swift          # Menu bar popover content
│   ├── SettingsView.swift         # Hotkey configuration UI
│   └── StatusItemManager.swift    # NSStatusItem wrapper (if not using MenuBarExtra)
├── Core/
│   ├── DisplayManager.swift       # Main business logic coordinator
│   ├── DisplayDetector.swift      # Display enumeration and identification
│   ├── RotationController.swift   # Rotation execution and arrangement preservation
│   └── HotkeyManager.swift        # Global hotkey registration
├── Models/
│   ├── DisplayInfo.swift          # Display metadata (ID, bounds, rotation)
│   └── RotationState.swift        # Current rotation state tracking
├── Utilities/
│   ├── CGDisplayExtensions.swift  # CoreGraphics helper extensions
│   └── PrivateAPIs.swift          # Private API declarations (if needed)
└── Resources/
    ├── Info.plist                 # LSUIElement = YES for menu bar only
    └── Assets.xcassets            # Menu bar icon
```

### Structure Rationale

- **App/**: Entry point and lifecycle management. AppDelegate handles force activation workaround for `.accessory` apps.
- **UI/**: SwiftUI views for menu bar interface. Separated from business logic for testability.
- **Core/**: Business logic layer. DisplayManager coordinates between detection, rotation, and hotkey components.
- **Models/**: Data structures representing display state. Keeps CoreGraphics types isolated from UI.
- **Utilities/**: Extensions and helpers for CoreGraphics APIs. Private API declarations isolated for maintainability.

## Architectural Patterns

### Pattern 1: Menu Bar Agent App

**What:** Application runs as background agent with menu bar presence only (no Dock icon, no main window).

**When to use:** Utility apps that should be always available but non-intrusive.

**Trade-offs:**
- **Pros:** Clean UX, doesn't clutter Dock, always accessible
- **Cons:** Requires `LSUIElement = YES` in Info.plist, needs force activation workaround for text input

**Example:**
```swift
@main
struct ScreenRotateApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        MenuBarExtra("Screen Rotate", systemImage: "rotate.right") {
            MenuBarView()
        }
        .menuBarExtraStyle(.window)
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Force activation for keyboard input in popover
        NSApp.activate(ignoringOtherApps: true)
    }
}
```

### Pattern 2: Display Configuration Transaction

**What:** CoreGraphics requires configuration changes to be wrapped in begin/apply transaction pattern.

**When to use:** Any display mode or arrangement changes (rotation, resolution, origin).

**Trade-offs:**
- **Pros:** Atomic changes, can batch multiple display updates, rollback on failure
- **Cons:** Verbose API, requires careful error handling

**Example:**
```swift
func rotateDisplay(_ displayID: CGDirectDisplayID, to rotation: Int) -> Bool {
    var config: CGDisplayConfigRef?

    guard CGBeginDisplayConfiguration(&config) == .success else {
        return false
    }

    // Get current mode and create rotated version
    guard let currentMode = CGDisplayCopyDisplayMode(displayID),
          let modes = CGDisplayCopyAllDisplayModes(displayID, nil) as? [CGDisplayMode] else {
        CGCancelDisplayConfiguration(config)
        return false
    }

    // Find matching mode with desired rotation
    let targetMode = modes.first { mode in
        mode.width == currentMode.width &&
        mode.height == currentMode.height &&
        mode.ioDisplayModeID == rotation // Simplified - actual rotation logic more complex
    }

    guard let targetMode = targetMode else {
        CGCancelDisplayConfiguration(config)
        return false
    }

    // Apply rotation
    CGConfigureDisplayWithDisplayMode(config, displayID, targetMode, nil)

    // Commit changes
    let result = CGCompleteDisplayConfiguration(config, .permanently)
    return result == .success
}
```

### Pattern 3: Global Hotkey Registration

**What:** Register system-wide keyboard shortcuts using Carbon EventHotKey API or modern wrapper.

**When to use:** Background apps that need to respond to keyboard shortcuts regardless of focus.

**Trade-offs:**
- **Pros:** Works globally, doesn't require app to be frontmost
- **Cons:** Carbon API is legacy (but still functional), requires accessibility permissions on modern macOS

**Example (using HotKey library):**
```swift
import HotKey

class HotkeyManager {
    private var hotKey: HotKey?

    func registerHotkey(key: Key, modifiers: NSEvent.ModifierFlags, handler: @escaping () -> Void) {
        hotKey = HotKey(key: key, modifiers: modifiers)
        hotKey?.keyDownHandler = handler
    }

    func unregister() {
        hotKey = nil
    }
}

// Usage
let hotkeyManager = HotkeyManager()
hotkeyManager.registerHotkey(key: .r, modifiers: [.command, .option]) {
    // Trigger rotation
}
```

## Data Flow

### Request Flow

```
[User Action: Click Menu Bar Icon / Press Hotkey]
    ↓
[UI Layer: MenuBarView / HotkeyManager]
    ↓
[DisplayManager.rotateSecondDisplay()]
    ↓
[DisplayDetector.getSecondDisplay()] → [Returns CGDirectDisplayID]
    ↓
[RotationController.getCurrentState()] → [Get current rotation & bounds]
    ↓
[RotationController.rotateDisplay()] → [Apply rotation via CGDisplayConfig]
    ↓
[RotationController.preserveArrangement()] → [Restore origin via CGConfigureDisplayOrigin]
    ↓
[Response: Success/Failure] → [Update UI state]
```

### State Management

```
[DisplayManager State]
    ↓ (subscribe)
[UI Components] ←→ [Actions] → [State Updates] → [DisplayManager State]
                      ↓
                [CoreGraphics APIs]
```

### Key Data Flows

1. **Display Detection Flow:** App launch → enumerate displays via `CGGetActiveDisplayList` → identify main display via `CGMainDisplayID` → second display is first non-main display → cache display ID
2. **Rotation Flow:** User trigger → get current display bounds/origin → apply rotation via display config transaction → restore origin to preserve arrangement → verify success
3. **Hotkey Flow:** App launch → register global hotkey via Carbon/HotKey → hotkey pressed → trigger rotation flow → return focus to previous app

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Single user, 2 displays | Current architecture sufficient - simple state management, no persistence needed |
| Multiple display profiles | Add profile storage (UserDefaults), profile switcher UI, display configuration presets |
| Advanced features (per-app rotation, scheduled rotation) | Add display event monitoring, app focus detection, scheduler component |

### Scaling Priorities

1. **First bottleneck:** Display arrangement preservation reliability - macOS sometimes resets arrangements after rotation. **Fix:** Store original bounds, implement retry logic, add verification step.
2. **Second bottleneck:** Hotkey conflicts with other apps. **Fix:** Make hotkey customizable, detect conflicts, provide alternative trigger methods.

## Anti-Patterns

### Anti-Pattern 1: Using Private APIs Without Fallback

**What people do:** Rely solely on private CoreGraphics APIs (CGSConfigureDisplayMode) for rotation without public API fallback.

**Why it's wrong:** Private APIs can break between macOS versions, causing app to fail completely.

**Do this instead:** Use public APIs where possible (CGDisplayConfigRef transaction pattern), only use private APIs for features not available publicly, and implement graceful degradation.

### Anti-Pattern 2: Not Preserving Display Arrangement

**What people do:** Rotate display without capturing and restoring the origin (position in display arrangement).

**Why it's wrong:** macOS resets display positions after rotation, breaking multi-monitor workflows.

**Do this instead:** Before rotation, capture `CGDisplayBounds` origin. After rotation, use `CGConfigureDisplayOrigin` within the same transaction to restore position.

### Anti-Pattern 3: Blocking Main Thread During Display Configuration

**What people do:** Execute display configuration synchronously on main thread, freezing UI during rotation.

**Why it's wrong:** Display configuration can take 1-3 seconds, causing UI to hang and poor user experience.

**Do this instead:** Dispatch display configuration to background queue, show progress indicator, update UI on completion.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| CoreGraphics (Quartz Display Services) | Direct C API calls | Primary API for display management, well-documented |
| Carbon Event Manager | Direct C API or wrapper library | For global hotkeys, legacy but stable |
| IOKit (optional) | Direct C API | For advanced display info (EDID, vendor), adds complexity |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| UI ↔ DisplayManager | Direct method calls, @Published state | SwiftUI observes DisplayManager state changes |
| DisplayManager ↔ RotationController | Direct method calls, Result<> return | Synchronous for simplicity, async possible for large configs |
| HotkeyManager ↔ DisplayManager | Closure callbacks | Hotkey triggers call DisplayManager methods |
| RotationController ↔ CoreGraphics | C API calls | Thin wrapper around CoreGraphics, minimal abstraction |

## Sources

- [Building a MacOS Menu Bar App with Swift](https://bytegoblin.io/blog/building-a-macos-menu-bar-app-with-swift) - Menu bar app architecture patterns
- [SwiftUI Popovers and WindowManagement APIs](https://coldfusion-example.blogspot.com/2026/01/macos-menu-bar-apps-swiftui-popovers.html) - Agent app activation workarounds
- [Build a macOS menu bar utility in SwiftUI](https://nilcoalescing.com/blog/BuildAMacOSMenuBarUtilityInSwiftUI) - MenuBarExtra implementation
- [Display reconfigurations on macOS](https://nonstrict.eu/blog/2023/display-reconfigurations-on-macos) - CoreGraphics display APIs and change detection
- [jakehilborn/displayplacer](https://github.com/jakehilborn/displayplacer) - Reference implementation for display configuration
- [CdLbB/fb-rotate](https://github.com/CdLbB/fb-rotate) - Display rotation utility reference
- [Swift4 Display Mode Switch Menu Bar App](https://gist.github.com/bellbind/0cbd295130e4e1dc4459925e81048cf1) - Private API usage examples
- [HotKey Swift Package](https://swiftpackageregistry.com/soffes/HotKey) - Global hotkey wrapper library
- [sindresorhus/KeyboardShortcuts](https://github.com/sindresorhus/KeyboardShortcuts) - User-customizable hotkeys library

---
*Architecture research for: macOS Display Rotation Utility*
*Researched: 2026-03-01*
