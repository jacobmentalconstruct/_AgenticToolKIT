# WE_ARE_HERE_NOW

_Fast pickup note for `.dev-tools`. Update this at meaningful milestones._

## Last updated

- 2026-04-30 (Local-agent sys-ops northstar closed)

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
    Tranche 6 and the next horizon is undecided
- Current runtime truth:
  - root toolbox is now a single-purpose installer (`install.py` GUI / `run.bat` /
    `run.sh`) plus the agent-facing MCP, smoke-test, and builder-tool surfaces
  - the journal UI lives only inside the vendable `_app-journal` package; the
    toolbox root no longer pretends to be the original journal package
  - sidecar install, setup orchestration, and onboarding-site verification are
    live builder-tool surfaces, all 39 smoke tests pass on the cleaned shape
  - `.gitignore` now covers `.claude/`, `.env*`, `*.key`/`*.pem`, credentials,
    logs, and runtime journal state
- Current collaboration truth:
  - the prototype is parkable: human installs via the GUI, agent takes over
    inside the target project from `project_setup` onward; the next useful
    expansion is host/project operations tooling for a local or podded agent

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

## Current bottleneck

- No internal root bottleneck. Remaining container work is operational:
  live-cluster `kubectl apply` / `kubectl attach`, plus registry publication.
- No active source-shaped sys-ops bottleneck remains. The next move is choosing
  the post-sys-ops capability horizon.

## Next best move

- Push the closeout commit, then choose the next horizon: browser/search,
  image tools, automations, sub-agents, Node REPL, or another local-agent
  layer.

## Current warnings

- The root prototype is parked; do not edit root surfaces casually while
  the v2 tranche is open. Treat root as frozen reference for this tranche.
- `_v2-pod/.dev-tools/` is gitignored (it is just an installed sidecar);
  the wrapper code we write inside `_v2-pod/` IS tracked.
- Deferred creative/browser/automation capabilities should wait until the
  sys-ops layer gives a local agent a reliable operating envelope.

## Read in this order if resuming cold

1. `README.md`
2. `_docs/WE_ARE_HERE_NOW.md`
3. `_docs/TODO.md`
4. `_docs/PARKING_WORKFLOW.md`
5. `_docs/NORTHSTARS.md`
6. `_docs/DEV_LOG.md`

## Known truth about the docs

- `README.md` is the architecture front door.
- `SETUP_DOCTRINE.md` is the setup-first doctrine for fresh project creation.
- `WE_ARE_HERE_NOW.md` is the fast state surface.
- `TODO.md` is the active backlog and next-tranche surface.
- `PARKING_WORKFLOW.md` is the tranche park/handoff regimen.
- `NORTHSTARS.md` is the longer-range capability direction surface.
