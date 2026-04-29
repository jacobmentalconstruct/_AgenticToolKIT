# Reference Harvest Map

_Last updated: 2026-04-29._

This file records what remaining reference material is for, what ships in the
sidecar release path, and what should be harvested or archived before the final
release candidate.

## Current Classification

| Surface | Classification | Default sidecar install | Current read |
|---|---:|---:|---|
| `README.md`, `VENDORING.md`, `CONTRACT.md`, launchers, setup scripts | ship | yes | Human and agent entry surfaces. |
| `onboarding/`, `START_HERE.html`, `assets/` | ship | yes | Protected microsite/onboarding UX. |
| `src/`, `tool_manifest.json`, `toolbox_manifest.json` | ship | yes | Active builder-tool surface. |
| `packages/`, `templates/` | ship | yes | Vendable code and document building material. |
| `_docs/` | ship | yes | Live doctrine, backlog, parking, and workflow memory. |
| `release_payload_manifest.json` | ship | yes | Machine-readable release payload boundary. |
| `authority.sqlite3` | transitional ship | yes | Retained while legacy authority/build surfaces still exist. Review again before final release candidate. |
| `authorities/` | reference pending harvest | no | Packed old BuilderSET authority/provenance bundle. Useful for comparison and extraction, not a default sidecar product surface. |
| `runtime/` | generated/cache | no | Hydrated authority runtime cache. Recreate from source when needed; do not ship. |
| `_logs/` | generated/test-only | no | Local exports and generated artifacts. |
| `.potential-intake/` | staging/exclude | no | Empty intake staging area. |
| `__pycache__/` | generated/exclude | no | Interpreter cache. |

## What Was Learned

- The live sidecar release spine is now the main product path.
- The old BuilderSET packed authority is useful as harvest/provenance material
  but should not be copied into every installed sidecar by default.
- Cleanup should follow proof: first exclude old reference material from the
  release payload, then verify install behavior, then archive or delete only
  after useful code and doctrine have been harvested.

## Harvest Targets

- Installer behavior that still matters for manual, project-local setup.
- Any setup or scaffold doctrine not already represented in
  `_docs/SETUP_DOCTRINE.md`, `_docs/PARKING_WORKFLOW.md`, or templates.
- Any microsite UX/copy pattern that improves human onboarding without linking
  back to old folders.
- Any tool implementation that should become a live builder tool, vendable
  package, or template.

## Rejected For Default Shipping

- Hydrated runtime caches.
- Local logs and generated exports.
- Old project absolute paths embedded in authority manifests.
- Reference-only codex bundles that make the installed sidecar look dependent
  on prior projects.

## Next Cleanup Gate

Before deleting or archiving reference material, run a fresh install trial from
the current manifest and confirm:

- The installed `<target>/.dev-tools` does not include `authorities/`,
  `runtime/`, `_logs/`, `.potential-intake/`, or `__pycache__/`.
- The installed microsite opens from `START_HERE.html`.
- `project_setup audit/apply/verify` works from inside the target project.
- Useful code/doctrine from the reference bundle has either been integrated or
  recorded as intentionally rejected.
