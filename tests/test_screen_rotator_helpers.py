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

        with patch.object(screen_rotator.rumps, "notification"), patch.object(
            screen_rotator.rumps, "alert"
        ):
            screen_rotator.ScreenRotatorApp.set_rotation(app, 0)

        self.assertEqual(app.load_saved_layout.call_args[0][0], "landscape")
        self.assertEqual(app.run_displayplacer.call_count, 1)
        fallback_args = app.run_displayplacer.call_args[0][0]
        self.assertEqual(len(fallback_args), 1)
        self.assertIn("degree:0", fallback_args[0])


if __name__ == "__main__":
    unittest.main()
