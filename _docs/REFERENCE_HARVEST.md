# Reference Harvest Map

_Last updated: 2026-04-29._

The reference-harvest phase is closed for this prototype.

## Final Decision

The live release shape is the self-contained sidecar toolbox. Old
BuilderSET/packed-authority material was useful as provenance during rebuild,
but it is no longer part of the active product.

## Current Classification

| Surface | Classification | Default sidecar install | Current read |
|---|---:|---:|---|
| `README.md`, `VENDORING.md`, `CONTRACT.md`, launchers, setup scripts | ship | yes | Human and agent entry surfaces. |
| `onboarding/`, `START_HERE.html`, `assets/` | ship | yes | Protected microsite/onboarding UX. |
| `src/`, `tool_manifest.json`, `toolbox_manifest.json` | ship | yes | Active builder-tool surface. |
| `packages/`, `templates/` | ship | yes | Vendable code and document building material. |
| `_docs/` | ship | yes | Live doctrine, backlog, parking, and workflow memory. |
| `release_payload_manifest.json` | ship | yes | Machine-readable release payload boundary. |
| old packed authorities and thin-shim authority surfaces | purged | no | Reference-era shape retired from the active prototype. |
| generated caches/log exports | purged or ignored | no | Not product surface. |

## Harvest Outcome

- The useful manual install behavior moved into `install.py` and
  `sidecar_install`.
- Setup doctrine moved into `_docs/SETUP_DOCTRINE.md` and `project_setup`.
- Parking/tranche doctrine moved into `_docs/PARKING_WORKFLOW.md`.
- Human onboarding moved into the protected microsite and
  `_docs/EXPERIENTIAL_WORKFLOW.md`.
- Windows-safe inspection became `repo_search`.

## Release Gate

Before calling the prototype release-ready, run the final install and smoke
verification from this cleaned source shape.
