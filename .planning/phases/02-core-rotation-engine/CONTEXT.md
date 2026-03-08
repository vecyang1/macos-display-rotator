# Phase 2: Core Rotation Engine

## Overview
This phase focuses on ensuring robust rotation command execution and display arrangement preservation.

## Key Changes
- Fix missing origin parameter in `set_rotation()` logic to prevent display layout breaking when rotating.
- Extract `origin:(x,y)` dynamically from `displayplacer list` when rotating if a saved layout isn't present for that orientation.

## Test Plan
- Run the python app `python3 screen_rotator.py`.
- Select an external monitor.
- Rotate the monitor via the menu items.
- Verify the display arrangement is perfectly maintained.
