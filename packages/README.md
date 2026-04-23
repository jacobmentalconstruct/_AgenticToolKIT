# Vendable Packages

Self-contained subprojects that get **installed into** target projects.

Unlike builder tools (which stay in the toolbox and operate ON projects), these packages are copied wholesale into a target project's workspace where they run independently.

## Current Packages

| Package | Purpose |
|---------|---------|
| `_app-journal/` | SQLite-backed shared journal for notes, dev logs, decisions, and human-agent activity |
| `_manifold-mcp/` | Reversible text-evidence-hypergraph package built around evidence bags |
| `_ollama-prompt-lab/` | Local prompt evaluation and Ollama model comparison |
| `_constraint-registry/` | Atomic constraint registry for surgical injection of BCC rules into agent prompts |

## Package Contract

Every vendable package includes:

- `README.md` — what it does and how to use it
- `CONTRACT.md` — mechanical contract for CLI and MCP
- `tool_manifest.json` — machine-readable tool index
- `mcp_server.py` — MCP stdio entrypoint
- `smoke_test.py` — self-test that proves the package works
- `common.py` — shared CLI runtime

## How to Vend

1. Copy the entire package folder into the target project (e.g. `<project>/.dev-tools/_app-journal/`)
2. Run `python smoke_test.py` from inside the package to verify
3. Connect the MCP server or use the CLI tools directly

Each package is fully path-agnostic and discovers its own location at runtime.
