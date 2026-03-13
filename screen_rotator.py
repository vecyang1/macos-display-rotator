import json
import logging
import os
import plistlib
import re
import shlex
import shutil
import subprocess
import sys
import queue
import threading
from typing import Dict, List, Optional, Sequence, Union

import AppKit
import rumps
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

ACTION_ROTATIONS = {
    "toggle": None,
    "rotate_90": 90,
    "rotate_0": 0,
    "rotate_270": 270,
}

MODIFIER_ORDER = ("ctrl", "shift", "alt", "cmd")
MODIFIER_SYMBOLS = {
    "ctrl": "⌃",
    "shift": "⇧",
    "alt": "⌥",
    "cmd": "⌘",
}
SPECIAL_KEY_DISPLAY = {
    "space": "Space",
    "enter": "↩",
    "tab": "⇥",
    "esc": "⎋",
}
STATUS_ITEM_TITLE = "SR"


def action_to_rotation(action: str) -> Optional[int]:
    return ACTION_ROTATIONS.get(action)


def is_modifier_key_name(key_name: str) -> bool:
    return key_name in MODIFIER_ORDER


def order_shortcut_keys(keys: Sequence[str]) -> List[str]:
    normalized: List[str] = []
    seen = set()
    for key in keys:
        normalized_key = str(key).strip().lower()
        if not normalized_key or normalized_key in seen:
            continue
        seen.add(normalized_key)
        normalized.append(normalized_key)

    modifiers = [key for key in MODIFIER_ORDER if key in normalized]
    non_modifiers = [key for key in normalized if key not in MODIFIER_ORDER]
    return modifiers + non_modifiers


def format_shortcut_display(keys: Sequence[str]) -> str:
    ordered = order_shortcut_keys(keys)
    if not ordered:
        return "None"

    display_parts = []
    for key in ordered:
        if key in MODIFIER_SYMBOLS:
            display_parts.append(MODIFIER_SYMBOLS[key])
        elif key in SPECIAL_KEY_DISPLAY:
            display_parts.append(SPECIAL_KEY_DISPLAY[key])
        elif len(key) == 1:
            display_parts.append(key.upper())
        else:
            display_parts.append(key.upper())
    return "".join(display_parts)


def parse_saved_layout_command(command: Union[str, Sequence[str], None]) -> Optional[List[str]]:
    if command is None:
        return None

    if isinstance(command, (list, tuple)):
        parsed = [str(token).strip() for token in command if str(token).strip()]
        return parsed or None

    if not isinstance(command, str):
        return None

    tokens = shlex.split(command)
    if not tokens:
        return None

    if os.path.basename(tokens[0]) == "displayplacer":
        tokens = tokens[1:]

    parsed = [token.strip() for token in tokens if token.strip()]
    return parsed or None


def is_portrait_degree(degree: Optional[int]) -> bool:
    if degree is None:
        return False
    return degree in (90, 270)


def is_landscape_degree(degree: Optional[int]) -> bool:
    if degree is None:
        return False
    return degree in (0, 180)


def degree_matches_target_rotation(actual_degree: Optional[int], target_degree: int) -> bool:
    if target_degree in (90, 270):
        return is_portrait_degree(actual_degree)
    return is_landscape_degree(actual_degree)


def extract_display_degree_from_layout_args(
    layout_args: Sequence[str],
    persistent_id: str,
) -> Optional[int]:
    id_pattern = f"id:{persistent_id}"
    for arg in layout_args:
        if id_pattern not in arg:
            continue
        degree_match = re.search(r"\bdegree:(\d+)\b", arg)
        if degree_match:
            return int(degree_match.group(1))
    return None


class ScreenRotatorApp(rumps.App):
    CONFIG_FILE = os.path.expanduser("~/.screen_rotator_config.json")
    LAUNCH_AGENT_LABEL = "com.screenrotator.app"

    @rumps.timer(0.2)
    def process_ui_queue(self, _):
        try:
            while True:
                task = self.ui_queue.get_nowait()
                if task[0] == "notification":
                    rumps.notification(task[1], task[2], task[3])
                elif task[0] == "alert":
                    rumps.alert(task[1], task[2])
                elif task[0] == "update_menu":
                    self.update_menu()
        except queue.Empty:
            pass

    def notify(self, title: str, subtitle: str, message: str = "") -> None:
        self.ui_queue.put(("notification", title, subtitle, message))

    def alert(self, title: str, message: str) -> None:
        self.ui_queue.put(("alert", title, message))

    def queue_update_menu(self) -> None:
        self.ui_queue.put(("update_menu",))

    def __init__(self):
        super().__init__(STATUS_ITEM_TITLE, icon=None)
        self.ui_queue = queue.Queue()
        self.action_lock = threading.Lock()
        self.recording_lock = threading.Lock()
        
        self.target_display_persistent_id: Optional[str] = None
        self.displayplacer_path = self.find_displayplacer()

        if not self.displayplacer_path:
            rumps.alert(
                "Error",
                "displayplacer not found. Install with: brew install jakehilborn/jakehilborn/displayplacer",
            )
            rumps.quit_application()
            return

        self.shortcuts: Dict[str, Optional[Dict[str, Union[List[str], str]]]] = {
            "toggle": None,
            "rotate_90": None,
            "rotate_0": None,
            "rotate_270": None,
        }

        self.recording_action: Optional[str] = None
        self.recorded_keys: List[str] = []
        self.recorded_non_modifier = False
        self.recording_listener: Optional[keyboard.Listener] = None
        self.hotkey_listener: Optional[keyboard.Listener] = None

        self.load_config()
        if not self.target_display_persistent_id:
            self.auto_select_target()

        self.setup_display_observer()
        self.update_menu()
        self.start_hotkey_listener()

    def setup_display_observer(self):
        """Listen to native macOS display changes to sync state."""
        nc = AppKit.NSNotificationCenter.defaultCenter()
        nc.addObserver_selector_name_object_(
            self,
            "displayParametersChanged:",
            AppKit.NSApplicationDidChangeScreenParametersNotification,
            None
        )
        
    def displayParametersChanged_(self, notification):
        logging.info("System display parameters changed, updating UI state.")
        self.queue_update_menu()

    def find_displayplacer(self) -> Optional[str]:
        displayplacer_path = shutil.which("displayplacer")
        if displayplacer_path:
            return displayplacer_path

        for path in ("/opt/homebrew/bin/displayplacer", "/usr/local/bin/displayplacer"):
            if os.path.exists(path):
                return path
        return None

    def read_config(self) -> Dict[str, object]:
        if not os.path.exists(self.CONFIG_FILE):
            return {}
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
                if isinstance(config, dict):
                    return config
        except Exception as error:
            logging.error(f"Error reading config: {error}")
        return {}

    def write_config(self, config: Dict[str, object]) -> None:
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as config_file:
                json.dump(config, config_file, indent=2)
        except Exception as error:
            logging.error(f"Error writing config: {error}")

    def load_config(self) -> None:
        config = self.read_config()
        self.target_display_persistent_id = config.get("target_display_id")

        saved_shortcuts = config.get("shortcuts", {})
        if not isinstance(saved_shortcuts, dict):
            return

        for action in self.shortcuts:
            shortcut = saved_shortcuts.get(action)
            if not isinstance(shortcut, dict):
                continue
            keys = shortcut.get("keys")
            if not isinstance(keys, list):
                continue
            normalized_keys = order_shortcut_keys(keys)
            if not normalized_keys:
                continue
            self.shortcuts[action] = {
                "keys": normalized_keys,
                "display": shortcut.get("display") or format_shortcut_display(normalized_keys),
            }

    def save_config(self) -> None:
        config = self.read_config()
        config["shortcuts"] = self.shortcuts
        config["target_display_id"] = self.target_display_persistent_id
        self.write_config(config)

    def auto_select_target(self) -> None:
        displays = self.list_displays()
        for display in displays:
            if display["is_external"]:
                self.target_display_persistent_id = display["persistent_id"]
                return
        if displays:
            self.target_display_persistent_id = displays[0]["persistent_id"]

    def update_menu(self) -> None:
        self.menu.clear()

        # Added threading for menu actions to prevent blocking the main UI thread during rotation
        self.menu.add(
            rumps.MenuItem(
                f"Toggle Screen  [{self.get_shortcut_display('toggle')}]",
                callback=lambda _: threading.Thread(target=self.toggle, args=(None,), daemon=True).start(),
            )
        )
        self.menu.add(rumps.separator)
        self.menu.add(
            rumps.MenuItem(
                f"Rotate Standard (0°)  [{self.get_shortcut_display('rotate_0')}]",
                callback=lambda _: threading.Thread(target=self.set_rotation, args=(0,), daemon=True).start(),
            )
        )
        self.menu.add(
            rumps.MenuItem(
                f"Rotate Vertical (90°)  [{self.get_shortcut_display('rotate_90')}]",
                callback=lambda _: threading.Thread(target=self.set_rotation, args=(90,), daemon=True).start(),
            )
        )
        self.menu.add(
            rumps.MenuItem(
                f"Rotate Vertical (270°)  [{self.get_shortcut_display('rotate_270')}]",
                callback=lambda _: threading.Thread(target=self.set_rotation, args=(270,), daemon=True).start(),
            )
        )
        self.menu.add(rumps.separator)

        displays_menu = rumps.MenuItem("Target Display")
        available_displays = self.list_displays()
        available_ids = {display["persistent_id"] for display in available_displays}

        if self.target_display_persistent_id and self.target_display_persistent_id not in available_ids:
            self.auto_select_target()
            self.save_config()

        if not available_displays:
            displays_menu.add(rumps.MenuItem("No displays detected"))
        else:
            for display in available_displays:
                display_type = "External" if display["is_external"] else "Built-in"
                # If there's an actual rotation, show it in the menu
                current_degree = display.get("degree", "?")
                display_name = f"{display['name']} ({display_type}) [{current_degree}°]"
                
                item = rumps.MenuItem(
                    display_name,
                    callback=lambda sender, pid=display["persistent_id"]: self.select_target(sender, pid),
                )
                item.state = display["persistent_id"] == self.target_display_persistent_id
                displays_menu.add(item)

        self.menu.add(displays_menu)
        self.menu.add(rumps.MenuItem("Refresh Displays", callback=self.refresh_displays))

        shortcuts_menu = rumps.MenuItem("Set Shortcuts")
        shortcuts_menu.add(
            rumps.MenuItem("Record Toggle...", callback=lambda _: self.start_recording("toggle"))
        )
        shortcuts_menu.add(
            rumps.MenuItem("Record 0°...", callback=lambda _: self.start_recording("rotate_0"))
        )
        shortcuts_menu.add(
            rumps.MenuItem("Record 90°...", callback=lambda _: self.start_recording("rotate_90"))
        )
        shortcuts_menu.add(
            rumps.MenuItem("Record 270°...", callback=lambda _: self.start_recording("rotate_270"))
        )
        shortcuts_menu.add(rumps.separator)
        shortcuts_menu.add(rumps.MenuItem("Clear All", callback=self.clear_all_shortcuts))
        self.menu.add(shortcuts_menu)
        self.menu.add(rumps.separator)

        launch_item = rumps.MenuItem("Launch at Login", callback=self.toggle_launch_at_login)
        launch_item.state = self.is_launch_at_login_enabled()
        self.menu.add(launch_item)

    def refresh_displays(self, _) -> None:
        available_ids = {display["persistent_id"] for display in self.list_displays()}
        if not self.target_display_persistent_id or self.target_display_persistent_id not in available_ids:
            self.auto_select_target()
        self.update_menu()
        self.save_config()
        self.notify("Display List Refreshed", "", "")

    def select_target(self, sender, persistent_id: str) -> None:
        self.target_display_persistent_id = persistent_id
        self.save_config()
        self.update_menu()
        self.notify("Display Selected", "Selection saved", persistent_id[:12] + "...")

    def list_displays(self) -> List[Dict[str, Union[str, bool]]]:
        _, output, _ = self.run_displayplacer(["list"])
        screens = output.split("Persistent screen id:")
        results: List[Dict[str, Union[str, bool]]] = []

        for index, screen in enumerate(screens):
            if not screen.strip():
                continue

            id_match = re.match(r"^\s*([A-Fa-f0-9-]+)", screen)
            if not id_match:
                continue
            persistent_id = id_match.group(1)
            lower_screen = screen.lower()
            is_built_in = "built in" in lower_screen or "built-in" in lower_screen
            is_external = "external" in lower_screen and not is_built_in

            type_match = re.search(r"Type:\s*(.+)", screen)
            name = f"Display {index}"
            if type_match:
                name = type_match.group(1).split("\n")[0].strip()

            degree = "?"
            rotation_match = re.search(r"Rotation:\s*(\d+)", screen)
            if rotation_match:
                degree = rotation_match.group(1)

            results.append(
                {
                    "persistent_id": persistent_id,
                    "name": name,
                    "is_external": is_external,
                    "is_built_in": is_built_in,
                    "degree": degree,
                }
            )

        return results

    def get_display_info(self, persistent_id: str) -> Optional[Dict[str, Union[int, str]]]:
        _, output, _ = self.run_displayplacer(["list"])
        screens = output.split("Persistent screen id:")
        for screen in screens:
            if not re.search(rf"^\s*{re.escape(persistent_id)}\b", screen):
                continue
            info: Dict[str, Union[int, str]] = {}
            resolution_match = re.search(r"Resolution:\s*(\d+x\d+)", screen)
            if resolution_match:
                info["res"] = resolution_match.group(1)
            origin_match = re.search(r"Origin:\s*\(([-\d]+),\s*([-\d]+)\)", screen)
            if origin_match:
                info["origin"] = f"({origin_match.group(1)},{origin_match.group(2)})"
            rotation_match = re.search(r"Rotation:\s*(\d+)", screen)
            if rotation_match:
                info["degree"] = int(rotation_match.group(1))
            for key in ("Hertz", "Color Depth", "Scaling"):
                property_match = re.search(rf"{key}:\s*([^\n]+)", screen)
                if property_match:
                    info[key.lower().replace(" ", "_")] = property_match.group(1).strip()
            return info
        return None

    def save_current_layout(self, mode_key: str) -> None:
        _, output, _ = self.run_displayplacer(["list"])
        restore_command = None
        for line in reversed(output.strip().splitlines()):
            if line.strip().startswith("displayplacer"):
                restore_command = parse_saved_layout_command(line.strip())
                break
        if not restore_command:
            return

        config = self.read_config()
        layouts = config.setdefault("layouts", {})
        if isinstance(layouts, dict):
            layouts[mode_key] = restore_command
            self.write_config(config)

    def load_saved_layout(self, mode_key: str) -> Optional[List[str]]:
        config = self.read_config()
        layouts = config.get("layouts", {})
        if not isinstance(layouts, dict):
            return None
        return parse_saved_layout_command(layouts.get(mode_key))

    def wait_for_rotation(self, target_degree: int, timeout_seconds: float = 3.0) -> bool:
        if not self.target_display_persistent_id:
            return False
        attempts = max(1, int(timeout_seconds / 0.2))
        for _ in range(attempts):
            info = self.get_display_info(self.target_display_persistent_id)
            current_degree = int(info.get("degree", -1)) if info else None
            if degree_matches_target_rotation(current_degree, target_degree):
                return True
            threading.Event().wait(0.2)
        return False

    def set_rotation(self, target_degree: int) -> None:
        if not self.action_lock.acquire(blocking=False):
            logging.info("Rotation action already in progress, ignoring duplicate request.")
            return

        try:
            if target_degree not in (0, 90, 270):
                self.notify("Invalid Rotation", str(target_degree), "")
                return

            if not self.target_display_persistent_id:
                self.auto_select_target()
                if not self.target_display_persistent_id:
                    self.notify("Error", "No external display found", "")
                    return
                self.queue_update_menu()

            display_info = self.get_display_info(self.target_display_persistent_id)
            if not display_info:
                self.auto_select_target()
                if self.target_display_persistent_id:
                    display_info = self.get_display_info(self.target_display_persistent_id)
                    self.queue_update_menu()
                if not display_info:
                    self.notify("Error", "Selected display not found", "")
                    return

            current_rotation = int(display_info.get("degree", 0))
            if current_rotation == target_degree:
                logging.info(f"Display is already at target degree {target_degree}")
                return

            current_mode = "portrait" if current_rotation in (90, 270) else "landscape"
            target_mode = "portrait" if target_degree in (90, 270) else "landscape"

            self.save_current_layout(current_mode)
            saved_layout = self.load_saved_layout(target_mode)
            if saved_layout:
                saved_target_degree = extract_display_degree_from_layout_args(
                    saved_layout,
                    self.target_display_persistent_id,
                )
                if degree_matches_target_rotation(saved_target_degree, target_degree):
                    for attempt in range(3):
                        return_code, _, error = self.run_displayplacer(saved_layout)
                        if return_code == 0 and self.wait_for_rotation(target_degree):
                            self.save_current_layout(target_mode)
                            self.notify("Success", f"Restored {target_mode} layout", "")
                            return
                        threading.Event().wait(0.5)
                    logging.warning(f"Saved layout did not apply target rotation ({target_mode}): {error}")
                else:
                    logging.info(
                        f"Ignoring stale saved layout '{target_mode}' "
                        f"(target display degree: {saved_target_degree})"
                    )

            current_resolution = display_info.get("res")
            if not current_resolution:
                self.notify("Error", "Could not determine display resolution", "")
                return
            current_resolution = str(current_resolution)
            current_is_portrait = current_rotation in (90, 270)
            target_is_portrait = target_degree in (90, 270)
            target_resolution = current_resolution

            if current_is_portrait != target_is_portrait and "x" in current_resolution:
                width, height = current_resolution.split("x", 1)
                target_resolution = f"{height}x{width}"

            current_origin = display_info.get("origin", "(0,0)")

            command_arg = (
                f"id:{self.target_display_persistent_id} "
                f"res:{target_resolution} origin:{current_origin} degree:{target_degree}"
            )
            for attempt in range(3):
                return_code, _, error = self.run_displayplacer([command_arg])
                if return_code == 0 and self.wait_for_rotation(target_degree):
                    self.save_current_layout(target_mode)
                    self.notify("Success", f"Target rotated to {target_degree}°", "")
                    return
                threading.Event().wait(0.5)

            self.notify("Failed", "Rotation failed after retries", error[:180] if error else "")
        finally:
            self.action_lock.release()

    def toggle(self, _) -> None:
        if not self.target_display_persistent_id:
            self.auto_select_target()
            if not self.target_display_persistent_id:
                self.notify("Error", "No external display found", "")
                return
            self.queue_update_menu()

        display_info = self.get_display_info(self.target_display_persistent_id)
        if not display_info:
            self.auto_select_target()
            if self.target_display_persistent_id:
                display_info = self.get_display_info(self.target_display_persistent_id)
                self.queue_update_menu()
            if not display_info:
                self.notify("Error", "Selected display not found", "")
                return

        target = 0 if int(display_info.get("degree", 0)) in (90, 270) else 90
        self.set_rotation(target)

    def get_shortcut_display(self, action: str) -> str:
        shortcut = self.shortcuts.get(action)
        if isinstance(shortcut, dict) and shortcut.get("display"):
            return str(shortcut["display"])
        return "None"

    def normalize_key_name(self, key) -> Optional[str]:
        if isinstance(key, KeyCode) and key.char:
            return key.char.lower()

        key_name_map = {
            Key.ctrl: "ctrl",
            Key.ctrl_l: "ctrl",
            Key.ctrl_r: "ctrl",
            Key.shift: "shift",
            Key.shift_l: "shift",
            Key.shift_r: "shift",
            Key.cmd: "cmd",
            Key.cmd_l: "cmd",
            Key.cmd_r: "cmd",
            Key.alt: "alt",
            Key.alt_l: "alt",
            Key.alt_r: "alt",
            Key.alt_gr: "alt",
            Key.space: "space",
            Key.enter: "enter",
            Key.tab: "tab",
            Key.esc: "esc",
        }
        if key in key_name_map:
            return key_name_map[key]

        key_repr = str(key)
        if key_repr.startswith("Key."):
            return key_repr.split(".", 1)[1].lower()
        return None

    def start_recording(self, action: str) -> None:
        with self.recording_lock:
            self.recording_action = action
            self.recorded_keys = []
            self.recorded_non_modifier = False

            if self.recording_listener:
                try:
                    self.recording_listener.stop()
                except Exception:
                    pass
                self.recording_listener = None

            self.notify("Record Shortcut", f"Press shortcut for {action.replace('_', ' ')}", "Press Esc to cancel")

            def on_press(key):
                if self.recording_action is None:
                    return False

                key_name = self.normalize_key_name(key)
                if key_name == "esc":
                    self.recording_action = None
                    self.recorded_keys = []
                    self.recorded_non_modifier = False
                    self.notify("Shortcut", "Recording cancelled", "")
                    self.queue_update_menu()
                    return False
                if not key_name:
                    return None

                if key_name not in self.recorded_keys:
                    self.recorded_keys.append(key_name)
                    if not is_modifier_key_name(key_name):
                        self.recorded_non_modifier = True
                return None

            def on_release(_):
                if self.recording_action is None:
                    return False
                if not self.recorded_non_modifier:
                    return None
                self.save_recorded_shortcut()
                return False

            def start_recording_listener():
                with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                    self.recording_listener = listener
                    listener.join()
                self.recording_listener = None

            threading.Thread(target=start_recording_listener, daemon=True).start()

    def save_recorded_shortcut(self) -> None:
        if not self.recording_action or not self.recorded_keys:
            return

        ordered_keys = order_shortcut_keys(self.recorded_keys)
        if not any(not is_modifier_key_name(key) for key in ordered_keys):
            self.notify("Invalid Shortcut", "Use at least one non-modifier key", "")
            self.recording_action = None
            self.recorded_keys = []
            self.recorded_non_modifier = False
            return

        action = self.recording_action
        display = format_shortcut_display(ordered_keys)
        self.shortcuts[action] = {"keys": ordered_keys, "display": display}
        self.recording_action = None
        self.recorded_keys = []
        self.recorded_non_modifier = False

        self.save_config()
        self.queue_update_menu()
        self.start_hotkey_listener()
        self.notify("Shortcut Saved", action.replace("_", " ").title(), display)

    def key_name_to_pynput_key(self, key_name: str):
        normalized = key_name.lower()
        mapping = {
            "ctrl": Key.ctrl,
            "shift": Key.shift,
            "alt": Key.alt,
            "cmd": Key.cmd,
            "space": Key.space,
            "enter": Key.enter,
            "tab": Key.tab,
            "esc": Key.esc,
        }
        if normalized in mapping:
            return mapping[normalized]
        if len(normalized) == 1:
            return KeyCode.from_char(normalized)
        if hasattr(Key, normalized):
            return getattr(Key, normalized)
        return None

    def parse_hotkey_keys(self, key_names: Sequence[str]):
        parsed = set()
        for key_name in order_shortcut_keys(key_names):
            key_value = self.key_name_to_pynput_key(key_name)
            if key_value is None:
                return None
            parsed.add(key_value)
        return parsed or None

    def execute_shortcut_action(self, action: str) -> None:
        target_rotation = action_to_rotation(action)
        if action == "toggle":
            threading.Thread(target=self.toggle, args=(None,), daemon=True).start()
        elif target_rotation is not None:
            threading.Thread(target=self.set_rotation, args=(target_rotation,), daemon=True).start()

    def handle_hotkey_event(self, hotkeys: Sequence[keyboard.HotKey], key, is_press: bool) -> None:
        listener = self.hotkey_listener
        if not listener:
            return
        canonical = listener.canonical(key)
        for hotkey in hotkeys:
            if is_press:
                hotkey.press(canonical)
            else:
                hotkey.release(canonical)

    def start_hotkey_listener(self) -> None:
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
            self.hotkey_listener = None

        hotkeys = []
        for action, shortcut in self.shortcuts.items():
            if not isinstance(shortcut, dict):
                continue
            keys = shortcut.get("keys")
            if not isinstance(keys, list):
                continue
            parsed = self.parse_hotkey_keys(keys)
            if not parsed:
                continue
            hotkeys.append(
                keyboard.HotKey(parsed, lambda action_name=action: self.execute_shortcut_action(action_name))
            )

        if not hotkeys:
            return

        self.hotkey_listener = keyboard.Listener(
            on_press=lambda key: self.handle_hotkey_event(hotkeys, key, True),
            on_release=lambda key: self.handle_hotkey_event(hotkeys, key, False),
        )
        self.hotkey_listener.start()

    def clear_all_shortcuts(self, _) -> None:
        for action in self.shortcuts:
            self.shortcuts[action] = None
        self.save_config()
        self.update_menu()
        self.start_hotkey_listener()
        self.notify("Shortcuts Cleared", "", "")

    def run_command(self, command: Sequence[str], timeout: float = 10.0):
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as error:
            logging.error(f"Command timed out after {timeout}s: {command}")
            return -1, "", f"Command timed out: {error}"
        except Exception as error:
            logging.error(f"Error running command {command}: {error}")
            return -1, "", str(error)

    def run_displayplacer(self, args: Sequence[str]):
        command = [self.displayplacer_path, *args]
        return self.run_command(command)

    def get_launch_agent_path(self) -> str:
        return os.path.expanduser(f"~/Library/LaunchAgents/{self.LAUNCH_AGENT_LABEL}.plist")

    def is_launch_at_login_enabled(self) -> bool:
        return_code, _, _ = self.run_command(["launchctl", "list", self.LAUNCH_AGENT_LABEL], timeout=5.0)
        if return_code == 0:
            return True
        return os.path.exists(self.get_launch_agent_path())

    def get_launch_program_arguments(self) -> List[str]:
        if getattr(sys, "frozen", False):
            app_bundle_path = os.path.abspath(
                os.path.join(os.path.dirname(sys.executable), "..", "..", "..")
            )
            return ["/usr/bin/open", "-a", app_bundle_path]
        return [sys.executable, os.path.abspath(__file__)]

    def write_launch_agent_plist(self) -> None:
        launch_agent_path = self.get_launch_agent_path()
        os.makedirs(os.path.dirname(launch_agent_path), exist_ok=True)
        plist_data = {
            "Label": self.LAUNCH_AGENT_LABEL,
            "ProgramArguments": self.get_launch_program_arguments(),
            "RunAtLoad": True,
            "KeepAlive": False,
        }
        with open(launch_agent_path, "wb") as plist_file:
            plistlib.dump(plist_data, plist_file)

    def load_launch_agent(self):
        launch_agent_path = self.get_launch_agent_path()
        return self.run_command(["launchctl", "bootstrap", f"gui/{os.getuid()}", launch_agent_path], timeout=5.0)

    def unload_launch_agent(self):
        launch_agent_path = self.get_launch_agent_path()
        return self.run_command(["launchctl", "bootout", f"gui/{os.getuid()}", launch_agent_path], timeout=5.0)

    def toggle_launch_at_login(self, sender) -> None:
        launch_agent_path = self.get_launch_agent_path()
        enabled = self.is_launch_at_login_enabled()

        if enabled:
            self.unload_launch_agent()
            if os.path.exists(launch_agent_path):
                os.remove(launch_agent_path)
            sender.state = 0
            self.notify("Launch at Login", "Disabled", "")
            return

        try:
            self.write_launch_agent_plist()
            return_code, _, error = self.load_launch_agent()
            if return_code != 0 and "already loaded" not in error.lower():
                raise RuntimeError(error.strip() or "launchctl bootstrap failed")
            sender.state = 1
            self.notify("Launch at Login", "Enabled", "")
        except Exception as error:
            sender.state = 0
            self.notify("Launch at Login", "Failed to enable", str(error)[:180])


if __name__ == "__main__":
    ScreenRotatorApp().run()
