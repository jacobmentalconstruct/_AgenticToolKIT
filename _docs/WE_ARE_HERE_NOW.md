# WE_ARE_HERE_NOW

_Fast pickup note for `.dev-tools`. Update this at meaningful milestones._

## Last updated

- 2026-05-07 (Tranche 17B Python CLI live passes achieved)

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
    practice scenarios; Tranche 17A Teaching Sandbox Control-File Integrity is
    parked as the first trace-tuning hardening slice; Tranche 17B Trace Review
    And Loop Tuning has started with an explicit training procedure and a
    read-only run comparison surface, a narrow parser repair for raw control
    characters inside JSON string content, and stronger task-card guidance for
    quote-heavy generated content plus mandatory static-web APIs. The Teaching
    Sandbox model-facing allowed set is now narrowed to file tools while the
    harness owns trace/evidence/journal capture
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
- Tranche 17A is parked and code-protects Teaching Sandbox control files.
  The harness injects `_docs/TASK_CARD.md` and
  `_docs/builder_constraint_contract.md` as protected paths into the local
  sidecar, `directory_scaffold` and `text_file_writer` reject writes to those
  paths with `control_file_tamper`, and scorecards expose the named safety
  signal.
- Tranche 17B has started. `_docs/TRAINING_RUNWAY.md` now describes how to
  perform a training slice end to end, and `teaching_sandbox_harness
  compare_runs` summarizes selected or recent runs by score, pass/fail state,
  failed checks, recovery classes, safety signals, trace IDs, Evidence IDs,
  App Journal UID, and next review steps.
- The first Tranche 17B comparison review found a recurring
  `malformed_tool_call` shape in `TS000015`, `TS000019`, and `TS000020`: the
  model put literal multiline file content inside JSON string values. The
  sidecar now repairs raw newline, carriage-return, and tab characters inside
  JSON strings before retrying parse, while task cards still teach escaped
  `\n` content as the desired form.
- Fresh live runs `TS000026`, `TS000027`, and `TS000028` exposed the next small
  lesson. Quote-heavy Python/README content still needs explicit JSON escaping
  discipline, and static task cards need to state that `localStorage` and
  `addEventListener` are required in the initial implementation, not future
  suggestions.
- Follow-up live runs reached passing Python artifacts but exposed post-success
  overreach into evidence/trace/journal tools. The sandbox now exposes only
  scaffold/read/write file-work tools to the model; deterministic validation,
  trace, evidence, and App Journal records remain automatic harness outputs.
- The latest closeout evidence has clean live Python CLI passes:
  `TS000038` (`config_validator_cli`) and `TS000042` (`csv_cleaner_cli`) both
  scored 93 with verification 100, agent status `ok`, and no safety signals.
  `TS000041` was an interrupted placeholder run and should be ignored for
  training conclusions.
- The next full live sweep on 2026-05-07 produced clean passes for
  `TS000047` (`csv_cleaner_cli`) and `TS000049` (`config_validator_cli`), plus
  four teachable failures/partials:
  `TS000043` missed static task lifecycle wiring, `TS000044` exposed invalid
  `\'` JSON escapes in JavaScript content, `TS000045` passed artifacts but
  errored on post-success readback, `TS000046` missed filter controls, and
  `TS000048` exposed escaped JSON object keys mid-scaffold.
- After the invalid-escape repair and task-card guidance update, reruns showed:
  `TS000052` (`python_notes_cli`) and `TS000053` (`markdown_previewer`) reached
  clean 93/100 passes; `TS000050` (`static_calculator`) recovered from parser
  error to artifact-producing partial and now re-scores at 86/90 after fairer
  symbol-operation verification; `TS000051`
  (`task_tracker_filter_update`) gained visible filter controls but still used
  `.onclick` and missed delete lifecycle.
- 17C reruns showed the literal event guidance helped the task trackers but was
  still too abstract for calculator output:
  `TS000054` remained partial because of inline `onclick`; `TS000055` used
  `addEventListener` but omitted edit/delete lifecycle; `TS000056` improved
  filter/event behavior but omitted delete lifecycle and tried to write a final
  report through `text_file_writer`.
- After concrete DOM-event and task-lifecycle recipes, the final 17C live
  checks are clean: `TS000058` (`static_calculator`), `TS000057`
  (`static_task_tracker`), and `TS000060` (`task_tracker_filter_update`) each
  scored 93 with verification 100 and agent status `ok`.
- Tranche 17D added `teaching_sandbox_harness export_review`, a privacy-bounded
  Markdown/JSON reviewer packet for selected comparison runs. It records
  sanitized scorecard summaries, failed checks, recovery classes, safety
  signals, aggregate counts, and reviewer checklist steps without raw model
  transcripts, sandbox file contents, or absolute local paths.
- Tranche 17E has started after the graduation-risk review. The key new lesson
  is that a successful run can still be harness-assisted if tool-call JSON was
  silently repaired. `local_sidecar_agent` now records successful parser repair
  strategies as `parse_repair_signals`, and Teaching Sandbox scorecards,
  comparisons, and reviewer exports surface those signals for pre-graduation
  review.
- Tranche 17F adds operator visibility while Teaching Sandbox runs are in
  progress. The harness now writes sanitized phase events under ignored runtime
  state, exposes read-only `latest_status` and `tail_events` actions, and the
  Teaching Lab UI can poll latest status during `run_agent` and `run_scenario`.
- Future tranche docs and App Journal entries should include a compact code
  reference manifest with approximate file names and line ranges for meaningful
  source changes.

## Current bottleneck

- No internal root bottleneck for first-use local-agent testing. Remaining
  container work is operational: live-cluster `kubectl apply` / `kubectl
  attach`, plus registry publication.
- The active source-shaped bottleneck remains Tranche 17 trace tuning. The
  first lessons are now encoded: inside-root is not the same as safe-to-write
  for sandbox control files, valid multiline scaffold intent should not be lost
  to common JSON drift, successful parser repairs must be visible before
  graduation, and operators need a phase trail while runs are active. The
  current remaining work is to validate and park this visibility slice, then
  compare across the broader scenario set before graduation shaping.

## Next best move

- Finish Tranche 17F validation and commit, then export a final reviewer packet
  and event tail over the selected pass set. The parking threshold is a pass set
  with no safety signals, no recovery classes, and no parse repair signals,
  plus an operator-visible event trail for harness phases.

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
- Teaching Sandbox `_docs/TASK_CARD.md` and
  `_docs/builder_constraint_contract.md` are code-protected during sidecar
  write tools. Treat any attempted rewrite as a `control_file_tamper` safety
  signal, not normal app-artifact work.
- Successful parser repairs are visible as `parse_repair_signals`. They are
  useful teaching telemetry in Tranche 17, but Tranche 18 graduation runs should
  be repair-silent.
- Teaching Sandbox event logs are sanitized status trails, not raw transcripts.
  Use them for operator visibility, not as a place to preserve generated app
  source or private local paths.
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
