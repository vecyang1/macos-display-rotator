# Development Environment Setup

## Overview

ScreenRotator is a Python-based macOS menu bar application that uses:
- **rumps** - Menu bar interface (Ridiculously Uncomplicated macOS Python Statusbar apps)
- **pynput** - Global hotkey monitoring
- **displayplacer** - CLI tool for display configuration (external dependency)
- **py2app** - Package Python app as standalone macOS .app bundle

## Prerequisites

### System Requirements

- **macOS**: 10.15 (Catalina) or later (tested on macOS 26.0.1)
- **Python**: 3.12+ (tested with Python 3.12.8)
- **Homebrew**: For installing displayplacer
- **Xcode Command Line Tools**: For building native extensions

### Install Xcode Command Line Tools

```bash
xcode-select --install
```

### Install displayplacer

```bash
brew install jakehilborn/jakehilborn/displayplacer
```

Verify installation:
```bash
displayplacer --version
# Should show: displayplacer v1.4.0 or later
```

## Python Environment Setup

### 1. Clone Repository

```bash
cd ~/Documents/A-coding
git clone <repository-url> "26.01.30 Screen Rotate"
cd "26.01.30 Screen Rotate"
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install rumps==0.4.0
pip install pynput==1.8.1
pip install py2app==0.28.9
```

Verify installation:
```bash
pip list | grep -E "(rumps|pynput|py2app)"
```

Expected output:
```
py2app                               0.28.9
pynput                               1.8.1
rumps                                0.4.0
```

## Running the Application

### Development Mode (from source)

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Run the application
python screen_rotator.py
```

You should see:
- Menu bar icon "SR" appears in the top-right menu bar
- Click icon to see menu with display selection and rotation options
- Hotkeys work (default: Cmd+Shift+R for toggle rotation)

### Stop the Application

Press `Ctrl+C` in the terminal, or click "Quit" from the menu bar icon.

## Building Standalone Application

### Build .app Bundle

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Clean previous builds
rm -rf build dist

# Build the app
python setup.py py2app
```

The built application will be at: `dist/ScreenRotator.app`

### Test Built Application

```bash
# Run the built app
open dist/ScreenRotator.app
```

Verify:
- Menu bar icon appears
- Menu items work
- Hotkeys work
- Rotation works (requires external display)

### Install Built Application

```bash
# Copy to Applications folder
cp -r dist/ScreenRotator.app /Applications/

# Launch from Applications
open /Applications/ScreenRotator.app
```

## Testing

### Manual Testing Checklist

**Basic Functionality:**
- [ ] Menu bar icon appears
- [ ] Menu shows current display list
- [ ] Can select target display
- [ ] Rotation commands work (0°, 90°, 270°, toggle)
- [ ] Hotkeys trigger rotation
- [ ] Preferences can be opened and saved

**Arrangement Preservation (Primary Bug):**
- [ ] Connect external display
- [ ] Note display position in System Settings > Displays
- [ ] Rotate display using ScreenRotator
- [ ] Verify display stays in same position (not reset to 0,0)
- [ ] Rotate back to original orientation
- [ ] Verify position still preserved

**Edge Cases:**
- [ ] Unplug display while app running (should handle gracefully)
- [ ] Replug display (should re-detect)
- [ ] Multiple external displays (should list all)
- [ ] Rotate with no external display (should show error or disable)

### Automated Testing

Currently no automated tests. Future work:
- Unit tests for display info parsing
- Integration tests for displayplacer command generation
- Mock displayplacer output for CI/CD

## Troubleshooting

### "displayplacer: command not found"

Install displayplacer via Homebrew:
```bash
brew install jakehilborn/jakehilborn/displayplacer
```

### "No module named 'rumps'"

Activate virtual environment and install dependencies:
```bash
source venv/bin/activate
pip install rumps pynput py2app
```

### Menu bar icon doesn't appear

Check if app is running:
```bash
ps aux | grep screen_rotator
```

Check for errors in terminal output. Common issues:
- Accessibility permissions not granted (pynput needs this for hotkeys)
- Python version incompatibility (need 3.12+)

### Rotation doesn't preserve arrangement

This is the primary bug being fixed in Phase 2. Current behavior:
- Display rotates successfully
- Display position resets to arbitrary location
- Saved layouts may restore position, but fallback rotation command doesn't

Fix: Add `origin:(<x>,<y>)` parameter to displayplacer command (Phase 2 implementation).

### py2app build fails

Common issues:
- Missing Xcode Command Line Tools: `xcode-select --install`
- Outdated py2app: `pip install --upgrade py2app`
- Conflicting system Python packages: Use virtual environment

## Development Workflow

### Typical Development Session

```bash
# 1. Activate environment
cd ~/Documents/A-coding/"26.01.30 Screen Rotate"
source venv/bin/activate

# 2. Make code changes
vim screen_rotator.py

# 3. Test changes
python screen_rotator.py
# (Test functionality, then Ctrl+C to stop)

# 4. Build and test standalone app
python setup.py py2app
open dist/ScreenRotator.app
# (Test built app, then quit from menu bar)

# 5. Commit changes
git add screen_rotator.py
git commit -m "fix: add origin parameter to preserve arrangement"
```

### Code Structure

**Main file**: `screen_rotator.py` (750 lines)

Key classes:
- `ScreenRotatorApp` - Main application class (rumps.App)
- Methods:
  - `get_display_info()` - Parse displayplacer list output (lines 361-379)
  - `set_rotation()` - Execute rotation command (lines 416-474)
  - `save_current_layout()` - Save display configuration
  - `restore_layout()` - Restore saved configuration

**Build configuration**: `setup.py`
- py2app options
- Bundle identifier: com.screenrotator.app
- Version: 1.1.0

## Next Steps

After environment setup is verified:
1. Implement origin parameter fix (Phase 2, Plan 01)
2. Add comprehensive error handling (Phase 2, Plan 02)
3. Improve retry logic (Phase 2, Plan 03)
4. Add profile system (Phase 3)

---

*Last updated: 2026-03-01*
