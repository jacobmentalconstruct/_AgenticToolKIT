# Northstars

_Last updated: 2026-04-29._

This file records the release-scope northstar for `.dev-tools`.

## Current Truth

The prototype northstar is now satisfied by a self-contained sidecar toolbox:

- A human can install `.dev-tools` into a project with `install.py` or
  `sidecar_install`.
- A human can onboard through the offline microsite without old project folders.
- A builder agent can orient from `toolbox_manifest.json`, `tool_manifest.json`,
  `_docs/AGENT_GUIDE.md`, `_docs/SETUP_DOCTRINE.md`, and `CONTRACT.md`.
- A target project can be audited, scaffolded, and verified with
  `project_setup`.
- The release payload is controlled by `release_payload_manifest.json`.
- Active tools, packages, templates, docs, and onboarding assets ship together.
- Old BuilderSET authority/reference material is no longer part of the current
  product shape.

## Release-Scope Capability Closure

| Capability direction | Prototype status | Current surface |
|---|---:|---|
| Sidecar install | complete | `install.py`, `sidecar_install` |
| Agent first-contact setup | complete | `_docs/AGENT_GUIDE.md`, `_docs/SETUP_DOCTRINE.md`, `project_setup` |
| Builder contract alignment | complete | `CONTRACT.md`, `_constraint-registry` |
| Human onboarding | complete | `START_HERE.html`, `onboarding/`, `_docs/EXPERIENTIAL_WORKFLOW.md` |
| File patching parity | satisfied | `tokenizing_patcher` |
| Repo search / Windows fallback | satisfied | `repo_search` |
| Local inspection and analysis | satisfied | `file_tree_snapshot`, `import_graph_mapper`, `dead_code_finder`, related analysis tools |
| Planning and parking | satisfied | `_docs/TODO.md`, `_docs/PARKING_WORKFLOW.md`, `_docs/WE_ARE_HERE_NOW.md` |
| MCP-visible tool surface | satisfied | `src/mcp_server.py`, `tool_manifest.json` |
| Vendable building material | satisfied | `packages/`, `templates/` |

## Deferred Expansion

These capabilities are valuable, but they are not required for this prototype to
be release-ready:

- Web browsing/search/open.
- Image generation/editing.
- Local image viewing.
- Automations/recurring tasks.
- Sub-agents/delegation.
- Node REPL/JavaScript execution.
- Full terminal execution parity.

They belong in later expansion tranches after the release candidate is clean.

## Release Gate

The remaining northstar is not another feature. It is cleanliness:

- Remove old reference/provenance material from the active repo shape.
- Verify the sidecar installs from the cleaned source only.
- Keep docs, manifests, microsite, and smoke tests aligned to the final shape.
