---
name: cluster-0
description: "Skill for the Cluster_0 area of 26.01.30 Screen Rotate. 15 symbols across 1 files."
---

# Cluster_0

15 symbols | 1 files | Cohesion: 74%

## When to Use

- Understanding how initWithApp_, process_ui_queue, alert work
- Modifying cluster_0-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `screen_rotator.py` | initWithApp_, process_ui_queue, alert, __init__, setup_display_observer (+10) |

## Entry Points

Start here when exploring this area:

- **`initWithApp_`** (Function) — `screen_rotator.py:79`
- **`process_ui_queue`** (Function) — `screen_rotator.py:189`
- **`alert`** (Function) — `screen_rotator.py:211`
- **`setup_display_observer`** (Function) — `screen_rotator.py:264`
- **`find_displayplacer`** (Function) — `screen_rotator.py:279`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `initWithApp_` | Function | `screen_rotator.py` | 79 |
| `process_ui_queue` | Function | `screen_rotator.py` | 189 |
| `alert` | Function | `screen_rotator.py` | 211 |
| `setup_display_observer` | Function | `screen_rotator.py` | 264 |
| `find_displayplacer` | Function | `screen_rotator.py` | 279 |
| `write_config` | Function | `screen_rotator.py` | 301 |
| `save_config` | Function | `screen_rotator.py` | 331 |
| `auto_select_target` | Function | `screen_rotator.py` | 337 |
| `update_menu` | Function | `screen_rotator.py` | 355 |
| `refresh_displays` | Function | `screen_rotator.py` | 433 |
| `select_target` | Function | `screen_rotator.py` | 441 |
| `list_displays` | Function | `screen_rotator.py` | 447 |
| `get_shortcut_display` | Function | `screen_rotator.py` | 742 |
| `__init__` | Function | `screen_rotator.py` | 219 |
| `_is_target_built_in` | Function | `screen_rotator.py` | 346 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Refresh_displays → Run_command` | cross_community | 6 |
| `Toggle → Run_command` | cross_community | 6 |
| `Clear_all_shortcuts → Run_command` | cross_community | 6 |
| `Process_ui_queue → Run_command` | cross_community | 6 |
| `Refresh_displays → Read_config` | cross_community | 4 |
| `Refresh_displays → Write_config` | intra_community | 4 |
| `Clear_all_shortcuts → Read_config` | cross_community | 4 |
| `Clear_all_shortcuts → Write_config` | cross_community | 4 |
| `Process_ui_queue → Read_config` | cross_community | 4 |
| `Process_ui_queue → Write_config` | intra_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Tests | 4 calls |
| Cluster_1 | 3 calls |
| Cluster_7 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "initWithApp_"})` — see callers and callees
2. `gitnexus_query({query: "cluster_0"})` — find related execution flows
3. Read key files listed above for implementation details
