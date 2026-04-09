# 🔄 ScreenRotator - Functional Specification

> Reverse-engineered from v2.2 baseline.

## 1. Purpose
The ultimate macOS utility for instant display orientation control. Allows users to seamlessly switch external monitors between landscape and portrait with a single click or a global hotkey, without opening System Settings.

## 2. Core Functional Requirements

### 2.1 One-Click Quick Toggle
- The App must reside in the macOS Menu Bar.
- Left-clicking the icon must present display options.
- The user must be able to click to toggle display sets between `Standard (0°)` and `Vertical (90°/270°)`.

### 2.2 Global Hotkeys
- Users must be able to bind global shortcuts (e.g., `Cmd+Option+R`).
- Triggering the hotkey anywhere in macOS must execute rotation on target displays.

### 2.3 Settings Panel (Native Cocoa UI)
- The app must include a built-in "Settings..." pane.
- The pane must allow intuitive assigning/recording of hotkeys without modifying code.
- Must provide clear instructions regarding Accessibility Permissions if hotkeys fail.

### 2.4 Smart Layout Memory
- Ensure window arrangement and specific display origins are preserved during orientation shifts.
- Rely on external utility output for parameter storage if needed.

### 2.5 Built-in Display Safety (15s Revert)
- The app must detect if the rotation target is the built-in MacBook display.
- To prevent permanent trackpad/mouse disorientation due to Apple's native hardware limitations, any rotation of the built-in screen MUST trigger an automatic 15-second revert countdown accompanied by a native macOS popup dialog.
- The user must explicitly click "Keep Rotation" to cancel the timer, otherwise the screen auto-reverts to its previous safe degree.

## 3. Out of Scope
- Windows/Linux compatibility.
- Cloud syncing of settings.
