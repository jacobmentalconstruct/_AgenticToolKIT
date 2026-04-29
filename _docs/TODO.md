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

---

## Current tranche

Name the current bounded work slice and list only the tasks that belong in it.

### Active tasks

- [x] Integrate the park-and-handoff doctrine cleanly into the dev-suite docs.
- [x] Add a machine-readable release payload inventory for the sidecar install path.
- [x] Add the full sidecar install path, project setup flow, and onboarding-site verification tools.
- [x] Run and tighten the fresh-project trial from an installed sidecar only.
- [x] Classify `authorities/` and remaining reference/cache material for release payload handling.
- [ ] Formalize how toolbox-level backlog items should be mirrored into the app journal.
- [ ] Scope and build the Windows-safe search fallback tool as the first concrete capability-hardening surface.

### Explicit non-goals

- [ ] Do not turn this backlog into a vague dumping ground with no ownership.
- [ ] Do not treat wishlist items as active implementation commitments by default.

---

## Near-term follow-up

- [ ] Add a lightweight convention for tagging backlog items as toolbox, package, or cross-project ideas.
- [ ] Decide whether `WE_ARE_HERE_NOW.md` should stay minimal or grow a more formal `PROJECT_STATUS`-style structure.
- [ ] Use `_docs/NORTHSTARS.md` to track capability-parity goals separately from bounded backlog work.
- [ ] Decide whether more of the setup-doctrine packet should be promoted into builtin scaffold files by default.
- [ ] Decide whether `authorities/` should be archived outside the release payload or deleted after harvest completion.
- [ ] Review whether root `authority.sqlite3` remains a transitional ship item or should become reference-only before release candidate.

---

## Longer-horizon work

- [ ] Build a repo-safe search fallback tool for Windows environments that detects `rg` permission/app-bundle failures and cleanly falls back to native PowerShell search instead of triggering awkward security-bypass behavior or brittle manual recovery.

---

## Known technical debt

- [ ] The repo does not yet have a formal, consistently used backlog/journal mirroring habit for toolbox-level deferred ideas.
- [ ] The toolbox continuity packet is improving, but still lighter than the fuller park packets used in stricter project-side regimens.
- [x] The installed sidecar flow no longer carries the `authorities/` reference bundle by default.
- [ ] Root `authority.sqlite3` remains a transitional authority artifact pending final release-candidate review.

---

## Compliance checklist

- [ ] `_docs/ARCHITECTURE.md` exists and reflects current truth
- [x] `_docs/WE_ARE_HERE_NOW.md` is current
- [ ] `_docs/builder_constraint_contract.md` exists
- [ ] `_docs/DEV_LOG.md` is being appended meaningfully
- [ ] `_docs/_journalDB/app_journal.sqlite3` exists
- [ ] `_docs/_AppJOURNAL/` is exportable/queryable
