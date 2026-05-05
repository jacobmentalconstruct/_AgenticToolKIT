# Vendoring

## What This Toolbox Is

`.dev-tools` is a **universal, project-agnostic toolbox** designed to be
vendored into any project for use by human developers and AI agents.

It contains three tiers of vendable assets:

1. **Builder tools** (`src/tools/`) — stay in the toolbox, used to work ON projects
2. **Vendable packages** (`packages/`) — self-contained subprojects installed INTO target projects
3. **Vendable documents** (`templates/`) — project-agnostic templates copied into new projects

## Tier 1: Builder Tools

These never leave the toolbox. They are analysis, patching, audit, and
scaffolding tools that agents invoke to examine or modify a target project.

Entrypoint: `src/mcp_server.py` (MCP) or individual tool CLI.

### Preferred Sidecar Install

The preferred install path is now the **full sidecar**:

```powershell
python install.py
```

Or from the CLI:

```powershell
python src/tools/sidecar_install.py run --input-json "{\"target_project_root\": \"<project_root>\"}"
```

This copies the current shipped `.dev-tools` payload into
`<target>/.dev-tools/` using `release_payload_manifest.json` as the source of
truth.

After install, start inside the target project and use:

```powershell
python .dev-tools/src/tools/project_setup.py run --input-json "{\"action\": \"audit\", \"project_root\": \".\"}"
python .dev-tools/src/tools/project_setup.py run --input-json "{\"action\": \"apply\", \"project_root\": \".\", \"actor_id\": \"builder_agent\"}"
python .dev-tools/src/tools/onboarding_site_check.py run --input-json "{\"toolbox_root\": \".dev-tools\"}"
```

## Tier 2: Vendable Packages

Each package in `packages/` is a complete, portable subproject:

| Package | What Gets Installed |
|---------|---------------------|
| `_app-journal/` | SQLite journal with Tkinter UI and MCP access |
| `_manifold-mcp/` | Evidence bag and hypergraph package |
| `_ollama-prompt-lab/` | Prompt eval and model comparison |

### How to Vend a Package

Copy the entire package folder into the target project:

```bash
cp -r packages/_app-journal <target>/.dev-tools/_app-journal
```

Then verify:

```bash
cd <target>/.dev-tools/_app-journal && python smoke_test.py
```

Every package discovers its own location at runtime via `Path(__file__).resolve()`.
No hardcoded paths. No project-specific assumptions.

## Tier 3: Vendable Documents

The `templates/` folder holds project-agnostic reference documents, boilerplate,
and starter templates. Copy what you need into new projects.

## SQLite State After Setup

- `_docs/_journalDB/app_journal.sqlite3` — the target project's working journal

## Source-Project Commands

Install the full sidecar into a target project:

```powershell
python src/tools/sidecar_install.py run --input-json "{\"target_project_root\": \"<project_root>\"}"
```
