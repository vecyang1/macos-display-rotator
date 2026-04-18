import unittest
from unittest.mock import MagicMock, patch

import screen_rotator


class ScreenRotatorHelperTests(unittest.TestCase):
    def test_status_item_title_is_visible_ascii(self):
        self.assertEqual(screen_rotator.STATUS_ITEM_TITLE, "SR")

    def test_action_to_rotation_includes_all_rotate_actions(self):
        self.assertEqual(screen_rotator.action_to_rotation("rotate_0"), 0)
        self.assertEqual(screen_rotator.action_to_rotation("rotate_90"), 90)
        self.assertEqual(screen_rotator.action_to_rotation("rotate_270"), 270)
        self.assertIsNone(screen_rotator.action_to_rotation("toggle"))

    def test_order_shortcut_keys_puts_modifiers_first(self):
        ordered = screen_rotator.order_shortcut_keys(["r", "shift", "ctrl", "shift"])
        self.assertEqual(ordered, ["ctrl", "shift", "r"])

    def test_format_shortcut_display_uses_symbols_and_uppercase(self):
        display = screen_rotator.format_shortcut_display(["shift", "ctrl", "r"])
        self.assertEqual(display, "⌃⇧R")

    def test_parse_saved_layout_command_supports_displayplacer_string(self):
        cmd = (
            'displayplacer "id:AAA res:1920x1080 degree:0" '
            '"id:BBB res:1080x1920 degree:90"'
        )
        parsed = screen_rotator.parse_saved_layout_command(cmd)
        self.assertEqual(
            parsed,
            [
                "id:AAA res:1920x1080 degree:0",
                "id:BBB res:1080x1920 degree:90",
            ],
        )

    def test_extract_display_degree_from_layout_args(self):
        args = [
            "id:AAA res:1920x1080 degree:0",
            "id:BBB res:1080x1920 degree:90",
        ]
        self.assertEqual(
            screen_rotator.extract_display_degree_from_layout_args(args, "AAA"),
            0,
        )
        self.assertEqual(
            screen_rotator.extract_display_degree_from_layout_args(args, "BBB"),
            90,
        )
        self.assertIsNone(
            screen_rotator.extract_display_degree_from_layout_args(args, "CCC"),
        )

    def test_degree_matches_target_rotation(self):
        self.assertTrue(screen_rotator.degree_matches_target_rotation(90, 90))
        self.assertTrue(screen_rotator.degree_matches_target_rotation(270, 90))
        self.assertTrue(screen_rotator.degree_matches_target_rotation(0, 0))
        self.assertTrue(screen_rotator.degree_matches_target_rotation(180, 0))
        self.assertFalse(screen_rotator.degree_matches_target_rotation(0, 90))
        self.assertFalse(screen_rotator.degree_matches_target_rotation(90, 0))

    def test_set_rotation_ignores_stale_saved_layout_and_falls_back(self):
        class DummyApp:
            target_display_persistent_id = "BBB"

        app = DummyApp()
        app.get_display_info = MagicMock(return_value={"degree": 90, "res": "1080x1920"})
        app.save_current_layout = MagicMock()
        app.load_saved_layout = MagicMock(return_value=["id:BBB res:1080x1920 degree:90"])
        app.run_displayplacer = MagicMock(return_value=(0, "", ""))
        app.wait_for_rotation = MagicMock(return_value=True)
        app.notify = MagicMock()

        with patch("builtins.print"), patch.object(
            screen_rotator.rumps, "notification"
        ), patch.object(screen_rotator.rumps, "alert"):
            screen_rotator.ScreenRotatorApp.set_rotation(app, 0)

        self.assertEqual(app.load_saved_layout.call_args[0][0], "landscape")
        self.assertEqual(app.run_displayplacer.call_count, 1)
        fallback_args = app.run_displayplacer.call_args[0][0]
        self.assertEqual(len(fallback_args), 1)
        self.assertIn("degree:0", fallback_args[0])

    def test_set_rotation_falls_back_when_no_saved_layout_exists(self):
        class DummyApp:
            target_display_persistent_id = "BBB"

        app = DummyApp()
        app.get_display_info = MagicMock(return_value={"degree": 0, "res": "1920x1080"})
        app.save_current_layout = MagicMock()
        app.load_saved_layout = MagicMock(return_value=None)
        app.run_displayplacer = MagicMock(return_value=(0, "", ""))
        app.wait_for_rotation = MagicMock(return_value=True)
        app.notify = MagicMock()

        screen_rotator.ScreenRotatorApp.set_rotation(app, 90)

        fallback_args = app.run_displayplacer.call_args[0][0]
        self.assertEqual(len(fallback_args), 1)
        self.assertIn("degree:90", fallback_args[0])
        self.assertIn("res:1080x1920", fallback_args[0])

    def test_start_recording_suspends_hotkeys_and_ignores_reentry(self):
        class DummyApp:
            pass

        started_threads = []

        class FakeThread:
            def __init__(self, target, daemon):
                self.target = target
                self.daemon = daemon

            def start(self):
                started_threads.append(self.target)

        app = DummyApp()
        app.recording_action = None
        app.recorded_keys = []
        app.recorded_non_modifier = False
        app.recording_listener = None
        app.hotkey_listener = MagicMock()
        app.notify = MagicMock()
        app.queue_update_menu = MagicMock()
        app.stop_hotkey_listener = MagicMock(
            side_effect=lambda: setattr(app, "hotkey_listener", None)
        )

        with patch.object(screen_rotator.threading, "Thread", FakeThread):
            screen_rotator.ScreenRotatorApp.start_recording(app, "toggle")
            screen_rotator.ScreenRotatorApp.start_recording(app, "rotate_90")

        app.stop_hotkey_listener.assert_called_once()
        self.assertEqual(len(started_threads), 1)
        self.assertEqual(app.recording_action, "toggle")

    def test_recording_restarts_hotkeys_after_listener_exits(self):
        class DummyApp:
            pass

        events = []

        class ImmediateThread:
            def __init__(self, target, daemon):
                self.target = target
                self.daemon = daemon

            def start(self):
                self.target()

        class FakeListener:
            def __init__(self, on_press, on_release):
                self.on_press = on_press
                self.on_release = on_release

            def __enter__(self):
                events.append("listener_enter")
                return self

            def __exit__(self, exc_type, exc, traceback):
                events.append("listener_exit")

            def join(self):
                self.on_press(screen_rotator.Key.cmd)
                self.on_press(screen_rotator.KeyCode.from_char("r"))
                self.on_release(screen_rotator.KeyCode.from_char("r"))
                events.append("listener_join_done")

        app = DummyApp()
        app.recording_action = None
        app.recorded_keys = []
        app.recorded_non_modifier = False
        app.recording_listener = None
        app.hotkey_listener = None
        app.shortcuts = {
            "toggle": None,
            "rotate_90": None,
            "rotate_0": None,
            "rotate_270": None,
        }
        app.notify = MagicMock()
        app.queue_update_menu = MagicMock()
        app.save_config = MagicMock()
        app.start_hotkey_listener = MagicMock(side_effect=lambda: events.append("start_hotkeys"))
        app.stop_hotkey_listener = MagicMock()
        app.normalize_key_name = screen_rotator.ScreenRotatorApp.normalize_key_name.__get__(app)
        app.save_recorded_shortcut = screen_rotator.ScreenRotatorApp.save_recorded_shortcut.__get__(app)

        with patch.object(screen_rotator.threading, "Thread", ImmediateThread), patch.object(
            screen_rotator.keyboard, "Listener", FakeListener
        ):
            screen_rotator.ScreenRotatorApp.start_recording(app, "toggle")

        self.assertEqual(app.shortcuts["toggle"]["keys"], ["cmd", "r"])
        self.assertLess(events.index("listener_exit"), events.index("start_hotkeys"))

    def test_recording_listener_failure_restores_hotkeys_and_clears_state(self):
        class DummyApp:
            pass

        class ImmediateThread:
            def __init__(self, target, daemon):
                self.target = target
                self.daemon = daemon

            def start(self):
                self.target()

        def raise_listener_error(*_args, **_kwargs):
            raise RuntimeError("event tap unavailable")

        app = DummyApp()
        app.recording_action = None
        app.recorded_keys = []
        app.recorded_non_modifier = False
        app.recording_listener = None
        app.hotkey_listener = None
        app.notify = MagicMock()
        app.queue_update_menu = MagicMock()
        app.start_hotkey_listener = MagicMock()
        app.stop_hotkey_listener = MagicMock()
        app.normalize_key_name = screen_rotator.ScreenRotatorApp.normalize_key_name.__get__(app)

        with patch.object(screen_rotator.threading, "Thread", ImmediateThread), patch.object(
            screen_rotator.keyboard, "Listener", raise_listener_error
        ):
            screen_rotator.ScreenRotatorApp.start_recording(app, "toggle")

        self.assertIsNone(app.recording_action)
        self.assertEqual(app.recorded_keys, [])
        self.assertFalse(app.recorded_non_modifier)
        app.start_hotkey_listener.assert_called_once()
        app.notify.assert_any_call("Shortcut", "Recording failed", "event tap unavailable")


if __name__ == "__main__":
    unittest.main()
