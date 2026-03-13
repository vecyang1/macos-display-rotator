# Screen Rotator 🔄 [v2.2]

The ultimate macOS utility for **instant display orientation control**. Seamlessly switch your external monitors between landscape and portrait with a single click or a global hotkey.

Designed for developers, researchers, and content consumers who need to flip their perspective without diving into System Settings.

## ✨ What's New in v2.2

- 🖥️ **Native Settings Panel**: A professional Cocoa-based settings window for intuitive shortcut management. No more confusing menu-item recording!
- ⚡ **Zero-Latency State Sync**: Integrated with macOS system observers. The menu bar now stays perfectly in sync even if you rotate your screen via System Settings or hardware changes.
- 🧵 **Hardened Concurrency**: Full background threading for all rotation commands. Your UI stays buttery smooth and never "beachballs" during layout changes.
- 🛡️ **Production-Grade Stability**: Added thread-locks to prevent race conditions and 10s timeouts for external utility calls to prevent application hangs.

## 🚀 Key Features

- ✅ **One-Click Toggle**: Instantly flip between Standard (0°) and Vertical (90°/270°).
- ✅ **Global Hotkeys**: Custom keyboard shortcuts that work anywhere in macOS.
- ✅ **Smart Layout Memory**: Remembers your exact window arrangement and display origin for *every* orientation.
- ✅ **Automatic Sync**: Real-time monitoring of display parameters.
- ✅ **Launch at Login**: Ready to go the moment you start your Mac.
- ✅ **Privacy First**: Local execution with zero tracking or external API calls.

## 📦 Installation

### 1. Download Pre-built App
1. **[Download ScreenRotator v2.2](https://github.com/vecyang1/macos-display-rotator/releases/latest)**
2. Move **ScreenRotator.app** to your `/Applications` folder.

### 2. Install Dependency
The app uses the highly reliable `displayplacer` engine:
```bash
brew install jakehilborn/jakehilborn/displayplacer
```

### 3. Grant Permissions
Because the app listens for hotkeys, you must grant **Accessibility permissions**:
- **System Settings** → **Privacy & Security** → **Accessibility** → Enable **ScreenRotator**.

## 🛠️ Usage

1. Find the **SR** icon in your menu bar.
2. **Left-click** to access rotation presets or refresh your display list.
3. Select **"Settings..."** to open the new Shortcut Panel.

### Setting Up Hotkeys (The Easy Way)
1. Open **Settings...** from the menu bar.
2. Click **"Set"** next to an action (e.g., Toggle).
3. The status will change to **"Recording..."**—simply press your keys (e.g., `Cmd+Option+R`).
4. Shortcuts are saved instantly!

## 🔧 Troubleshooting

- **"SR" icon shows [?]**: Click **Refresh Displays** to re-scan your connected hardware.
- **Shortcuts not triggering?**: Ensure ScreenRotator is enabled in Accessibility settings and that another app isn't hogging the same key combination.
- **Need Logs?**: Check `~/screen_rotator_debug.log` for a detailed trace of application activity.

## 📜 License
MIT License - Open, free, and lightweight.

---
Built with ❤️ for the macOS community.
Powered by [rumps](https://github.com/jaredks/rumps), [pynput](https://github.com/moses-palmer/pynput), and [displayplacer](https://github.com/jakehilborn/displayplacer).
