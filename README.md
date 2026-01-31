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

### Quick Install (Recommended)

1. Download/clone this folder
2. Open Terminal and navigate to this folder
3. Run:
   ```bash
   ./run.sh
   ```

### Manual Install

1. Install Homebrew if you don't have it:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install displayplacer:
   ```bash
   brew tap jakehilborn/jakehilborn
   brew install displayplacer
   ```

3. Install Python dependencies:
   ```bash
   pip3 install rumps pynput
   ```

4. Run the app:
   ```bash
   python3 screen_rotator.py
   ```

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
