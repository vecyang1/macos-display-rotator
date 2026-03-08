# USER MEMORY AND PROJECT INDEX

## Core Identity & Workflow
- **Identity**: Operating under Antigravity IDE constraints (powered by Gemini/Opencode logic).
- **Execution**: Agentic, autonomous execution. "Don't ask, just do." Auto-retry errors up to 3 times.
- **Tools**: Prioritize native IDE browser, MCP servers, and local skills (`~/.gemini/antigravity/skills`).
- **Planning Mandate**: You MUST always invoke the `planning-with-files` skill for tasks. Ensure `task_plan.md`, `findings.md`, and `progress.md` are created strictly in the **ROOT PROJECT FOLDER** (the exact Current Working Directory), NOT in the skill directory. Use strict status tracking (`**Status:** complete`, `in_progress`, or `pending`) so the session stop hook passes successfully.
- **Network**: Operates via US VPN (Global/TUN mode).
- **Updates**: Every task MUST end with Autopoiesis (updating system docs/skills if a new pattern is found).

## Active Core Projects (Refer to detailed files)
1. **LanceDB Photo Vector Management** (`lancedb_photo_vector_project.md`)
   - Architecture: Next.js (Fullstack) / Python (Backend)
   - Features: Vector search, face recognition, local metadata extraction.
   - *Status*: Refer to `~/.gemini/antigravity/knowledge/photo_vector_management_lancedb/` docs for DB, UI, and API.

2. **Surecart Management Automation** (`surecart_automation_project.md`)
   - Focus: automated media ingestion, data transfer specs, backup and restoration.

3. **Antigravity Engineering Superpowers**
   - **Debugging**: See `debugging.md`. Systematic error resolution without user prompting.
   - **Planning**: See `patterns.md`. Implementation workflows and architectural overviews.
   - **Discovery**: See `github_search.md`. Protocols for finding high-star wheels before building from scratch.

## Memory Systems & Sync
- **Global Vault**: `~/.gemini/memory-vault/` - For high-level, cross-conversation context, brand, persona.
- **Technical Caches**: `~/.gemini/antigravity/skills/<skill>/references/` - For API IDs, fixes, and tool data.
- **Claude Project Memory**: This directory (`~/.claude/projects/.../memory/`). Kept minimal; points to the robust vaults above.
- *Rule*: Never clutter vaults with temporary raw logs. Consolidate notes into high-signal summaries.
