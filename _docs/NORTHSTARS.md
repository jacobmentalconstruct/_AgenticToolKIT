# Northstars

_Last updated: 2026-04-30._

This file records the release-scope northstar for `.dev-tools` and the next
post-release capability horizon.

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

## Container Bridge

The first post-RC bridge is now present in `_v2-pod/`:

- The root prototype stays parked.
- `_v2-pod/` wraps an installed sidecar in a `python:3.11-slim` image.
- The entrypoint installs `.dev-tools` into `/workspace`, runs smoke tests, and
  launches the MCP server over stdio.
- The image builds and runs locally; in-container smoke tests pass.
- Docker and Kubernetes wrapper tools now expose the bridge through structured
  MCP-visible operations.
- Remaining work is environment-side: live `kubectl apply`, `kubectl attach`,
  and registry publication when a cluster/registry target is available.

## Next Northstar: Local Agent Operations

The next meaningful expansion is not broad creative tooling. It is a sys-ops
layer that lets a local or podded agent understand and operate its host/project
environment safely.

The desired shape is a small set of MCP-visible tools with structured outputs,
clear write boundaries, and boring failure modes:

| Capability | Purpose | Likely tool surface |
|---|---|---|
| Host capability probe | Report OS, shell, Python, Git, Docker, kubectl, Node, rg, browser availability, and versions. | `host_capability_probe` — complete |
| Workspace boundary audit | Confirm project root, sidecar location, ignored/generated paths, disk footprint, and unsafe write targets. | `workspace_boundary_audit` — complete |
| Command profile detector | Discover package managers, test commands, launch commands, lockfiles, and likely dev-server entrypoints. | `project_command_profile` — complete |
| Process and port inspector | See running dev servers, occupied ports, command lines, and stale child processes. | `process_port_inspector` — complete |
| Dev server manager | Start, stop, restart, tail logs, and health-check local app servers by declared profile. | `dev_server_manager` — complete |
| Dependency environment check | Verify virtualenv/node_modules/lockfile state without installing blindly. | `dependency_env_check` — complete |
| Docker ops wrapper | Build, run, inspect, and log toolbox/project containers with consistent JSON results. | `docker_ops` — complete |
| Kubernetes ops wrapper | Check context, dry-run/apply manifests, watch readiness, fetch logs, and report attach instructions. | `k8s_ops` — complete |
| Secret and credential audit | Detect obvious committed secrets, local `.env` exposure, and unsafe payload inclusion. | `secret_surface_audit` — complete |
| Runtime artifact cleaner | Identify generated smoke/build/cache artifacts and propose or perform scoped cleanup. | `runtime_artifact_cleaner` — complete |
| Local agent bootstrap | Produce a launch packet for a local agent: root, commands, constraints, available tools, and safe operating envelope. | `local_agent_bootstrap` |

This is the foundation for a local agent using the toolset directly. Once the
agent can inspect the host, run declared workflows, manage servers, and report
state without improvising shell behavior, richer capabilities become safer.

## Later Expansion

These remain valuable, but they should follow the sys-ops layer rather than
compete with it:

- Web browsing/search/open.
- Image generation/editing.
- Local image viewing.
- Automations/recurring tasks.
- Sub-agents/delegation.
- Node REPL/JavaScript execution.
- Full terminal execution parity.

Terminal parity should arrive through declared command profiles and audited
wrappers first, not as an undifferentiated "run anything" surface.
