import rumps
import subprocess
import re
import shutil
import json
import os
import sys
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import threading
import time

class ScreenRotatorApp(rumps.App):
    CONFIG_FILE = os.path.expanduser("~/.screen_rotator_config.json")
    
    def __init__(self):
        super(ScreenRotatorApp, self).__init__("🔄", icon=None)
        self.target_display_persistent_id = None
        self.displayplacer_path = shutil.which("displayplacer")
        
        if not self.displayplacer_path:
            possible_paths = ["/opt/homebrew/bin/displayplacer", "/usr/local/bin/displayplacer"]
            for path in possible_paths:
                if os.path.exists(path):
                    self.displayplacer_path = path
                    break
        
        if not self.displayplacer_path:
            rumps.alert("Error", "displayplacer not found. Please install via: brew install jakehilborn/jakehilborn/displayplacer")
            rumps.quit_application()

        # Shortcuts: action_name -> {"keys": [...], "display": "⌃⇧R"}
        self.shortcuts = {
            "toggle": None,
            "rotate_90": None,
            "rotate_0": None,
            "rotate_270": None
        }
        
        self.load_config()
        
        # Recording state
        self.recording_action = None
        self.recorded_keys = set()
        self.hotkey_listener = None
        
        # Initial target selection if none saved
        if not self.target_display_persistent_id:
            self.auto_select_target()
        
        self.update_menu()
        self.start_hotkey_listener()

    def load_config(self):
        """Load shortcuts and target display from config"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    
                    # Target display
                    self.target_display_persistent_id = config.get('target_display_id')
                    
                    # Shortcuts
                    saved_shortcuts = config.get('shortcuts', {})
                    for action in self.shortcuts:
                        if action in saved_shortcuts and saved_shortcuts[action]:
                            self.shortcuts[action] = saved_shortcuts[action]
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self):
        """Save config to file"""
        try:
            config = {}
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            
            config['shortcuts'] = self.shortcuts
            config['target_display_id'] = self.target_display_persistent_id
            
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def auto_select_target(self):
        """Automatically select the first external display as target"""
        displays = self.list_displays()
        # Prefer external
        for d in displays:
            if d['is_external']:
                self.target_display_persistent_id = d['persistent_id']
                return
        # Fallback to any if only one
        if displays:
            self.target_display_persistent_id = displays[0]['persistent_id']

    def update_menu(self):
        """Update menu structure"""
        self.menu.clear()
        
        # Action Items
        toggle_display = self.get_shortcut_display('toggle')
        self.menu.add(rumps.MenuItem(f"Toggle Screen  [{toggle_display}]", callback=self.toggle))
        
        self.menu.add(rumps.separator)
        
        self.menu.add(rumps.MenuItem("Rotate Standard (0°)", callback=lambda _: self.set_rotation(0)))
        self.menu.add(rumps.MenuItem("Rotate Vertical (90°)", callback=lambda _: self.set_rotation(90)))
        self.menu.add(rumps.MenuItem("Rotate Vertical (270°)", callback=lambda _: self.set_rotation(270)))
        
        self.menu.add(rumps.separator)

        # Target Display Selection Submenu
        displays_menu = rumps.MenuItem("Target Display")
        available_displays = self.list_displays()
        
        for d in available_displays:
            display_name = f"{d['name']} ({'External' if d['is_external'] else 'Built-in'})"
            item = rumps.MenuItem(display_name, callback=lambda x, pid=d['persistent_id']: self.select_target(x, pid))
            item.state = (d['persistent_id'] == self.target_display_persistent_id)
            displays_menu.add(item)
        
        self.menu.add(displays_menu)
        
        # Shortcuts Submenu (Same logic as before)
        shortcuts_menu = rumps.MenuItem("Set Shortcuts")
        shortcuts_menu.add(rumps.MenuItem("Record Toggle...", callback=lambda _: self.start_recording('toggle')))
        shortcuts_menu.add(rumps.MenuItem("Record 90°...", callback=lambda _: self.start_recording('rotate_90')))
        shortcuts_menu.add(rumps.MenuItem("Record Standard...", callback=lambda _: self.start_recording('rotate_0')))
        shortcuts_menu.add(rumps.separator)
        shortcuts_menu.add(rumps.MenuItem("Clear All", callback=self.clear_all_shortcuts))
        self.menu.add(shortcuts_menu)
        
        self.menu.add(rumps.separator)
        
        # System items
        launch_item = rumps.MenuItem("Launch at Login", callback=self.toggle_launch_at_login)
        launch_item.state = self.is_launch_at_login_enabled()
        self.menu.add(launch_item)


    def select_target(self, sender, persistent_id):
        """Handle target display selection from menu"""
        self.target_display_persistent_id = persistent_id
        self.save_config()
        self.update_menu()
        rumps.notification("Display Selected", "Selection saved", f"Target ID: {persistent_id[:8]}...")

    # --- Display Logic Utilities ---

    def list_displays(self):
        """Get list of all displays using displayplacer"""
        output, _ = self.run_command(f'"{self.displayplacer_path}" list')
        screens = output.split("Persistent screen id:")
        results = []
        
        for idx, screen in enumerate(screens):
            if not screen.strip(): continue
            
            # Persistent ID
            id_match = re.match(r"^\s*([A-F0-9-]+)", screen)
            if not id_match: continue
            pid = id_match.group(1)
            
            # Name/Type
            is_built_in = ("built in" in screen.lower() or "built-in" in screen.lower())
            is_external = "external" in screen.lower()
            name = f"Display {idx}"
            
            # Better name if available
            type_match = re.search(r"Type:\s*(.+)", screen)
            if type_match:
                name = type_match.group(1).split('\n')[0].strip()

            results.append({
                'persistent_id': pid,
                'name': name,
                'is_external': is_external,
                'is_built_in': is_built_in
            })
        return results

    def get_display_info(self, pid):
        output, _ = self.run_command(f'"{self.displayplacer_path}" list')
        screens = output.split("Persistent screen id:")
        for screen in screens:
            if pid in screen:
                info = {}
                res_match = re.search(r"Resolution:\s*(\d+x\d+)", screen)
                if res_match: info['res'] = res_match.group(1)
                rot_match = re.search(r"Rotation:\s*(\d+)", screen)
                if rot_match: info['degree'] = int(rot_match.group(1))
                # Add hz, color, scaling as before...
                for key in ['Hertz', 'Color Depth', 'Scaling']:
                    match = re.search(fr"{key}:\s*(\w+)", screen)
                    if match: info[key.lower().replace(' ', '_')] = match.group(1)
                return info
        return None

    def save_current_layout(self, mode_key):
        """Save the FULL current displayplacer command for a given mode (landscape/portrait)"""
        output, _ = self.run_command(f'"{self.displayplacer_path}" list')
        lines = output.strip().splitlines()
        
        # Find the restore command at the end
        restore_cmd = None
        for line in reversed(lines):
            if line.strip().startswith("displayplacer"):
                restore_cmd = line.strip()
                break
        
        if not restore_cmd:
            return
        
        try:
            config = {}
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            
            if 'layouts' not in config:
                config['layouts'] = {}
            
            config['layouts'][mode_key] = restore_cmd
            
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving layout: {e}")

    def load_saved_layout(self, mode_key):
        """Load a previously saved layout command"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                layouts = config.get('layouts', {})
                cmd = layouts.get(mode_key)
                if cmd:
                    # Replace displayplacer with full path
                    if cmd.startswith("displayplacer"):
                        cmd = cmd.replace("displayplacer", f'"{self.displayplacer_path}"', 1)
                    return cmd
        except Exception as e:
            print(f"Error loading layout: {e}")
        return None

    def set_rotation(self, target_degree):
        if not self.target_display_persistent_id:
            rumps.alert("Wait", "Please select a target display in the menu first!")
            return

        info = self.get_display_info(self.target_display_persistent_id)
        if not info:
            rumps.notification("Error", "Selected display not found", "")
            return

        current_rot = info.get('degree', 0)
        
        # Determine mode keys
        current_mode = "portrait" if current_rot in [90, 270] else "landscape"
        target_mode = "portrait" if target_degree in [90, 270] else "landscape"
        
        # Save current layout BEFORE rotating
        self.save_current_layout(current_mode)
        
        # Try to restore saved layout for target mode
        saved_cmd = self.load_saved_layout(target_mode)
        if saved_cmd:
            stdout, stderr = self.run_command(saved_cmd)
            if not (stderr and "Error" in stderr):
                rumps.notification("Success", f"Restored {target_mode} layout", "")
                return
        
        # Fallback: simple rotation if no saved layout
        current_res = info.get('res', '1920x1080')
        is_p_now = current_rot in [90, 270]
        is_p_target = target_degree in [90, 270]
        
        target_res = current_res
        if is_p_now != is_p_target:
            w, h = current_res.split('x')
            target_res = f"{h}x{w}"

        cmd = (f'"{self.displayplacer_path}" "id:{self.target_display_persistent_id} '
               f'res:{target_res} degree:{target_degree}"')
        
        stdout, stderr = self.run_command(cmd)
        if stderr and "Error" in stderr:
            rumps.notification("Failed", "Rotation command failed", stderr)
        else:
            rumps.notification("Success", f"Target rotated to {target_degree}°", "")

    def toggle(self, _):
        if not self.target_display_persistent_id: return
        info = self.get_display_info(self.target_display_persistent_id)
        if info:
            target = 90 if info.get('degree', 0) == 0 else 0
            self.set_rotation(target)

    # --- Copy remaining methods (Shortcuts, LaunchAtLogin) from previous version ---
    # (Methods: get_shortcut_display, start_recording, save_recorded_shortcut, 
    # clear_all_shortcuts, start_hotkey_listener, run_command, 
    # get_launch_agent_path, get_app_path, is_launch_at_login_enabled, toggle_launch_at_login)
    
    def get_shortcut_display(self, action):
        shortcut = self.shortcuts.get(action)
        if shortcut and shortcut.get('display'):
            return shortcut['display']
        return "None"

    def start_recording(self, action):
        self.recording_action = action
        self.recorded_keys = set()
        rumps.notification("Record", f"Press hotkey for {action}", "ESC to cancel")
        def on_press(key):
            if self.recording_action is None: return False
            if key == Key.esc: 
                self.recording_action = None
                return False
            self.recorded_keys.add(key)
        def on_release(key):
            if self.recording_action: self.save_recorded_shortcut(); return False
        threading.Thread(target=lambda: keyboard.Listener(on_press=on_press, on_release=on_release).start()).start()

    def save_recorded_shortcut(self):
        if not self.recorded_keys or not self.recording_action: return
        keys, disp = [], []
        symbol_map = {Key.ctrl:'⌃', Key.ctrl_l:'⌃', Key.shift:'⇧', Key.cmd:'⌘', Key.alt:'⌥'}
        for k in self.recorded_keys:
            if k in symbol_map: keys.append(str(k).split('.')[-1].split('_')[0]); disp.append(symbol_map[k])
            elif hasattr(k, 'char') and k.char: keys.append(k.char.lower()); disp.append(k.char.upper())
        self.shortcuts[self.recording_action] = {'keys': keys, 'display': ''.join(disp)}
        self.save_config(); self.update_menu(); self.start_hotkey_listener()
        self.recording_action = None

    def start_hotkey_listener(self):
        if self.hotkey_listener: self.hotkey_listener.stop()
        hotkeys = []
        for action, s in self.shortcuts.items():
            if s and s.get('keys'):
                def h(a=action): 
                    if a=='toggle': self.toggle(None)
                    elif a=='rotate_90': self.set_rotation(90)
                def parse(kl):
                    r = set()
                    for k in kl:
                        if k=='ctrl': r.add(Key.ctrl)
                        elif k=='shift': r.add(Key.shift)
                        elif k=='cmd': r.add(Key.cmd)
                        elif k=='alt': r.add(Key.alt)
                        else: r.add(KeyCode.from_char(k))
                    return r
                try: hotkeys.append(keyboard.HotKey(parse(s['keys']), h))
                except: pass
        if not hotkeys: return
        self.hotkey_listener = keyboard.Listener(on_press=lambda k: [hk.press(self.hotkey_listener.canonical(k)) for hk in hotkeys],
                                               on_release=lambda k: [hk.release(self.hotkey_listener.canonical(k)) for hk in hotkeys])
        self.hotkey_listener.start()

    def clear_all_shortcuts(self, _):
        for k in self.shortcuts: self.shortcuts[k] = None
        self.save_config(); self.update_menu(); self.start_hotkey_listener()

    def run_command(self, cmd):
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout, result.stderr

    def get_launch_agent_path(self): return os.path.expanduser("~/Library/LaunchAgents/com.screenrotator.app.plist")
    def is_launch_at_login_enabled(self): return os.path.exists(self.get_launch_agent_path())
    def toggle_launch_at_login(self, sender):
        p = self.get_launch_agent_path()
        if self.is_launch_at_login_enabled(): os.remove(p); sender.state=0
        else:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            prog = ["/usr/bin/open", "-a", "/Applications/ScreenRotator.app"] if getattr(sys,'frozen',False) else ["/usr/bin/python3", os.path.abspath(__file__)]
            with open(p, 'w') as f: f.write(f'<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><dict><key>Label</key><string>com.screenrotator.app</string><key>ProgramArguments</key><array>{"".join(f"<string>{a}</string>" for a in prog)}</array><key>RunAtLoad</key><true/></dict></plist>')
            sender.state=1

if __name__ == "__main__":
    ScreenRotatorApp().run()
