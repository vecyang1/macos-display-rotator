---
name: tests
description: "Skill for the Tests area of 26.01.30 Screen Rotate. 34 symbols across 3 files."
---

# Tests

34 symbols | 3 files | Cohesion: 73%

## When to Use

- Working with code in `tests/`
- Understanding how parse_saved_layout_command, extract_display_degree_from_layout_args, read_config work
- Modifying tests-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `screen_rotator.py` | parse_saved_layout_command, extract_display_degree_from_layout_args, read_config, get_display_info, save_current_layout (+21) |
| `tests/test_screen_rotator_helpers.py` | test_parse_saved_layout_command_supports_displayplacer_string, test_extract_display_degree_from_layout_args, test_action_to_rotation_includes_all_rotate_actions, test_order_shortcut_keys_puts_modifiers_first, test_format_shortcut_display_uses_symbols_and_uppercase (+1) |
| `tests/test_setup_options.py` | read_setup_options, test_excludes_do_not_remove_py2app_runtime_dependencies |

## Entry Points

Start here when exploring this area:

- **`parse_saved_layout_command`** (Function) — `screen_rotator.py:130`
- **`extract_display_degree_from_layout_args`** (Function) — `screen_rotator.py:170`
- **`read_config`** (Function) — `screen_rotator.py:289`
- **`get_display_info`** (Function) — `screen_rotator.py:486`
- **`save_current_layout`** (Function) — `screen_rotator.py:509`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `parse_saved_layout_command` | Function | `screen_rotator.py` | 130 |
| `extract_display_degree_from_layout_args` | Function | `screen_rotator.py` | 170 |
| `read_config` | Function | `screen_rotator.py` | 289 |
| `get_display_info` | Function | `screen_rotator.py` | 486 |
| `save_current_layout` | Function | `screen_rotator.py` | 509 |
| `load_saved_layout` | Function | `screen_rotator.py` | 525 |
| `wait_for_rotation` | Function | `screen_rotator.py` | 532 |
| `set_rotation` | Function | `screen_rotator.py` | 627 |
| `toggle` | Function | `screen_rotator.py` | 728 |
| `run_displayplacer` | Function | `screen_rotator.py` | 954 |
| `test_parse_saved_layout_command_supports_displayplacer_string` | Function | `tests/test_screen_rotator_helpers.py` | 24 |
| `test_extract_display_degree_from_layout_args` | Function | `tests/test_screen_rotator_helpers.py` | 38 |
| `action_to_rotation` | Function | `screen_rotator.py` | 91 |
| `key_name_to_pynput_key` | Function | `screen_rotator.py` | 862 |
| `parse_hotkey_keys` | Function | `screen_rotator.py` | 872 |
| `execute_shortcut_action` | Function | `screen_rotator.py` | 880 |
| `handle_hotkey_event` | Function | `screen_rotator.py` | 888 |
| `start_hotkey_listener` | Function | `screen_rotator.py` | 902 |
| `clear_all_shortcuts` | Function | `screen_rotator.py` | 935 |
| `test_action_to_rotation_includes_all_rotate_actions` | Function | `tests/test_screen_rotator_helpers.py` | 10 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Refresh_displays → Run_command` | cross_community | 6 |
| `Toggle → Run_command` | cross_community | 6 |
| `Clear_all_shortcuts → Run_command` | cross_community | 6 |
| `Process_ui_queue → Run_command` | cross_community | 6 |
| `Refresh_displays → Read_config` | cross_community | 4 |
| `Clear_all_shortcuts → Read_config` | cross_community | 4 |
| `Clear_all_shortcuts → Write_config` | cross_community | 4 |
| `Clear_all_shortcuts → Order_shortcut_keys` | cross_community | 4 |
| `Clear_all_shortcuts → Key_name_to_pynput_key` | intra_community | 4 |
| `Clear_all_shortcuts → Action_to_rotation` | intra_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_1 | 8 calls |
| Cluster_0 | 7 calls |
| Cluster_7 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "parse_saved_layout_command"})` — see callers and callees
2. `gitnexus_query({query: "tests"})` — find related execution flows
3. Read key files listed above for implementation details
