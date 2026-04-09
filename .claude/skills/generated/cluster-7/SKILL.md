---
name: cluster-7
description: "Skill for the Cluster_7 area of 26.01.30 Screen Rotate. 8 symbols across 1 files."
---

# Cluster_7

8 symbols | 1 files | Cohesion: 90%

## When to Use

- Understanding how run_command, get_launch_agent_path, is_launch_at_login_enabled work
- Modifying cluster_7-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `screen_rotator.py` | run_command, get_launch_agent_path, is_launch_at_login_enabled, get_launch_program_arguments, write_launch_agent_plist (+3) |

## Entry Points

Start here when exploring this area:

- **`run_command`** (Function) — `screen_rotator.py:943`
- **`get_launch_agent_path`** (Function) — `screen_rotator.py:958`
- **`is_launch_at_login_enabled`** (Function) — `screen_rotator.py:961`
- **`get_launch_program_arguments`** (Function) — `screen_rotator.py:966`
- **`write_launch_agent_plist`** (Function) — `screen_rotator.py:972`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `run_command` | Function | `screen_rotator.py` | 943 |
| `get_launch_agent_path` | Function | `screen_rotator.py` | 958 |
| `is_launch_at_login_enabled` | Function | `screen_rotator.py` | 961 |
| `get_launch_program_arguments` | Function | `screen_rotator.py` | 966 |
| `write_launch_agent_plist` | Function | `screen_rotator.py` | 972 |
| `load_launch_agent` | Function | `screen_rotator.py` | 984 |
| `unload_launch_agent` | Function | `screen_rotator.py` | 988 |
| `toggle_launch_at_login` | Function | `screen_rotator.py` | 992 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Refresh_displays → Run_command` | cross_community | 6 |
| `Toggle → Run_command` | cross_community | 6 |
| `Clear_all_shortcuts → Run_command` | cross_community | 6 |
| `Process_ui_queue → Run_command` | cross_community | 6 |
| `Toggle_launch_at_login → Run_command` | intra_community | 3 |
| `Toggle_launch_at_login → Get_launch_agent_path` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_1 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "run_command"})` — see callers and callees
2. `gitnexus_query({query: "cluster_7"})` — find related execution flows
3. Read key files listed above for implementation details
