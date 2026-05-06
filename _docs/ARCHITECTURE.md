# Architecture

_Last updated: 2026-05-06._

`.dev-tools` is a self-contained sidecar toolbox. Its job is to help a human
install the toolbox into a project and help a builder agent orient, set up,
inspect, patch, verify, and park work from inside that project.

## Surfaces

| Surface | Purpose |
|---|---|
| `install.py` and `src/tools/sidecar_install.py` | Manual and CLI sidecar installation into `<target>/.dev-tools`. |
| `chat.bat`, `chat.sh`, `agent_ui.py` | Desktop operator prototype for running the local sidecar agent and testing toolbox tools. |
| `teaching_sandbox_harness` | Ignored sandbox practice/evaluation bridge for local-agent builder-loop teaching runs. |
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
Local Agent Operator UI prototype, Bag of Evidence / Evidence Shelf layer,
Tranche 12 recovery hardening layer, Tranche 13 Teaching Sandbox Harness, and
Tranche 17A Teaching Sandbox control-file protection are implemented. Tranche
17B remains selected as the active trace-tuning slice. The current architecture
now has an Ollama-backed loop that uses the guarded toolbox, checkpoints
through private Git, hydrates from a visible session evidence shelf, records
run traces for recovery/tuning data, can be exercised from a desktop
prototype, can practice in disposable teaching sandboxes, and avoids raw shell
or unrestricted filesystem parity.

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
guarded tools. Tranche 12 closes the first recovery hardening layer over that
floor with run traces, evidence passes, filesystem-claim guardrails,
disposable planning hooks, and richer approval UX.

## Runtime Recovery and Live Model Hardening

Tranche 12 is now closed as the recovery and live-model hardening layer. It
adds `agent_run_trace`, a project-scoped ignored SQLite run/tuning-data store,
model readiness preflight, structured recovery classification in
`local_sidecar_agent`, optional recovery-model advice, heartbeat events, named
operator recovery decisions, disposable planning workspace hooks, and
evidence-backed claim guardrails. The layer hardens live Ollama runs and the
operator UI without expanding the agent's authority.

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
4. present concise retry/status actions and named decisions in `agent_ui.py`
5. archive confirmed failed/recovered turns into `session_evidence_store`
6. write App Journal metadata linking recovery class, evidence IDs, models, and
   timeout settings
7. require final summaries to cite touched paths or evidence IDs for claims
8. write heartbeat events under ignored runtime state when enabled
9. expose disposable planning workspace hooks for future verification loops

Implemented recovery classes include `request_timeout`, `ollama_unreachable`,
`model_missing`, fallback `model_request_failed`, `malformed_tool_call`,
`tool_schema_error`, `tool_runtime_error`, `approval_required`,
`max_rounds_exhausted`, and `claim_guardrail_warning`.

This layer preserves deterministic mocked-model smoke tests and keeps heartbeat
behavior optional. It does not add raw command execution, dependency
installation, or hidden memory.

The popup/chat operator surface now has the narrative cockpit floor over
project LTM, Evidence Shelf, run traces, recovery decisions, and teaching
scorecards. Its job is to help the user and sidecar agent move one builder step
at a time, while each step leaves inspectable evidence that can later become
evaluation or tuning data.

## Teaching Sandbox Harness

Tranche 13 adds the first repeatable practice/evaluation bridge for the local
sidecar agent. The harness lives between the local-agent runtime, Evidence
Shelf, run trace store, App Journal, and future tuning-data work.

`teaching_sandbox_harness` owns ignored runtime state under:

```
.dev-tools/runtime/teaching_sandbox/
```

It creates disposable sandbox projects, copies in a task card plus the builder
constraint contract, runs `local_sidecar_agent` with either mocked or live
Ollama responses, verifies scenario outputs, scores the run, and exports a
sanitized scorecard. The current scenario set is `static_task_tracker`,
`python_notes_cli`, `static_calculator`, `markdown_previewer`,
`task_tracker_filter_update`, `csv_cleaner_cli`, and
`config_validator_cli`.

The teaching harness is not an authority expansion. It adds no raw shell
execution, package installation, broad CLI sandbox, hidden memory, or tracked
project artifact promotion. Its value is that it turns the builder loop into
repeatable practice data:

1. create a bounded sandbox project
2. give the agent a concrete task card
3. route all work through guarded tools
4. verify outputs deterministically
5. archive Evidence Shelf material
6. link App Journal entries and run traces
7. score and export the run for operator review

The operator UI Teaching Lab is a thin human surface over the same tool. It is
useful for exercising the agent loop and selecting the next small builder step
from observed traces and scorecards.

## Local-Agent Training Runway

Tranche 14 parks the first app-builder training layer over the existing runtime. It
does not introduce a new authority surface; it organizes the current harness,
Evidence Shelf, run trace store, App Journal, and operator UI into a repeatable
training/evaluation cycle.

`_docs/TRAINING_RUNWAY.md` is the committed operator manual for this layer. It
defines the curriculum, baseline protocol, score rubric, failure taxonomy,
trace-review checklist, and the ignored run-index/export convention that uses
the existing Teaching Sandbox SQLite store and export directory.

The data flow is:

1. `teaching_sandbox_harness` creates or runs a bounded scenario.
2. `local_sidecar_agent` acts through allowlisted guarded tools.
3. `session_evidence_store` archives visible session evidence when confirmed.
4. `agent_run_trace` records prompts, models, tool calls, touched paths,
   recovery classes, Evidence IDs, and journal links.
5. The harness verifies and scores the run.
6. The operator reviews the scorecard and promotes lessons into task cards,
   prompt/contract constraints, or future scenario changes.
7. App Journal and `_docs/DEV_LOG.md` preserve the durable project-level
   training story.

The first baseline set confirms the architecture split. Mocked runs prove the
harness, verification, scoring, export, trace, and journal path. Live runs
surface model-loop teaching gaps without expanding authority; the first
repeatable gap is sandbox contract resolution before app scaffold.

Tranches 15-18 continue this architecture by adding builder-doctrine task
cards, broader small-app scenarios, trace-driven loop tuning, and unseen
graduation runs. Model weight fine-tuning is deliberately deferred until the
project has clean, sanitized, high-signal traces worth tuning on.

Tranche 15 adds the parked task-card doctrine layer. The harness now returns
project-birth template metadata, required/optional/forbidden scenario steps,
and sandbox-local contract rules in scenario plans. Created sandboxes receive a
complete `_docs/builder_constraint_contract.md` so the live model does not need
to chase parent/root contract paths. The local agent also classifies array item
schema mistakes before tool execution and tolerates a common `[/tool_call]`
closing tag without treating otherwise valid JSON as unusable.

Tranche 16 expands the curriculum layer without changing the authority model.
The harness now includes five additional deterministic baselines across static
web apps, stdlib Python CLIs, and an edit-after-feedback feature-addition
scenario. Each new scenario has mocked fixture payloads and verifier checks so
trace tuning can compare broader app-building behavior before graduation runs.

Tranche 17A adds the first trace-tuning hardening lesson. The Teaching Sandbox
control files `_docs/TASK_CARD.md` and
`_docs/builder_constraint_contract.md` are inside the sandbox root but not
safe-to-write. The harness now injects those paths into the sidecar as
protected paths; `directory_scaffold` and `text_file_writer` reject attempted
writes with `control_file_tamper`, and scorecards expose that safety signal.

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
