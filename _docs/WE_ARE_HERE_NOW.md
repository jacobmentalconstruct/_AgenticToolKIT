# WE_ARE_HERE_NOW

_Fast pickup note for `.dev-tools`. Update this at meaningful milestones._

## Last updated

- 2026-04-30 (Tranche 1 local-agent sys-ops introspection implemented)

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
    Kubernetes-wrapped bridge; Tranche 1 read-only local-agent sys-ops
    introspection is implemented and Tranche 2 is next
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

## Current bottleneck

- No internal root bottleneck. Remaining container work is operational:
  live-cluster `kubectl apply` / `kubectl attach`, plus registry publication.
- The next source-shaped bottleneck is Tranche 2: dependency readiness and
  stronger command-profile IDs for later guarded operations.

## Next best move

- Either finish the operational pod proof (`kubectl apply`, readiness,
  `kubectl attach`, registry push), or open Tranche 2:
  `dependency_env_check` plus command-profile refinements.

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
