# Architecture

_Last updated: 2026-04-30._

`.dev-tools` is a self-contained sidecar toolbox. Its job is to help a human
install the toolbox into a project and help a builder agent orient, set up,
inspect, patch, verify, and park work from inside that project.

## Surfaces

| Surface | Purpose |
|---|---|
| `install.py` and `src/tools/sidecar_install.py` | Manual and CLI sidecar installation into `<target>/.dev-tools`. |
| `onboarding/` and `START_HERE.html` | Offline human onboarding microsite. |
| `src/tools/` | Builder tools that stay inside the toolbox and operate on projects. |
| `src/mcp_server.py` | MCP stdio exposure for builder tools. |
| `packages/` | Vendable subprojects copied into target projects when needed. |
| `templates/` | Vendable document templates and starter governance material. |
| `_v2-pod/` | Isolated Kubernetes/container bridge around an installed sidecar. |
| `_docs/` | Doctrine, continuity, release state, and workflow memory. |
| `release_payload_manifest.json` | Source of truth for what the sidecar installer copies. |

## Current Boundary

The active prototype is the full sidecar install path plus a post-RC container
bridge in `_v2-pod/`. Legacy packed-authority and old BuilderSET reference
surfaces are not part of the current architecture.

The toolbox should remain project-agnostic and should not depend on sibling
folders, old project roots, generated caches, or hidden runtime state.

The next source-shaped architecture layer is local-agent system operations:
small MCP-visible wrappers that expose host/project operational truth without
giving an agent raw unrestricted terminal parity. These tools should prefer
structured read-only inspection first, then guarded mutations through declared
command profiles and explicit confirmations.

## Agent Flow

1. Confirm the project root and write boundary.
2. Confirm `.dev-tools` is installed.
3. Read `toolbox_manifest.json`, `tool_manifest.json`, `_docs/AGENT_GUIDE.md`,
   `_docs/SETUP_DOCTRINE.md`, and `CONTRACT.md`.
4. Run `project_setup audit`.
5. Apply setup only when the project is missing required surfaces.
6. Use tools/packages/templates deliberately.
7. Verify and park meaningful tranches using `_docs/PARKING_WORKFLOW.md`.

## Local-Agent Ops Direction

The planned sys-ops layer closes the remaining local-agent northstar in stages:

1. Probe host capabilities, workspace boundaries, command profiles, and
   processes/ports. This stage is implemented by `host_capability_probe`,
   `workspace_boundary_audit`, `project_command_profile`, and
   `process_port_inspector`.
2. Check dependency readiness without installing anything.
3. Manage only declared dev-server commands with tracked runtime state.
4. Wrap Docker and Kubernetes workflows with structured status, validation,
   logs, dry-runs, and explicit confirmation for side effects.
5. Audit secrets and runtime artifacts before cleanup or packaging.
6. Emit a local-agent bootstrap packet that summarizes the safe operating
   envelope for the current project.
