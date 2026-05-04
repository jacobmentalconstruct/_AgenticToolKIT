# Architecture

_Last updated: 2026-05-04._

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

The local-agent system operations layer is now closed. The next source-shaped
architecture layer is Safe Text Workspace Operations: small MCP-visible file
primitives that let a local agent create and maintain text project assets under
a user-chosen project root without raw filesystem or terminal parity.

## Agent Flow

1. Confirm the project root and write boundary.
2. Confirm `.dev-tools` is installed.
3. Read `toolbox_manifest.json`, `tool_manifest.json`, `_docs/AGENT_GUIDE.md`,
   `_docs/SETUP_DOCTRINE.md`, and `CONTRACT.md`.
4. Run `project_setup audit`.
5. Apply setup only when the project is missing required surfaces.
6. Use tools/packages/templates deliberately.
7. Verify and park meaningful tranches using `_docs/PARKING_WORKFLOW.md`.

## Local-Agent Ops Closure

The sys-ops layer now closes the local-agent northstar in stages:

1. Probe host capabilities, workspace boundaries, command profiles, and
   processes/ports. This stage is implemented by `host_capability_probe`,
   `workspace_boundary_audit`, `project_command_profile`, and
   `process_port_inspector`.
2. Check dependency readiness without installing anything. This stage is
   implemented by `dependency_env_check` and command-profile metadata.
3. Manage only declared dev-server commands with tracked runtime state. This
   stage is implemented by `dev_server_manager`; it starts only
   `project_command_profile` command IDs with `dev` or `run` kind, requires
   explicit confirmation for start/stop/restart, and writes state/logs under
   ignored `.dev-tools/runtime/dev_servers/`.
4. Wrap Docker and Kubernetes workflows with structured status, validation,
   logs, dry-runs, and explicit confirmation for side effects. This stage is
   implemented by `docker_ops` and `k8s_ops`; Docker contexts and Kubernetes
   manifests must resolve under the project root, image tag/push and live
   Kubernetes apply require `confirm: true`, and portable preview/validation
   paths allow agents to plan operations before touching a daemon or cluster.
5. Audit secrets and runtime artifacts before cleanup or packaging. This stage
   is implemented by `secret_surface_audit` and `runtime_artifact_cleaner`;
   secret-like values are redacted in output, cleanup defaults to dry-run, and
   tracked files are protected unless explicitly allowlisted and confirmed.
6. Emit a local-agent bootstrap packet that summarizes the safe operating
   envelope for the current project. This stage is implemented by
   `local_agent_bootstrap`; it aggregates host, workspace, command,
   dependency, journal, tool-manifest, and constraint-doc context, returning
   the packet by default and writing only to ignored runtime exports when
   requested.

## Safe Text Workspace Operations

Tranche 7 is the planned bridge between sys-ops bootstrap and a future
Ollama-backed local agent runtime. The agent can already learn where it is,
which commands exist, and which operational boundaries apply. It still needs a
bounded way to touch text files.

The planned layer should add:

- `text_file_reader` for bounded reads under `project_root`.
- `text_file_writer` for confirmed create/overwrite/append operations.
- `directory_scaffold` for declarative folder/file creation, dry-run first.
- `text_file_validator` for stdlib validation of Python, JSON, TOML, and basic
  text-like surfaces.
- `file_move_guarded` for confirmed move/rename operations with tracked-file
  protection.
- `file_delete_guarded` for quarantine delete under ignored
  `.dev-tools/runtime/trash/` with receipts.

`project_setup` remains the authority for the builder-contract scaffold. Safe
Text Workspace Operations should not reinvent setup doctrine; it should give
the later local agent the basic text/file hand tools needed after setup has
been audited or applied.

## Private Git Workspace Operations

Tranche 8 is queued as the private checkpoint layer for a future sidecar agent.
It should use Git without taking ownership of the user's existing project
repository. The planned shape is a `git_private_workspace` wrapper that stores
an agent-owned gitdir under ignored `.dev-tools/runtime/private_git/` while
using the chosen `project_root` as the worktree.

The tool should expose guarded actions for `status`, `init`, `add`, `commit`,
`branch`, `checkout`, `pull`, and `push`. Mutating actions require
`confirm: true`; commit requires a message; pull/push require an explicitly
configured private remote. The wrapper must exclude `.git/`,
`.dev-tools/runtime/`, generated caches, and risky secret surfaces by default.

This makes Git available as an agent checkpoint mechanism before the local
agent becomes more autonomous, while keeping the operator's primary repository
history out of the default blast radius.

## Local Sidecar Agent Runtime

Tranche 9 is queued as the first real local desktop agent runtime. It should be
Ollama-backed and stdlib-first, using the toolbox's own MCP-visible tools and
CLI contracts as its action surface.

The agent should not plan the scaffold required by the builder contract.
Instead, its loop should be fixed by the sidecar:

1. choose and audit the project root
2. load `local_agent_bootstrap`
3. run `project_setup audit` or `verify`
4. produce a structured task list
5. ask binary or multiple-choice questions for ambiguous or risky decisions
6. call only allowlisted tools with schema-validated JSON arguments
7. verify changed surfaces
8. checkpoint through private Git
9. journal and park

Qwen coder-family models are the preferred planning/JSON generators. Qwen
human-interface models are the preferred conversational response layer. Model
names, endpoint, and timeouts should be configurable, with localhost Ollama as
the first target.
