# WE_ARE_HERE_NOW

_Fast pickup note for `.dev-tools`. Update this at meaningful milestones._

## Last updated

- 2026-05-06 (Tranche 16 parked; Tranche 17 next)

## Fresh-thread start

- Read `README.md` for the main architecture overview.
- Read `_docs/SETUP_DOCTRINE.md` if the task is a fresh project birth or scaffold phase.
- Read `_docs/TODO.md` for active backlog and next tranche shaping.
- Read `_docs/PARKING_WORKFLOW.md` for the expected park-and-handoff discipline.

## Current footing

- Project root:
  - `.dev-tools`
- Current phase or tranche:
  - root prototype parked (strangler complete); `_v2-pod/` carries the
    Kubernetes-wrapped bridge; local-agent sys-ops tooling is closed through
    Tranche 6; Tranche 7 Safe Text Workspace Operations is implemented;
    Tranche 8 Private Git Workspace Operations is implemented; Tranche 9
    Local Sidecar Agent Runtime is implemented as a safe floor; Tranche 10
    Local Agent Operator UI prototype is implemented; Tranche 11 Bag of
    Evidence and Evidence Shelf are implemented; Tranche 12 Local Agent
    Runtime Recovery and Live Model Hardening is now closed with run traces,
    model readiness preflight, broader recovery classification, heartbeat
    events, optional recovery-model advice, named operator decisions,
    one-click retry, planning workspace hooks, and evidence-backed claim
    guardrails; Tranche 13 Teaching Sandbox Harness is implemented as a
    side-support bridge for realistic agent practice/eval data; Tranche 14
    Training Curriculum And Baseline Runs is parked and now has
    `_docs/TRAINING_RUNWAY.md` as its curriculum, baseline protocol, rubric,
    taxonomy, trace-review checklist, ignored run-index/export convention, and
    first mocked/live baseline evidence; Tranche 15 Builder Doctrine Task Cards
    is parked with explicit project-birth task-card doctrine; Tranche 16
    Curriculum Scenario Expansion is parked with five additional deterministic
    practice scenarios; Tranche 17 Trace Review And Loop Tuning is the next
    source tranche
- Current runtime truth:
  - root toolbox is now a single-purpose installer (`install.py` GUI / `run.bat` /
    `run.sh`) plus the agent-facing MCP, smoke-test, and builder-tool surfaces
  - the journal UI lives only inside the vendable `_app-journal` package; the
    toolbox root no longer pretends to be the original journal package
  - sidecar install, setup orchestration, onboarding-site verification, and the
    local agent operator UI are live human/operator surfaces; the root smoke
    suite is current at the Tranche 13 teaching sandbox support slice
  - Tranche 14-16 baseline artifacts use the existing ignored Teaching Sandbox
    store and export path under `.dev-tools/runtime/teaching_sandbox/`
  - `.gitignore` now covers `.claude/`, `.env*`, `*.key`/`*.pem`, credentials,
    logs, and runtime journal state
- Current collaboration truth:
  - the prototype is parkable: human installs via the GUI, agent takes over
    inside the target project from `project_setup` onward; `local_sidecar_agent`
    now provides the first guarded local agent loop; `teaching_sandbox_harness`
    lets that loop practice on ignored sandbox apps; the popup/chat operator
    surface now has the narrative cockpit floor over project LTM, Evidence
    Shelf, run traces, recovery decisions, and scorecards

## What works right now

- Three-surface sidecar architecture is established.
- Vendable packages are present and recently drift-cleaned.
- Offline onboarding microsite is in place.
- Backlog and northstars now exist as explicit surfaces.
- Full sidecar install path exists via `install.py` and `sidecar_install`.
- Project setup can now be audited, applied, and verified with `project_setup`.
- Microsite integrity can now be checked with `onboarding_site_check`.
- The temporary-project install/apply/verify/microsite trial is now passing.
- The release payload manifest now lists only active release-candidate surfaces.
- `repo_search` now gives agents a Windows-safe search surface with an `rg`
  fast path and native fallback.
- `_v2-pod/` contains the container bridge: Dockerfile, entrypoint, deployment
  manifest, and README. The image build/run path has been recorded as verified
  in `DEV_LOG.md`.
- Tranche 1 sys-ops tools are active: `host_capability_probe`,
  `workspace_boundary_audit`, `project_command_profile`, and
  `process_port_inspector`.
- Tranche 2 added `dependency_env_check` and enriched command profiles with
  stable metadata for later guarded operations.
- Tranche 3 added `dev_server_manager`: it starts only profiled `dev`/`run`
  command IDs with confirmation, records runtime state under ignored
  `.dev-tools/runtime/dev_servers/`, tails logs, reports status, checks health,
  and stops registered processes.
- Tranche 4 added `docker_ops` and `k8s_ops`: Docker contexts and Kubernetes
  manifests are scoped under the project root, Docker tag/push and Kubernetes
  apply require confirmation, `_v2-pod/` can be previewed/validated through the
  tools, and MCP now lists 35 tools.
- Tranche 5 added `secret_surface_audit` and `runtime_artifact_cleaner`: secret
  findings are redacted, risky env files are flagged, cleanup defaults to
  dry-run, tracked files are protected, and MCP now lists 37 tools.
- Tranche 6 added `local_agent_bootstrap`: it aggregates host, workspace,
  command, dependency, journal, tool-manifest, and constraint context into a
  JSON or Markdown launch packet, returning by default and writing only to
  ignored runtime exports when requested. MCP now lists 38 tools.
- Tranche 7 added Safe Text Workspace Operations: `text_file_reader`,
  `text_file_writer`, `directory_scaffold`, `text_file_validator`,
  `file_move_guarded`, and `file_delete_guarded`. MCP now lists 44 tools.
- Tranche 8 added Private Git Workspace Operations: `git_private_workspace`, a
  sidecar-owned Git checkpoint layer using ignored runtime state instead of the
  user's main `.git` by default. MCP now lists 45 tools.
- Tranche 9 added `local_sidecar_agent`: an Ollama-backed agent floor that acts
  only through allowlisted guarded toolbox tools, stops for approval before
  unconfirmed mutations, writes ignored runtime state, validates touched files,
  journals turns, and checkpoints through private Git. MCP now lists 46 tools.
- Tranche 10 added `agent_ui.py`, a stdlib Tkinter operator prototype with an
  Agent Console and Tool Lab. It lets the human pick Ollama models from
  dropdowns, run the local sidecar agent, test manifest-listed tools, and view
  privacy-sanitized output without adding raw terminal parity or a new
  MCP-visible tool.
- Tranche 11 added `session_evidence_store`, a project-scoped ignored SQLite
  Bag of Evidence plus Evidence Shelf. The sidecar agent now hydrates from a
  visible shelf, archives sliding-window overflow when confirmed, records
  evidence archive status into normal journal metadata, and exposes shelf,
  search, get, and export through the operator UI. MCP now lists 47 tools.
- Tranche 12 has started with `agent_run_trace`, a project-scoped ignored
  SQLite run/tuning-data spine. The sidecar agent now records successful,
  approval-stopped, and failed runs, links recovery metadata to Evidence IDs
  and App Journal entries, and classifies initial model-transport failures such
  as `request_timeout`, `ollama_unreachable`, and `model_missing`.
- The second Tranche 12 slice added live model readiness preflight, early
  recovery stops for unreachable Ollama or missing selected models, structured
  recovery for malformed tool calls, schema errors, runtime tool failures,
  approval stops, and max-round exhaustion, first-pass UI recovery status text,
  and initial claim guardrail metadata. MCP still lists 48 tools.
- Tranche 13 added `teaching_sandbox_harness` and a Teaching Lab tab to the
  operator UI. The harness creates ignored runtime sandbox projects, copies in
  task cards and the builder constraint contract, runs the local sidecar agent
  through guarded static-task-tracker or Python-notes-CLI scenarios, verifies
  deterministic checks, records trace/evidence/journal links, scores the run,
  and exports scorecards. MCP now lists 49 tools.
- Tranche 12 is now closed after its final hardening slice. `local_sidecar_agent`
  attaches named recovery decisions, optional recovery-model advice, heartbeat
  events, disposable planning workspace metadata, and stronger touched-path /
  Evidence ID claim guardrails. `agent_ui.py` exposes one-click retry with a
  longer timeout and recovery decision controls while keeping model dropdowns
  and no-model disabled-run behavior. The root smoke suite is current at 138
  passing checks with MCP still listing 49 tools.
- Tranche 14 is now parked as the local-agent app-builder training
  runway. `_docs/TRAINING_RUNWAY.md` defines the curriculum, baseline
  protocol, score rubric, failure taxonomy, trace-review checklist, and ignored
  runtime run-index/export convention. Mocked baselines passed both initial
  scenarios; live Ollama baselines were reachable but failed on the same
  sandbox contract-resolution issue, trying to read `CONTRACT.md` inside the
  disposable sandbox after reading the copied pointer doc.
- Tranche 15 is parked and has added `_docs/BUILDER_DOCTRINE_TASK_CARDS.md`,
  project-birth task-card metadata, required/optional/forbidden scenario
  steps, sandbox-local contract rules, scaffold argument examples, tool-call
  format rules, and schema guardrails for array item types and common tool-call
  closing tags. Live reruns now reach real artifact creation instead of failing
  before scaffold. The root smoke suite is current at 142 passing checks with
  MCP still listing 49 tools.
- Tranche 16 is parked and expands the Teaching Sandbox curriculum from two
  initial scenarios to seven total scenarios. New deterministic tasks are
  `static_calculator`, `markdown_previewer`, `task_tracker_filter_update`,
  `csv_cleaner_cli`, and `config_validator_cli`; each has task-card metadata,
  mocked fixture payloads, deterministic verification, and smoke coverage.

## Current bottleneck

- No internal root bottleneck for first-use local-agent testing. Remaining
  container work is operational: live-cluster `kubectl apply` / `kubectl
  attach`, plus registry publication.
- The active source-shaped bottleneck has moved to Tranche 17 trace tuning: the
  curriculum is broader, and the next step is to compare scorecards/traces
  across scenarios, then promote recurring lessons into prompt, task-card,
  schema, or recovery improvements.

## Next best move

- Begin Tranche 17 Trace Review And Loop Tuning by comparing the Tranche 15
  live partial passes and the Tranche 16 expanded mocked baselines, then choose
  the smallest prompt/task-card/schema change that should improve live runs
  without broadening authority.

## Current warnings

- The root prototype is parked; do not edit root surfaces casually while
  the v2 tranche is open. Treat root as frozen reference for this tranche.
- `_v2-pod/.dev-tools/` is gitignored (it is just an installed sidecar);
  the wrapper code we write inside `_v2-pod/` IS tracked.
- Deferred creative/browser/automation capabilities should wait until the
  sys-ops layer gives a local agent a reliable operating envelope.
- Do not let Safe Text Workspace Operations replace `project_setup`; setup doctrine remains the
  authority for required project scaffold and builder-contract surfaces.
- Delete should mean quarantine by default, with receipts under ignored runtime
  state, not permanent removal.
- Private Git should not mutate the user's main `.git` by default.
- The sidecar agent should not gain raw shell or unrestricted filesystem parity;
  it should use the guarded tool suite and human confirmation gates.
- Treat the Bag of Evidence as session STM archive. The App Journal remains
  durable project LTM, and important evidence should be promoted into journal
  entries deliberately rather than copied wholesale.
- Tranche 12 should not add raw terminal parity, dependency installation, or
  unrestricted model authority. Recovery should route through existing tool
  contracts, Evidence Shelf state, and explicit operator choices.
- Teaching sandboxes are disposable ignored runtime projects. Do not promote
  sandbox artifacts into tracked source unless an operator explicitly asks for
  that promotion.
- Committed docs and onboarding surfaces should use relative paths or
  placeholders such as `<project_root>` and `<toolbox_root>`. `LICENSE.md` is
  the intentional exception for copyright holder identity.

## Read in this order if resuming cold

1. `README.md`
2. `_docs/WE_ARE_HERE_NOW.md`
3. `_docs/TODO.md`
4. `_docs/PARKING_WORKFLOW.md`
5. `_docs/TRAINING_RUNWAY.md`
6. `_docs/BUILDER_DOCTRINE_TASK_CARDS.md`
7. `_docs/NORTHSTARS.md`
8. `_docs/DEV_LOG.md`

## Known truth about the docs

- `README.md` is the architecture front door.
- `SETUP_DOCTRINE.md` is the setup-first doctrine for fresh project creation.
- `WE_ARE_HERE_NOW.md` is the fast state surface.
- `TODO.md` is the active backlog and next-tranche surface.
- `PARKING_WORKFLOW.md` is the tranche park/handoff regimen.
- `TRAINING_RUNWAY.md` is the Tranche 14 training/evaluation manual.
- `BUILDER_DOCTRINE_TASK_CARDS.md` is the Tranche 15 task-card doctrine.
- `NORTHSTARS.md` is the longer-range capability direction surface.
