# Architecture

_Last updated: 2026-05-05._

`.dev-tools` is a self-contained sidecar toolbox. Its job is to help a human
install the toolbox into a project and help a builder agent orient, set up,
inspect, patch, verify, and park work from inside that project.

## Surfaces

| Surface | Purpose |
|---|---|
| `install.py` and `src/tools/sidecar_install.py` | Manual and CLI sidecar installation into `<target>/.dev-tools`. |
| `chat.bat`, `chat.sh`, `agent_ui.py` | Desktop operator prototype for running the local sidecar agent and testing toolbox tools. |
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

The local-agent system operations layer, Safe Text Workspace Operations layer,
Private Git Workspace Operations layer, Local Sidecar Agent Runtime safe floor,
Local Agent Operator UI prototype, Bag of Evidence / Evidence Shelf layer, and
Tranche 12 run-trace foundation are implemented. The current architecture now
has an Ollama-backed loop that uses the guarded toolbox, checkpoints through
private Git, hydrates from a visible session evidence shelf, records run traces
for recovery/tuning data, can be exercised from a desktop prototype, and avoids
raw shell or unrestricted filesystem parity.

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

Tranche 7 implements the bridge between sys-ops bootstrap and a future
Ollama-backed local agent runtime. The agent can already learn where it is,
which commands exist, and which operational boundaries apply; it now also has
a bounded way to touch text files.

The implemented layer adds:

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

Tranche 8 implements the private checkpoint layer for a future sidecar agent. It
uses Git without taking ownership of the user's existing project repository.
The implemented shape is a `git_private_workspace` wrapper that stores an
agent-owned gitdir under ignored `.dev-tools/runtime/private_git/` while using
the chosen `project_root` as the worktree.

The tool exposes guarded actions for `status`, `init`, `add`, `commit`,
`branch`, `checkout`, `pull`, and `push`. Mutating actions require
`confirm: true`; commit requires a message; pull/push require an explicitly
configured private remote. The wrapper must exclude `.git/`,
`.dev-tools/runtime/`, generated caches, and risky secret surfaces by default,
and it blocks `origin` unless explicitly allowed.

This makes Git available as an agent checkpoint mechanism before the local
agent becomes more autonomous, while keeping the operator's primary repository
history out of the default blast radius.

## Local Sidecar Agent Runtime

Tranche 9 implements the first real local desktop agent runtime as a safe
floor. It is Ollama-backed and stdlib-first, using the toolbox's own
MCP-visible tools and CLI contracts as its action surface.

The agent should not plan the scaffold required by the builder contract.
Instead, its loop is fixed by the sidecar:

1. choose and audit the project root
2. load `local_agent_bootstrap`
3. run `project_setup audit` or `verify`
4. get model output through the configured Ollama role or a mock response
5. parse fenced `tool_call` JSON blocks
6. call only allowlisted tools with schema-validated JSON arguments
7. stop with `approval_required` before unconfirmed mutations
8. verify touched file surfaces
9. archive sliding-window overflow into the Bag of Evidence when confirmed
10. checkpoint through private Git when confirmed
11. journal and park runtime state under `.dev-tools/runtime/local_agent/`

Qwen coder-family models are the preferred planning/JSON generators. Qwen
human-interface models are the preferred conversational response layer. Model
names, endpoint, and timeouts should be configurable, with localhost Ollama as
the first target.

The safe floor deliberately does not add raw CLI parity, dependency
installation, or a duplicate file/VCS stack. It routes through the existing
guarded tools. Future hardening should add recovery-pattern detection, evidence
passes, filesystem-claim guardrails, disposable run workspaces, and richer
approval UX.

## Runtime Recovery and Live Model Hardening

Tranche 12 is the active architecture step. Its implemented slices add
`agent_run_trace`, a project-scoped ignored SQLite run/tuning-data store, model
readiness preflight, initial claim guardrail metadata, and structured recovery
classification in `local_sidecar_agent`. Remaining work should harden the
Ollama-backed runtime and operator UI around longer live-model runs and richer
operator decisions without expanding the agent's authority.

`agent_run_trace` owns this ignored runtime path:

```
.dev-tools/runtime/local_agent/run_trace/run_trace.sqlite3
```

The run trace store is not durable project LTM and not hidden memory. It is
local tuning/eval evidence: prompts, selected models, allowed tools, tool
calls/results, approvals, touched paths, recovery classes, Evidence IDs,
verification signals, linked journal entries, and operator outcomes.

The observed floor issue is a raw timeout envelope from a live Agent Console
run. Architecturally, that belongs to a recovery layer between model transport,
tool execution, Evidence Shelf parking, and operator UX:

1. preflight selected models before a run
2. classify transport/model/tool/approval failures into stable recovery classes
3. return structured recovery status in the normal JSON envelope
4. present concise retry/status actions in `agent_ui.py`
5. archive confirmed failed/recovered turns into `session_evidence_store`
6. write App Journal metadata linking recovery class, evidence IDs, models, and
   timeout settings
7. require final summaries to cite touched paths or evidence IDs for claims

Implemented recovery classes include `request_timeout`, `ollama_unreachable`,
`model_missing`, fallback `model_request_failed`, `malformed_tool_call`,
`tool_schema_error`, `tool_runtime_error`, `approval_required`,
`max_rounds_exhausted`, and `claim_guardrail_warning`.

This layer should preserve deterministic mocked-model smoke tests and keep
streaming or heartbeat behavior optional. It should not add raw command
execution, dependency installation, or hidden memory.

The popup/chat operator surface should become the narrative cockpit over
project LTM, Evidence Shelf, and run traces. Its job is to help the user and
sidecar agent move one builder step at a time, while each step leaves
inspectable evidence that can later become evaluation or tuning data.

## Local Agent Operator UI

Tranche 10 adds the first human-facing operator prototype for the local sidecar
agent. It is deliberately a UI layer, not a new authority layer.

The UI has two surfaces:

- Agent Console: project picker, Ollama base URL, planner and response model
  dropdowns, prompt input, allowed-tool checklist, confirmation toggles, status,
  run, and sanitized output.
- Tool Lab: manifest-backed tool picker, metadata/schema display, editable JSON
  input, side-effect confirmation gate, and sanitized result pane.

The implementation calls existing `run(arguments)` functions in process and
loads tool metadata from `tool_manifest.json`. It does not introduce arbitrary
shell execution, a web server, or a parallel MCP surface. Public display paths
are rendered as relative paths or placeholders such as `<project_root>` and
`<toolbox_root>`; committed docs should follow the same rule, with
`LICENSE.md` as the copyright identity exception.

The friendliest human entrypoints are `chat.bat` on Windows and `chat.sh` on
Linux/macOS. `agent_ui.py` remains the direct Python launcher and supports
`--self-test` for headless verification.

## Bag of Evidence and Evidence Shelf

Tranche 11 implements the session coherence layer for the local sidecar agent.
It sits between the active prompt window and durable project memory.

`session_evidence_store` owns the shared SQLite path under ignored runtime
state:

```
.dev-tools/runtime/local_agent/evidence/evidence.sqlite3
```

The SQLite shape is explicit: evidence items carry stable IDs, session IDs,
sequence ranges, kind/source metadata, summaries, tags, paths, tools,
importance, timestamps, and a SHA-256 reference to verbatim body storage.
Shelves store the rolling summary, open loops, decisions, and last archived
sequence for a session.

The architecture intentionally separates memory layers:

- live context: the current prompt and last `window_turns` turns
- Bag of Evidence: ignored session STM archive with searchable summaries and
  retrievable verbatim bodies
- Evidence Shelf: compact session summary and item index injected into agent
  context
- App Journal: durable project LTM for decisions, tranche outcomes, and
  important handoff records

`local_sidecar_agent` now accepts `session_id`, `window_turns`,
`use_evidence_shelf`, and `confirm_evidence`. It loads the shelf before model
work, archives overflow turns after a run when confirmed, and records archive
status into the normal journal entry metadata. `local_agent_bootstrap` can add
the shelf to launch packets, and the operator UI has an Evidence Shelf tab for
init, shelf, search, get, and export.
