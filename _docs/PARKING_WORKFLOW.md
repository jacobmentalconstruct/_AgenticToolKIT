# Parking Workflow

_Last updated: 2026-04-29._

This document records the practical park-and-handoff workflow for meaningful
tranches inside `.dev-tools`.

It is adapted from a stricter builder parking regimen, but normalized to the
surfaces that actually exist in this toolbox. The goal is not ceremony for its
own sake. The goal is to leave the repo resumable, inspectable, and honest.

---

## One-Pass Park Loop

Use this sequence at the end of a meaningful tranche:

1. Inspect repo state.
2. Identify tranche-owned changes.
3. Run focused verification.
4. Capture evidence, warnings, and current truth.
5. Summarize tranche outcome.
6. Update active continuity docs.
7. Write append-only journal/backlog state.
8. Re-run final verification if docs or code changed.
9. Report park state and the next tranche clearly.

---

## Practical Park Steps

### 1. Inspect repo state

- Run `git status --short --branch`.
- Identify all files changed during the tranche.
- Separate tranche-owned changes from unrelated pre-existing or user changes.

### 2. Run the right verification

- Run focused verification for the exact surface touched.
- Run broader verification when shared behavior moved.
- Typical toolbox checks:
  - `python src/smoke_test.py`
  - package-local `smoke_test.py`
  - manifest/readme review
  - launch-path checks
  - install-path checks
  - targeted compile checks when source changed

### 3. Capture evidence

Record the things the next session would otherwise have to rediscover:

- commands run
- pass/fail results
- warnings
- relevant outputs
- trust-boundary notes
- any runtime or packaged-surface truth that changed

### 4. Name the parked tranche

Record:

- tranche name
- status
- what changed
- why it changed
- what boundary it preserves

Useful status language for this toolbox:

- `parked_complete`
- `recorded`
- `blocked`
- `deferred`

### 5. Update continuity docs

Update the docs that future sessions actually use:

- `_docs/WE_ARE_HERE_NOW.md`
- `_docs/TODO.md`
- `_docs/DEV_LOG.md`
- `_docs/EXPERIENTIAL_WORKFLOW.md` when the collaboration method changed
- `README.md` when user-facing entry or architecture understanding changed
- package or authority readmes when their local truth changed

### 6. Journal and backlog discipline

- Use append-only behavior for meaningful session records.
- Do not rewrite prior history casually.
- Keep deferred work visible without pretending it is active.
- Mirror notable longer-range capability goals into `_docs/NORTHSTARS.md`.

### 7. Orbit/spiral check

Use this as a light parking-analysis checkpoint, not as a new ceremony.

During park, classify the tranche as:

- `spiral`
- `orbit`
- `blocked`

If the tranche ended in review, constraint tightening, or repeated
test/check/tighten cycles, ask:

- did capability increase?
- did uncertainty decrease?
- did a boundary become clearer?
- did a future implementation path become more concrete?

If the tranche was mostly review or doctrine work, record what changed:

- new guardrail
- clarified non-goal
- exposed blocker
- deferred capability
- safer implementation path

If the tranche feels like a locked orbit, name the lock:

- contract lock
- architectural non-goal
- missing evidence
- missing fixture
- ambiguous ownership
- truth-boundary risk

Then record the escape vector:

- implement the next smallest feature
- create a falsifier or fixture
- add instrumentation
- ask the user for a boundary decision
- park as deferred sibling work
- update contract or motion only if explicitly authorized

Always end by naming the next concrete tranche that resumes forward motion.

### 8. Re-run final verification when needed

If the tranche changed source, tests, docs that affect commands, or operational
entry surfaces, do a final verification pass before calling it parked.

### 9. Report the park state

At minimum, report:

- changed files
- verification commands and results
- current next tranche
- unresolved risks or skipped verification

---

## Minimum Park Payload

Every meaningful park should leave these truths visible:

- what changed
- why it changed
- what was verified
- whether the tranche was spiral, orbit, or blocked
- what remains
- what the next bounded move is

If those five things are not easy to recover, the tranche is not really parked.

---

## Toolbox-Specific Notes

- This toolbox does not currently expose every project-side parking surface used
  in larger app regimens such as `PROJECT_STATUS.md` or
  `THOUGHTS_FOR_NEXT_SESSION.md`.
- For now, the closest equivalent continuity packet here is:
  - `_docs/WE_ARE_HERE_NOW.md`
  - `_docs/TODO.md`
  - `_docs/DEV_LOG.md`
  - `_docs/NORTHSTARS.md`
  - journal surfaces under `_docs/_journalDB/` and `_docs/_AppJOURNAL/`
- If a fuller parking packet becomes standard for `.dev-tools`, extend this
  workflow deliberately rather than by one-off drift.
