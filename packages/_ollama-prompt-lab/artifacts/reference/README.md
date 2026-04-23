# Prompt Eval Reference Pack

This folder contains a portable SQLite snapshot of the most reusable
prompt-lab history.

Included in the DB:

- canonical example job specs from `jobs/examples/`
- curated non-dry-run prompt-eval runs from `artifacts/runs/`
- prompt variants, cases, summaries, and per-run result rows
- raw artifact file contents for each included run
- onboarding notes and dataset manifest rows inside the database itself

Primary files:

- `prompt_eval_reference.sqlite3`
- `prompt_eval_reference_manifest.json`

Use this bundle when an agent needs to understand prior prompt experiments
without scraping every loose artifact folder.
