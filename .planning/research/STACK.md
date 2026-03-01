# Stack Research

**Domain:** macOS Display Rotation Utility
**Researched:** 2026-03-01
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Swift | 6.0+ | Primary language | Native macOS development language with modern concurrency, type safety, and direct AppKit/CoreGraphics access. Industry standard for macOS utilities in 2025. |
| Xcode | 16.4+ | IDE and build system | Official Apple IDE with integrated Swift Package Manager, Interface Builder, and debugging tools. Required for macOS Sequoia (15.x) development. |
| AppKit | macOS 15+ | UI framework | Native framework for menu bar apps (NSStatusBar), provides NSMenu for menu bar interactions. More appropriate than SwiftUI for system utilities. |
| CoreGraphics | macOS 15+ | Display management | Low-level API for display configuration via CGDisplay* functions. Only way to programmatically rotate displays and manage display arrangements. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| KeyboardShortcuts | 2.x | Global hotkey registration | User-customizable global keyboard shortcuts. Sandbox-compatible, Mac App Store approved. Wraps Carbon APIs cleanly. |
| LaunchAtLogin-Modern | 5.x | Launch at login | Optional feature for auto-starting utility. Uses modern SMAppService API (macOS 13+). Mac App Store compatible. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Swift Package Manager | Dependency management | Built into Xcode, no external tools needed. Industry standard replacing CocoaPods/Carthage. |
| Git | Version control | Standard version control for tracking changes |
| Instruments | Performance profiling | Built into Xcode for debugging display API calls and memory usage |

## Installation

```bash
# Core dependencies via Swift Package Manager (add in Xcode)
# File > Add Package Dependencies...

# KeyboardShortcuts
https://github.com/sindresorhus/KeyboardShortcuts

# LaunchAtLogin-Modern (optional)
https://github.com/sindresorhus/LaunchAtLogin-Modern
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Swift + AppKit | Objective-C + AppKit | Never for new projects. Swift is the modern standard with better safety and concurrency. |
| Swift + AppKit | SwiftUI | Only if targeting macOS 14+ exclusively and building complex UI. For menu bar utilities, AppKit's NSStatusBar is more direct. |
| KeyboardShortcuts | MASShortcut | Never. MASShortcut is Objective-C based and less maintained. KeyboardShortcuts is the modern Swift successor. |
| KeyboardShortcuts | Carbon HotKey API directly | Only if you need extremely custom behavior. KeyboardShortcuts wraps Carbon cleanly and handles edge cases. |
| LaunchAtLogin-Modern | LaunchAtLogin-Legacy | Only if supporting macOS 12 or earlier. Modern version uses SMAppService (macOS 13+). |
| displayplacer (C/Objective-C) | Pure Swift implementation | displayplacer is a proven CLI tool but written in C/Objective-C. For a native app, pure Swift is cleaner and more maintainable. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| SwiftUI for menu bar | MenuBarExtra API is limited, less control over NSStatusItem behavior | AppKit NSStatusBar + NSMenu |
| CocoaPods | Deprecated in 2025, being sunset. No longer maintained. | Swift Package Manager |
| Carthage | Less integrated than SPM, declining usage | Swift Package Manager |
| MASShortcut | Objective-C library, less maintained than KeyboardShortcuts | KeyboardShortcuts (Swift) |
| CGDisplayCapture | Deprecated, causes black screen, not needed for rotation | CGDisplaySetDisplayMode with rotation parameter |
| Electron/web wrapper | Massive overhead (100MB+) for simple utility, poor system integration | Native Swift + AppKit |

## Stack Patterns by Variant

**If targeting Mac App Store distribution:**
- Enable App Sandbox in entitlements
- Use KeyboardShortcuts (sandbox-compatible)
- Use LaunchAtLogin-Modern (uses SMAppService, sandbox-compatible)
- No special display entitlements needed (CoreGraphics display APIs work in sandbox)

**If distributing outside Mac App Store:**
- Can skip sandboxing for simpler development
- Still use KeyboardShortcuts and LaunchAtLogin-Modern (work both ways)
- Consider code signing with Developer ID for Gatekeeper compatibility

**If supporting older macOS versions:**
- macOS 13+: Use LaunchAtLogin-Modern
- macOS 12 and earlier: Use LaunchAtLogin-Legacy
- macOS 11 and earlier: Consider dropping support (Swift 6 requires macOS 12+)

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Swift 6.0+ | Xcode 16.4+ | Swift 6 requires Xcode 16+, ships with macOS Sequoia SDK |
| KeyboardShortcuts 2.x | Swift 5.9+ | Works with Swift 6, requires macOS 11+ |
| LaunchAtLogin-Modern 5.x | macOS 13+ | Uses SMAppService API introduced in macOS 13 |
| AppKit + CoreGraphics | All macOS versions | Core frameworks, always available |

## Core API Reference

### Display Rotation APIs (CoreGraphics)

```swift
// Key functions for display management
CGGetActiveDisplayList()           // Get all active displays
CGDisplayCopyAllDisplayModes()     // Get available display modes
CGDisplaySetDisplayMode()          // Set display mode (including rotation)
CGConfigureDisplayOrigin()         // Preserve display arrangement
CGDisplayRotation()                // Get current rotation angle
```

**Critical Implementation Notes:**
1. Display rotation is set via `CGDisplaySetDisplayMode()` with a mode that has the desired rotation
2. Must enumerate available modes with `CGDisplayCopyAllDisplayModes()` to find rotated variants
3. After rotation, use `CGConfigureDisplayOrigin()` to restore display position in arrangement
4. Rotation angles: 0°, 90°, 180°, 270° (not all displays support all angles)
5. Changes require display reconfiguration transaction (begin/commit pattern)

### Menu Bar App Pattern (AppKit)

```swift
// Standard menu bar app structure
NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
statusItem.button?.image = NSImage(systemSymbolName:...)
statusItem.menu = NSMenu()
```

## Architecture Pattern

```
┌─────────────────────────────────────┐
│         AppDelegate                 │
│  - Initialize NSStatusBar           │
│  - Register global hotkey           │
│  - Handle app lifecycle             │
└──────────────┬──────────────────────┘
               │
               ├──> DisplayManager
               │    - Enumerate displays
               │    - Rotate second display
               │    - Preserve arrangement
               │
               └──> HotkeyManager
                    - Register shortcuts
                    - Handle key events
```

## Sources

- [KeyboardShortcuts GitHub](https://github.com/sindresorhus/KeyboardShortcuts) — HIGH confidence, official docs
- [Context7: KeyboardShortcuts](/sindresorhus/keyboardshortcuts) — HIGH confidence, verified API usage
- [displayplacer GitHub](https://github.com/jakehilborn/displayplacer) — HIGH confidence, proven display management implementation
- [Apple Developer: CoreGraphics Display Services](https://developer.apple.com/documentation/coregraphics/quartz_display_services) — HIGH confidence, official API docs
- [Swift Package Manager best practices 2025](https://oneuptime.com/blog/post/2026-02-02-swift-package-manager/view) — MEDIUM confidence, web search
- [Xcode 16 macOS Sequoia development](https://osxhub.com/xcode-download-install-guide-macos-sequoia-2025/) — MEDIUM confidence, web search
- [LaunchAtLogin-Modern](https://swiftpackageregistry.com/sindresorhus/LaunchAtLogin-Modern) — HIGH confidence, official package registry

---
*Stack research for: macOS Display Rotation Utility*
*Researched: 2026-03-01*
