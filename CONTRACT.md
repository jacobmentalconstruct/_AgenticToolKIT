# Contract

This package is the project authority tool for agent-driven development. This document defines the contracts that govern its behavior, structure, and integration points.

---

## Builder Pledge

Anyone building on or modifying this package agrees to:

- **Isolation** — Keep the folder portable and self-contained. No external runtime dependencies beyond Python stdlib.
- **MCP-first** — The MCP path is primary for agent use. The CLI and UI are secondary interfaces to the same store layer.
- **Schema stability** — The SQLite schema is explicit, versioned, and migrated. Prefer additive changes (new columns with defaults, new tables) over destructive ones.
- **Single store** — UI and tool behavior are unified through `src/lib/journal_store.py`. There is exactly one code path to the database.
- **CAS integrity** — All content flows through `blob_store` via SHA-256 hashes. The `body` column stays forever (readable), `body_hash` is the additive integrity layer.
- **Readable exports** — Markdown and JSON exports must be human-readable and mechanically parseable.
- **Contract authority** — The builder constraint contract lives in the DB (seeded on init) and is served during onboarding. Agents must acknowledge it before meaningful work.

---

## Standard Tool Contract

Every tool in `src/tools/` must follow the `FILE_METADATA + run(arguments)` pattern:

### Required Exports

```python
FILE_METADATA = {
    "tool_name": "journal_example",       # unique name
    "version": "2.0.0",                   # semver
    "entrypoint": "src/tools/journal_example.py",
    "category": "...",                     # bootstrap, write, query, export, introspection, contract, ledger, scaffold, packing, snapshot
    "summary": "One-line description.",
    "mcp_name": "journal_example",        # MCP tool registration name
    "input_schema": { ... },              # JSON Schema for arguments
}

def run(arguments: dict) -> dict:
    # Must return a dict compatible with common.tool_result()
    ...
```

### Required CLI Support

Each tool supports three CLI modes:

```bash
# Show metadata
python src/tools/journal_example.py metadata

# Run with inline JSON
python src/tools/journal_example.py run --input-json '{"key": "value"}'

# Run with JSON file
python src/tools/journal_example.py run --input-file path/to/input.json
```

### Required File Header

Every tool file begins with a docstring block:

```python
"""
FILE: journal_example.py
ROLE: What this tool is.
WHAT IT DOES: What it actually does in detail.
"""
```

### Result Envelope

All tools return this stable JSON shape:

```json
{
  "status": "ok",
  "tool": "journal_example",
  "input": { ... },
  "result": { ... }
}
```

The `result` key contains the tool-specific payload. The `status` key is `"ok"` or `"error"`.

---

## Journal Contract

### Data Model

The journal preserves these concepts explicitly in the `journal_entries` table:

| Field | Type | Purpose |
|-------|------|---------|
| `entry_uid` | TEXT | Unique identifier (e.g., `journal_a1b2c3d4e5f6`) |
| `created_at` | TEXT | ISO 8601 UTC timestamp |
| `updated_at` | TEXT | ISO 8601 UTC timestamp |
| `kind` | TEXT | note, decision, todo, issue, log, feedback, contract, specification, work_log, devlog, guide, design_record |
| `source` | TEXT | user, agent, system, codex, builder |
| `author` | TEXT | Free-text author identifier |
| `status` | TEXT | open, closed, archived, active |
| `importance` | INTEGER | 0 (low) to 10 (critical) |
| `title` | TEXT | Entry title |
| `body` | TEXT | Full body text (always readable) |
| `body_hash` | TEXT | SHA-256 hash pointing to blob_store (additive integrity) |
| `tags` | JSON array | Stored as `tags_json` column |
| `related_path` | TEXT | File path this entry relates to |
| `related_ref` | TEXT | Git ref, URL, or other reference |
| `metadata` | JSON object | Stored as `metadata_json` column |
| `project_id` | TEXT | Empty for self, set by mother app for ingested project entries |

### CAS (Content-Addressed Storage)

Every piece of content (journal body, tool source, template content) is stored exactly once in `blob_store`, keyed by its SHA-256 hash. Other tables reference the hash. This provides:

- **Deduplication** — identical content stored once regardless of how many entries reference it
- **Integrity** — hash mismatch means corruption or tampering
- **Merkle snapshots** — sort all hashes, concatenate, SHA-256 the result = deterministic root

### Action Ledger

The `action_log` table records every action by both humans and agents:

| Field | Purpose |
|-------|---------|
| `actor_type` | `"human"` or `"agent"` |
| `actor_id` | Who did it (e.g., `"claude"`, `"user"`, `"smoke_test_agent"`) |
| `action_type` | What they did (e.g., `"create_entry"`, `"acknowledge_contract"`, `"scaffold"`) |
| `target` | What they acted on |
| `summary` | Human-readable summary |

Both the UI and MCP tools write to this ledger, providing mutual visibility.

### Self-Orientation

The database contains enough manifest data for an agent to orient itself from the DB alone:

- `journal_meta` stores: project_root, initialized_at, schema_version, sqlite_user_version, contract_version, contract_hash, contract_acknowledged_at, contract_acknowledged_by
- `journal_migrations` stores the full migration history
- The package manifest and DB manifest are stored as JSON in `journal_meta`

---

## UI Contract

- The Tkinter UI (`src/ui/app_journal_ui.py`) uses the same `journal_store.py` functions as the MCP tools. There is no separate data path.
- The UI is optional. The package is fully functional headlessly via MCP or CLI.
- Both human actions (via UI) and agent actions (via MCP) appear in the shared action ledger.
- The action log panel in the UI polls every 3 seconds for new actions.

---

## Project-Local Convention

When initialized in a project, the journal creates:

```
project-root/
├── _docs/
│   ├── _journalDB/
│   │   └── app_journal.sqlite3    ← the journal database
│   └── _AppJOURNAL/
│       ├── journal_config.json    ← paths, schema version, hints
│       ├── db_manifest.json       ← tables, entrypoints, conventions
│       └── exports/               ← markdown/JSON exports
```

This convention is fixed. Tools resolve paths from either `project_root` or `db_path`. The `_docs/` folder is the single documentation root — no nested `_docs/` anywhere.
