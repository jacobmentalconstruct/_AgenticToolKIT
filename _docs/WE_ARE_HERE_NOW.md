# WE_ARE_HERE_NOW

_Fast pickup note for `.dev-tools`. Update this at meaningful milestones._

## Last updated

- 2026-04-29 (strangler finalization tranche parked)

## Fresh-thread start

- Read `README.md` for the main architecture overview.
- Read `_docs/SETUP_DOCTRINE.md` if the task is a fresh project birth or scaffold phase.
- Read `_docs/TODO.md` for active backlog and next tranche shaping.
- Read `_docs/PARKING_WORKFLOW.md` for the expected park-and-handoff discipline.

## Current footing

- Project root:
  - `.dev-tools`
- Current phase or tranche:
  - parked release-candidate prototype (strangler finalization complete)
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
    inside the target project from `project_setup` onward; next step is
    container packaging for Kubernetes reuse

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

## Current bottleneck

- None internal to the prototype. The release-candidate is parkable.
  Outstanding work is packaging-shaped (Dockerfile, Kubernetes pod), not
  source-shaped.

## Next best move

- Wrap the cleaned `.dev-tools/` in a minimal Dockerfile (Python 3.11 slim,
  `COPY . /opt/dev-tools/`, headless `install.py` entrypoint against a
  mounted `/workspace`) so the same artifact serves local desktop install
  and Kubernetes pod reuse.

## Current warnings

- The backlog is still young and not yet a fully mature continuation surface.
- Deferred expansion capabilities remain intentionally out of scope for this
  release candidate.
- Not all compliance checklist surfaces exist yet in final form.

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
