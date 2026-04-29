# Project Backlog

_Last updated: 2026-04-29._

---

## Current footing

- `.dev-tools` is active as the main universal toolbox.
- The offline onboarding microsite is now in place as the human-first entry.
- This backlog is now joined by `WE_ARE_HERE_NOW.md`, `NORTHSTARS.md`, and the
  tranche closeout regimen in `PARKING_WORKFLOW.md`.
- The release spine now includes a full sidecar install path, project setup
  orchestration, and an onboarding-site integrity check.
- The prototype northstars are collapsed into current release truth; deferred
  expansion is intentionally out of scope for this release candidate.

---

## Current tranche

Name the current bounded work slice and list only the tasks that belong in it.

### Active tasks

- [x] Integrate the park-and-handoff doctrine cleanly into the dev-suite docs.
- [x] Add a machine-readable release payload inventory for the sidecar install path.
- [x] Add the full sidecar install path, project setup flow, and onboarding-site verification tools.
- [x] Run and tighten the fresh-project trial from an installed sidecar only.
- [x] Classify and retire remaining reference/cache material for release payload handling.
- [x] Formalize release-scope northstars and defer post-release expansion explicitly.
- [x] Formalize how toolbox-level backlog items should be mirrored into the docs-first continuity packet for this prototype.
- [x] Scope and build the Windows-safe search fallback tool as the first concrete capability-hardening surface.
- [x] Retire legacy authority/thin-shim surfaces from the active prototype shape.

### Explicit non-goals

- [x] Do not turn this backlog into a vague dumping ground with no ownership.
- [x] Do not treat wishlist items as active implementation commitments by default.

---

## Near-term follow-up

- [x] Run final release-candidate verification after reference material purge.
- [x] Commit the clean release-candidate state.

---

## Longer-horizon work

- [x] Build a repo-safe search fallback tool for Windows environments that detects `rg` permission/app-bundle failures and cleanly falls back to native search instead of triggering awkward security-bypass behavior or brittle manual recovery.

---

## Known technical debt

- [x] Toolbox-level deferred ideas are tracked in the docs-first continuity packet for this prototype.
- [x] The toolbox continuity packet is sufficient for release-candidate handoff.
- [x] The installed sidecar flow no longer carries old reference bundles by default.
- [x] Transitional authority artifacts are no longer part of the active release shape.

---

## Compliance checklist

- [x] `_docs/ARCHITECTURE.md` exists and reflects current truth
- [x] `_docs/WE_ARE_HERE_NOW.md` is current
- [x] `_docs/builder_constraint_contract.md` exists
- [x] `_docs/DEV_LOG.md` is being appended meaningfully
- [x] `_docs/_journalDB/` and `_docs/_AppJOURNAL/` exist as gitignored runtime surfaces (generated on demand by `journal_init`; not part of the shipped source state)
