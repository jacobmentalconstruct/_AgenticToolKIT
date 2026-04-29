# WE_ARE_HERE_NOW

_Fast pickup note for `.dev-tools`. Update this at meaningful milestones._

## Last updated

- 2026-04-29

## Fresh-thread start

- Read `README.md` for the main architecture overview.
- Read `_docs/SETUP_DOCTRINE.md` if the task is a fresh project birth or scaffold phase.
- Read `_docs/TODO.md` for active backlog and next tranche shaping.
- Read `_docs/PARKING_WORKFLOW.md` for the expected park-and-handoff discipline.

## Current footing

- Project root:
  - `.dev-tools`
- Current phase or tranche:
  - reference-harvest classification for the sidecar release payload
- Current runtime truth:
  - full sidecar install, setup orchestration, and onboarding-site verification
    are now present as live builder-tool surfaces and have passed the fresh
    temporary-project verification loop
  - the old BuilderSET packed authority is now classified as harvest/reference
    material and excluded from default sidecar installs
- Current collaboration truth:
  - the toolbox is shifting from doctrine-only planning toward a testable
    project-local install and onboarding path

## What works right now

- Four-surface toolbox architecture is established.
- Vendable packages are present and recently drift-cleaned.
- Offline onboarding microsite is in place.
- Backlog and northstars now exist as explicit surfaces.
- Full sidecar install path exists via `install.py` and `sidecar_install`.
- Project setup can now be audited, applied, and verified with `project_setup`.
- Microsite integrity can now be checked with `onboarding_site_check`.
- The temporary-project install/apply/verify/microsite trial is now passing.
- The release payload manifest now excludes `authorities/`, `runtime/`, `_logs/`,
  `.potential-intake/`, and caches from default sidecar installs.

## Current bottleneck

- The release spine now exists and old reference material is excluded from
  default installs, but final archive/delete cleanup should wait until harvest
  review is complete.

## Next best move

- Decide whether to archive or delete the excluded reference/cache surfaces
  after confirming all useful code and doctrine have been harvested.
- Build the Windows-safe search fallback tool as the next capability-hardening move.

## Current warnings

- The backlog is still young and not yet a fully mature continuation surface.
- Root `authority.sqlite3` still ships as a transitional artifact until the
  final release-candidate authority boundary is decided.
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
