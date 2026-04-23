# _app-journal Blueprint

_Status: v2.0.0 — verified 2026-03-28 (31/31 smoke tests passing)._

## 1. Purpose

`_app-journal` is the project authority tool for agent-driven development. It is vendored into every project and serves as:

1. **Onboarding gate** — seeds the builder constraint contract, requires acknowledgment before work begins
2. **Operational memory** — SQLite-backed journal for notes, decisions, work logs, design records
3. **Content-addressed store** — blob store with SHA-256 dedup, merkle snapshots for integrity
4. **Human/AI action ledger** — shared visibility into what both humans and agents are doing
5. **Project scaffolder** — lays out standard project layouts from templates stored in the DB
6. **Tool packer** — stores tool source code as blobs, enabling the DB to be the portable package
7. **Mother app hub** — tracks all vendored child projects, ingests returned DBs, manages tool evolution

## 2. Architecture

### Storage: Single SQLite File

Everything lives in one `.sqlite3` file per context:

- **Mother app:** `_docs/_journalDB/app_journal.sqlite3` — owns canonical tools, project registry, all histories
- **Vendored project:** Two files:
  - `.dev-tools/_app-journal/journal.sqlite3` — packed package (tools as blobs)
  - `_docs/_journalDB/app_journal.sqlite3` — project working journal

### Schema v2 Tables

| Table | Role |
|-------|------|
| `journal_meta` | Key-value config (project root, schema version, contract state) |
| `journal_migrations` | Schema migration history |
| `journal_entries` | Journal notes with `body_hash` → blob_store |
| `blob_store` | Content-addressed store — all content lives here once |
| `scaffold_templates` | Project layout recipes → blob_store |
| `packed_tools` | Tool source code → blob_store |
| `action_log` | Shared human/AI action ledger |
| `snapshots` | Point-in-time merkle roots |
| `snapshot_items` | Items in each snapshot → blob_store |
| `project_registry` | Mother app: tracks all vendored child projects |

### CAS (Content-Addressed Storage)

Every piece of content (journal body, tool source, template) is stored once in `blob_store` keyed by SHA-256. Other tables reference the hash. This gives:

- Deduplication (same content stored once regardless of how many entries reference it)
- Integrity (hash mismatch = corruption or tampering)
- Merkle snapshots (sort hashes, hash the concatenation = deterministic root)

### Two User Paths

```
Human (Tkinter UI)                 Agent (MCP tools)
       │                                  │
       ├─ writes to action_log ◄──────────┤
       │   (actor_type="human")           │  (actor_type="agent")
       │                                  │
       └──────► journal_store.py ◄────────┘
                     │
                 SQLite DB
```

Both paths converge on `src/lib/journal_store.py`. The action log provides mutual visibility.

## 3. Lifecycle

### Vend Out
Mother app packs tools into a `.sqlite3`, copies thin shim (common.py + mcp_server.py) to target project.

### Bootstrap
Agent calls `journal_init` → unpacks tools, creates working journal, seeds contract. Calls `journal_acknowledge` → begins work.

### Work
Agent works within builder contract constraints. All actions logged. Human can observe via UI.

### Pack Up
Agent calls `journal_pack` (stores WIP), `journal_snapshot` (merkle checkpoint). Returns `.db` to mother app intake.

### Ingest
Mother app imports journal entries (tagged by project), reviews tool diffs, promotes changes to canonical head.

## 4. Tool Inventory (10 MCP tools)

| Tool | Category | Purpose |
|------|----------|---------|
| `journal_init` | bootstrap | Create DB, seed contract, optionally scaffold |
| `journal_manifest` | introspection | Inspect package + DB manifests |
| `journal_write` | write | Create/update/append journal entries |
| `journal_query` | query | Search and filter entries |
| `journal_export` | export | Export to markdown or JSON |
| `journal_acknowledge` | contract | Acknowledge builder constraint contract |
| `journal_actions` | ledger | Query the shared action log |
| `journal_scaffold` | scaffold | Unpack project layout templates |
| `journal_pack` | packing | Pack/unpack tools to/from DB |
| `journal_snapshot` | snapshot | Create/verify merkle snapshots |

## 5. File Layout

```
_app-journal/
├── README.md, LICENSE.md, requirements.txt
├── setup_env.bat/.sh, run-ui.bat/.sh
├── CONTRACT.md, VENDORING.md
├── tool_manifest.json
├── assets/
├── _docs/
│   ├── BLUEPRINT.md (this file)
│   ├── ARCHITECTURE.md
│   └── _journalDB/, _AppJOURNAL/
├── _parts/ (reference archive)
└── src/
    ├── common.py, mcp_server.py, launch_ui.py, smoke_test.py
    ├── lib/ (journal_store, contract, scaffolds, tool_pack, snapshots, intake)
    ├── tools/ (10 MCP-callable tools)
    └── ui/ (Tkinter UI with action log + HITL)
```
