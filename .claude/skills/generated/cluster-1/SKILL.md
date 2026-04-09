---
name: cluster-1
description: "Skill for the Cluster_1 area of 26.01.30 Screen Rotate. 13 symbols across 1 files."
---

# Cluster_1

13 symbols | 1 files | Cohesion: 70%

## When to Use

- Understanding how displayParametersChanged_, is_modifier_key_name, notify work
- Modifying cluster_1-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `screen_rotator.py` | displayParametersChanged_, is_modifier_key_name, notify, queue_update_menu, _show_revert_dialog (+8) |

## Entry Points

Start here when exploring this area:

- **`displayParametersChanged_`** (Function) — `screen_rotator.py:86`
- **`is_modifier_key_name`** (Function) — `screen_rotator.py:95`
- **`notify`** (Function) — `screen_rotator.py:208`
- **`queue_update_menu`** (Function) — `screen_rotator.py:214`
- **`normalize_key_name`** (Function) — `screen_rotator.py:748`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `displayParametersChanged_` | Function | `screen_rotator.py` | 86 |
| `is_modifier_key_name` | Function | `screen_rotator.py` | 95 |
| `notify` | Function | `screen_rotator.py` | 208 |
| `queue_update_menu` | Function | `screen_rotator.py` | 214 |
| `normalize_key_name` | Function | `screen_rotator.py` | 748 |
| `start_recording` | Function | `screen_rotator.py` | 763 |
| `on_press` | Function | `screen_rotator.py` | 784 |
| `start_recording_listener` | Function | `screen_rotator.py` | 817 |
| `_show_revert_dialog` | Function | `screen_rotator.py` | 552 |
| `_start_revert_countdown` | Function | `screen_rotator.py` | 571 |
| `_auto_revert` | Function | `screen_rotator.py` | 588 |
| `_confirm_rotation` | Function | `screen_rotator.py` | 609 |
| `_revert_now` | Function | `screen_rotator.py` | 620 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Toggle → Notify` | cross_community | 3 |
| `Toggle → Queue_update_menu` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Tests | 1 calls |

## How to Explore

1. `gitnexus_context({name: "displayParametersChanged_"})` — see callers and callees
2. `gitnexus_query({query: "cluster_1"})` — find related execution flows
3. Read key files listed above for implementation details
