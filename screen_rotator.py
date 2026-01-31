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
        self.external_display_id = None
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

        self.external_display_id = self.get_external_display_id()
        
        # Shortcuts: action_name -> {"keys": [...], "display": "⌃⇧R"} or None
        self.shortcuts = {
            "toggle": None,
            "rotate_90": None,
            "rotate_0": None,
            "rotate_270": None
        }
        
        # Load saved shortcuts
        self.load_shortcuts()
        
        # Recording state
        self.recording_action = None
        self.recorded_keys = set()
        self.hotkey_listener = None
        
        # Build menu
        self.update_menu()
        
        # Start global hotkey listener
        self.start_hotkey_listener()

    def load_shortcuts(self):
        """Load shortcuts from config"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    saved = config.get('shortcuts', {})
                    for action in self.shortcuts:
                        if action in saved and saved[action]:
                            self.shortcuts[action] = saved[action]
        except Exception as e:
            print(f"Error loading shortcuts: {e}")

    def save_shortcuts(self):
        """Save shortcuts to config"""
        try:
            config = {}
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            
            config['shortcuts'] = self.shortcuts
            
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            rumps.notification("Error", "Could not save shortcuts", str(e))

    def get_shortcut_display(self, action):
        """Get display string for a shortcut"""
        shortcut = self.shortcuts.get(action)
        if shortcut and shortcut.get('display'):
            return shortcut['display']
        return "Not set"

    def update_menu(self):
        """Update menu with current shortcuts"""
        self.menu.clear()
        
        # Main actions
        toggle_display = self.get_shortcut_display('toggle')
        self.menu.add(rumps.MenuItem(f"Toggle  [{toggle_display}]", callback=self.toggle))
        
        self.menu.add(rumps.separator)
        
        rotate_90_display = self.get_shortcut_display('rotate_90')
        self.menu.add(rumps.MenuItem(f"Rotate 90°  [{rotate_90_display}]", callback=self.rotate_90))
        
        rotate_0_display = self.get_shortcut_display('rotate_0')
        self.menu.add(rumps.MenuItem(f"Rotate Standard  [{rotate_0_display}]", callback=self.rotate_0))
        
        rotate_270_display = self.get_shortcut_display('rotate_270')
        self.menu.add(rumps.MenuItem(f"Rotate 270°  [{rotate_270_display}]", callback=self.rotate_270))
        
        self.menu.add(rumps.separator)
        
        # Shortcut recording submenu
        shortcuts_menu = rumps.MenuItem("Set Shortcuts")
        shortcuts_menu.add(rumps.MenuItem("Record Toggle Shortcut...", callback=lambda _: self.start_recording('toggle')))
        shortcuts_menu.add(rumps.MenuItem("Record Rotate 90° Shortcut...", callback=lambda _: self.start_recording('rotate_90')))
        shortcuts_menu.add(rumps.MenuItem("Record Rotate Standard Shortcut...", callback=lambda _: self.start_recording('rotate_0')))
        shortcuts_menu.add(rumps.MenuItem("Record Rotate 270° Shortcut...", callback=lambda _: self.start_recording('rotate_270')))
        shortcuts_menu.add(rumps.separator)
        shortcuts_menu.add(rumps.MenuItem("Clear All Shortcuts", callback=self.clear_all_shortcuts))
        self.menu.add(shortcuts_menu)
        
        self.menu.add(rumps.separator)
        
        # Launch at Login toggle
        launch_item = rumps.MenuItem("Launch at Login", callback=self.toggle_launch_at_login)
        launch_item.state = self.is_launch_at_login_enabled()
        self.menu.add(launch_item)

    def start_recording(self, action):
        """Start recording a shortcut for an action"""
        self.recording_action = action
        self.recorded_keys = set()
        
        action_names = {
            'toggle': 'Toggle',
            'rotate_90': 'Rotate 90°',
            'rotate_0': 'Rotate Standard',
            'rotate_270': 'Rotate 270°'
        }
        
        rumps.notification(
            "Recording Shortcut",
            f"Press your desired hotkey for '{action_names[action]}'",
            "Press ESC to cancel"
        )
        
        # Start a recording listener
        def on_press(key):
            if self.recording_action is None:
                return False
            
            # Check for ESC to cancel
            if key == Key.esc:
                self.recording_action = None
                self.recorded_keys = set()
                rumps.notification("Cancelled", "Shortcut recording cancelled", "")
                return False
            
            # Add key to recorded set
            self.recorded_keys.add(key)

        def on_release(key):
            if self.recording_action is None:
                return False
            
            # When any key is released, save the combination
            if len(self.recorded_keys) > 0:
                self.save_recorded_shortcut()
                return False
        
        # Run listener in thread
        def start_listener():
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
        
        threading.Thread(target=start_listener, daemon=True).start()

    def save_recorded_shortcut(self):
        """Save the recorded keys as a shortcut"""
        if not self.recorded_keys or not self.recording_action:
            return
        
        keys = []
        display_parts = []
        
        symbol_map = {
            Key.ctrl: ('ctrl', '⌃'),
            Key.ctrl_l: ('ctrl', '⌃'),
            Key.ctrl_r: ('ctrl', '⌃'),
            Key.shift: ('shift', '⇧'),
            Key.shift_l: ('shift', '⇧'),
            Key.shift_r: ('shift', '⇧'),
            Key.cmd: ('cmd', '⌘'),
            Key.cmd_l: ('cmd', '⌘'),
            Key.cmd_r: ('cmd', '⌘'),
            Key.alt: ('alt', '⌥'),
            Key.alt_l: ('alt', '⌥'),
            Key.alt_r: ('alt', '⌥'),
        }
        
        # Sort: modifiers first, then regular keys
        modifiers = []
        regular = []
        
        for key in self.recorded_keys:
            if key in symbol_map:
                key_name, symbol = symbol_map[key]
                if key_name not in keys:  # Avoid duplicates (left/right)
                    modifiers.append((key_name, symbol))
                    keys.append(key_name)
            elif isinstance(key, KeyCode):
                char = key.char if key.char else str(key.vk)
                regular.append((char.lower(), char.upper()))
                keys.append(char.lower())
            else:
                # Handle other special keys
                key_name = str(key).replace('Key.', '')
                regular.append((key_name, key_name.upper()))
                keys.append(key_name)
        
        # Build display string (modifiers first)
        for _, symbol in modifiers:
            display_parts.append(symbol)
        for _, display in regular:
            display_parts.append(display)
        
        display = ''.join(display_parts)
        
        self.shortcuts[self.recording_action] = {
            'keys': keys,
            'display': display
        }
        
        action = self.recording_action
        self.recording_action = None
        self.recorded_keys = set()
        
        self.save_shortcuts()
        self.update_menu()
        
        # Restart hotkey listener with new shortcuts
        self.start_hotkey_listener()
        
        action_names = {
            'toggle': 'Toggle',
            'rotate_90': 'Rotate 90°',
            'rotate_0': 'Rotate Standard',
            'rotate_270': 'Rotate 270°'
        }
        
        rumps.notification(
            "Shortcut Saved",
            f"{action_names[action]}: {display}",
            "Shortcut is now active"
        )

    def clear_all_shortcuts(self, _):
        """Clear all shortcuts"""
        self.shortcuts = {
            "toggle": None,
            "rotate_90": None,
            "rotate_0": None,
            "rotate_270": None
        }
        self.save_shortcuts()
        self.update_menu()
        self.start_hotkey_listener()
        rumps.notification("Cleared", "All shortcuts have been cleared", "")

    def get_launch_agent_path(self):
        """Get the path to the LaunchAgent plist"""
        return os.path.expanduser("~/Library/LaunchAgents/com.screenrotator.app.plist")
    
    def get_app_path(self):
        """Get the path to run the app"""
        # Check if running as .app bundle
        if getattr(sys, 'frozen', False):
            # Running as .app
            return sys.executable
        else:
            # Running as script
            return os.path.abspath(__file__)

    def is_launch_at_login_enabled(self):
        """Check if launch at login is enabled"""
        return os.path.exists(self.get_launch_agent_path())

    def toggle_launch_at_login(self, sender):
        """Toggle launch at login"""
        plist_path = self.get_launch_agent_path()
        
        if self.is_launch_at_login_enabled():
            # Disable - remove LaunchAgent
            try:
                os.remove(plist_path)
                sender.state = False
                rumps.notification("Launch at Login", "Disabled", "App will not start automatically")
            except Exception as e:
                rumps.alert("Error", f"Could not disable: {e}")
        else:
            # Enable - create LaunchAgent
            try:
                # Ensure LaunchAgents directory exists
                launch_agents_dir = os.path.dirname(plist_path)
                os.makedirs(launch_agents_dir, exist_ok=True)
                
                # Determine program to run
                if getattr(sys, 'frozen', False):
                    # Running as .app bundle
                    program = ["/usr/bin/open", "-a", os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))]
                else:
                    # Running as script
                    script_path = os.path.abspath(__file__)
                    program = ["/usr/bin/python3", script_path]
                
                plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.screenrotator.app</string>
    <key>ProgramArguments</key>
    <array>
        {"".join(f"<string>{arg}</string>" for arg in program)}
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
'''
                with open(plist_path, 'w') as f:
                    f.write(plist_content)
                
                sender.state = True
                rumps.notification("Launch at Login", "Enabled", "App will start automatically on login")
            except Exception as e:
                rumps.alert("Error", f"Could not enable: {e}")

    def start_hotkey_listener(self):
        """Start listening for global hotkeys"""
        # Stop existing listener
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
        
        # Build hotkey handlers
        active_hotkeys = []
        
        for action, shortcut in self.shortcuts.items():
            if shortcut and shortcut.get('keys'):
                keys = shortcut['keys']
                
                def make_handler(act):
                    def handler():
                        if act == 'toggle':
                            self.toggle(None)
                        elif act == 'rotate_90':
                            self.rotate_90(None)
                        elif act == 'rotate_0':
                            self.rotate_0(None)
                        elif act == 'rotate_270':
                            self.rotate_270(None)
                    return handler
                
                def parse_keys(key_list):
                    result = set()
                    for k in key_list:
                        if k == 'ctrl':
                            result.add(Key.ctrl)
                        elif k == 'shift':
                            result.add(Key.shift)
                        elif k == 'cmd':
                            result.add(Key.cmd)
                        elif k == 'alt':
                            result.add(Key.alt)
                        else:
                            result.add(KeyCode.from_char(k))
                    return result
                
                try:
                    hotkey = keyboard.HotKey(parse_keys(keys), make_handler(action))
                    active_hotkeys.append(hotkey)
                except Exception as e:
                    print(f"Error creating hotkey for {action}: {e}")
        
        if not active_hotkeys:
            return
        
        def for_canonical(f):
            return lambda k: f(self.hotkey_listener.canonical(k))

        self.hotkey_listener = keyboard.Listener(
            on_press=for_canonical(lambda key: [h.press(key) for h in active_hotkeys]),
            on_release=for_canonical(lambda key: [h.release(key) for h in active_hotkeys])
        )
        self.hotkey_listener.start()

    # ===== Display Control Methods =====
    
    def run_command(self, cmd):
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout, result.stderr

    def get_external_display_id(self):
        output, _ = self.run_command(f'"{self.displayplacer_path}" list')
        screens = output.split("Persistent screen id:")
        
        for screen in screens:
            if not screen.strip(): continue
            
            screen_lower = screen.lower()
            is_external = "external" in screen_lower
            is_built_in = "built in" in screen_lower or "built-in" in screen_lower

            if is_external or (not is_built_in and "type:" in screen_lower):
                match = re.match(r"^\s*([A-F0-9-]+)", screen)
                if match:
                    return match.group(1)
        
        return None

    def get_display_info(self, display_id):
        if not display_id: return None
        output, _ = self.run_command(f'"{self.displayplacer_path}" list')
        screens = output.split("Persistent screen id:")
        for screen in screens:
            if display_id in screen:
                info = {}
                res_match = re.search(r"Resolution:\s*(\d+x\d+)", screen)
                if res_match: info['res'] = res_match.group(1)
                
                hz_match = re.search(r"Hertz:\s*(\d+)", screen)
                if hz_match: info['hz'] = hz_match.group(1)
                
                cd_match = re.search(r"Color Depth:\s*(\d+)", screen)
                if cd_match: info['color_depth'] = cd_match.group(1)
                
                sc_match = re.search(r"Scaling:\s*(on|off)", screen)
                if sc_match: info['scaling'] = sc_match.group(1)
                
                rot_match = re.search(r"Rotation:\s*(\d+)", screen)
                if rot_match: info['degree'] = int(rot_match.group(1))
                
                return info
        return None

    def get_current_rotation(self, display_id):
        info = self.get_display_info(display_id)
        if info:
            return info.get('degree', 0)
        return 0

    def rotate_90(self, _):
        self.set_rotation(90)

    def rotate_270(self, _):
        self.set_rotation(270)

    def rotate_0(self, _):
        self.set_rotation(0)

    def toggle(self, _):
        current_degree = self.get_current_rotation(self.external_display_id)
        if current_degree == 0:
            self.set_rotation(90)
        else:
            self.set_rotation(0)

    def save_layout(self, degree):
        output, _ = self.run_command(f'"{self.displayplacer_path}" list')
        lines = output.strip().splitlines()
        if not lines: return

        restore_cmd = None
        for line in reversed(lines):
            if line.strip().startswith("displayplacer"):
                restore_cmd = line.strip()
                break
        
        if not restore_cmd:
            return

        mode = "portrait" if degree in [90, 270] else "landscape"
        
        try:
            config = {}
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            
            config[mode] = restore_cmd
            
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving layout: {e}")

    def load_layout(self, degree):
        mode = "portrait" if degree in [90, 270] else "landscape"
        if not os.path.exists(self.CONFIG_FILE):
            return None
        
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            cmd = config.get(mode)
            if cmd:
                if cmd.startswith("displayplacer"):
                    cmd = cmd.replace("displayplacer", f'"{self.displayplacer_path}"', 1)
                return cmd
        except:
            return None
        return None

    def set_rotation(self, target_degree):
        if not self.external_display_id:
            self.external_display_id = self.get_external_display_id()
            if not self.external_display_id:
                rumps.notification("Error", "No external display found", "Please connect a second monitor.")
                return

        current_degree = self.get_current_rotation(self.external_display_id)
        self.save_layout(current_degree)

        saved_cmd = self.load_layout(target_degree)
        
        if saved_cmd:
            stdout, stderr = self.run_command(saved_cmd)
            if not (stderr and "Error" in stderr):
                rumps.notification("Success", f"Restored {target_degree}° Layout", "")
                return

        info = self.get_display_info(self.external_display_id)
        if not info:
            rumps.notification("Error", "Could not get display info", "")
            return

        current_res = info.get('res', '1920x1080')
        hz = info.get('hz', '60')
        color_depth = info.get('color_depth', '8')
        scaling = info.get('scaling', 'off')

        is_portrait_current = current_degree in [90, 270]
        is_portrait_target = target_degree in [90, 270]
        
        target_res = current_res
        if is_portrait_current != is_portrait_target:
            w, h = current_res.split('x')
            target_res = f"{h}x{w}"

        cmd = (f'"{self.displayplacer_path}" "id:{self.external_display_id} '
               f'res:{target_res} hz:{hz} color_depth:{color_depth} '
               f'enabled:true scaling:{scaling} degree:{target_degree}"')
        
        stdout, stderr = self.run_command(cmd)
        if stderr and "Error" in stderr:
            rumps.notification("Failed", f"Could not rotate to {target_degree}", stderr)
        else:
            rumps.notification("Success", f"Rotated to {target_degree}°", "")

if __name__ == "__main__":
    ScreenRotatorApp().run()
