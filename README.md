# Screen Rotator 🔄

A simple macOS menu bar app to **one-click rotate** your external display between horizontal and vertical. Perfect for viewing short videos or reading documents.

## Features

- ✅ **One-click rotation** - Toggle between Standard (0°) and Vertical (90°/270°)
- ✅ **Menu bar app** - Lives in your menu bar, always accessible
- ✅ **Custom global hotkeys** - Record any keyboard shortcut you want
- ✅ **Remembers position** - Saves your display arrangement for each orientation
- ✅ **Launch at Login** - Start automatically when you log in
- ✅ **No default shortcuts** - You choose your own hotkeys

## Installation

### 📦 Download Pre-built App (Easiest)

1. **[Download ScreenRotator v1.1.1](https://github.com/vecyang1/macos-display-rotator/releases/latest)** (24MB)
2. Unzip and move **ScreenRotator.app** to your `/Applications` folder
3. Install `displayplacer`:
   ```bash
   brew install jakehilborn/jakehilborn/displayplacer
   ```
4. Open **ScreenRotator.app**
5. Grant **Accessibility permissions** when prompted:
   - System Settings → Privacy & Security → Accessibility → Enable for ScreenRotator

### 🛠️ Build from Source (Advanced)

1. Clone this repo:
   ```bash
   git clone https://github.com/vecyang1/macos-display-rotator.git
   cd macos-display-rotator
   ```

2. Install dependencies:
   ```bash
   brew install jakehilborn/jakehilborn/displayplacer
   pip3 install rumps pynput py2app
   ```

3. Build the app:
   ```bash
   python3 setup.py py2app
   ```

4. Find your app in `dist/ScreenRotator.app`


## Usage

1. Look for the **🔄** icon in your menu bar
2. Click to see options:
   - **Toggle** - Switch between horizontal/vertical
   - **Rotate 90°** - Make screen vertical
   - **Rotate Standard** - Make screen horizontal
   - **Rotate 270°** - Vertical (opposite direction)

### Setting Up Keyboard Shortcuts

1. Click 🔄 → **Set Shortcuts**
2. Click **"Record Toggle Shortcut..."** (or any action)
3. Press your desired key combination (e.g., Ctrl+Shift+R)
4. Done! The shortcut is now active globally

### Launch at Login

1. Click 🔄 → **Launch at Login**
2. A checkmark appears when enabled
3. The app will start automatically on login

## Requirements

- macOS 10.13 or later
- Python 3.8 or later
- An external display

## Troubleshooting

**App doesn't find my display?**
- Make sure your external display is connected
- The app auto-detects displays marked as "external" by macOS

**Shortcuts don't work?**
- Grant Accessibility permissions: System Settings → Privacy & Security → Accessibility → Enable for Terminal/Python

**displayplacer not found?**
- Run: `brew install jakehilborn/jakehilborn/displayplacer`

## License

MIT License - Free to use and modify.

## Credits

Built with:
- [rumps](https://github.com/jaredks/rumps) - Menu bar apps
- [pynput](https://github.com/moses-palmer/pynput) - Keyboard input
- [displayplacer](https://github.com/jakehilborn/displayplacer) - Display control
