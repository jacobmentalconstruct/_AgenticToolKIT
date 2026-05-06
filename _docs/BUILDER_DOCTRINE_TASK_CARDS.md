# Builder Doctrine Task Cards

_Introduced: 2026-05-06 for Tranche 15._

Task cards are the bridge between the builder doctrine and the local sidecar
agent. Their job is to remove avoidable inference: what to read, what to build,
which tools are allowed, what files should exist, how to verify, how to journal,
and what a truthful final claim must cite.

The Tranche 14 live baseline failure made the first rule concrete. Disposable
Teaching Sandbox projects need a sandbox-local contract and task card that are
complete inside the sandbox. A live model should not chase a pointer to a root
`CONTRACT.md` that is not present in the sandbox.

---

## Card Rules

Every task card must include:

- Local contract rule.
- Allowed tools.
- Expected artifacts.
- Required, optional, and forbidden doctrine steps.
- Verification checks.
- Journaling, trace, and evidence expectations.
- Final claim rule.

Project-birth cards that use `directory_scaffold` must include a scaffold
argument rule:

- `entries` must be a list of objects, not a list of strings.
- Each file entry must include `type`, `path`, `content`, and `overwrite`.
- The first scaffold call should provide real content for each expected file.
- Multiline file `content` must stay inside one valid JSON string; prefer
  escaped `\n` sequences rather than literal line breaks inside tool-call JSON.
- Tool calls should be a single ```tool_call fenced JSON object without
  extra closing tags such as `[/tool_call]`.
- If a later `text_file_writer` call rewrites an existing file, it must set
  `action:"overwrite"` and `overwrite:true`.

Every Teaching Sandbox task card must say:

- Treat `_docs/builder_constraint_contract.md` as the complete sandbox-local
  contract.
- Treat `_docs/TASK_CARD.md` and `_docs/builder_constraint_contract.md` as
  protected control files, not app artifacts to rewrite.
- Do not read `CONTRACT.md`, `../CONTRACT.md`, parent folders, or paths outside
  the sandbox.
- If a pointer appears stale, continue with the sandbox-local contract and the
  task card.

---

## Reusable Templates

| Template | Purpose | Required sections |
|---|---|---|
| `project_birth` | Create a new small project from a task card. | Local contract rule; allowed tools; expected artifacts; verification checks; journal/evidence expectations; final claim rule. |
| `feature_addition` | Add a feature to an existing project without changing unrelated behavior. | Current behavior; new behavior; touched files; verification checks. |
| `bug_fix` | Correct a named defect with a focused reproduction and verification loop. | Observed failure; expected behavior; fix boundary; regression check. |
| `validation_pass` | Run declared validation, inspect failures, and report honest status. | Commands or tool checks; pass/fail evidence; residual risk. |
| `recovery_pass` | Recover from a failed or partial run using named recovery classes. | Recovery class; safe next action; evidence to preserve. |
| `documentation_park` | Update continuity documents and journal state after meaningful work. | Changed truth; verification; next tranche. |
| `release_handoff` | Prepare a project for handoff with verified payload and known warnings. | Release payload; verification; known warnings; handoff state. |

---

## Scenario Metadata

The Teaching Sandbox curriculum now uses task-card metadata across both
project-birth and feature-addition practice.

The project-birth static web scenarios are `static_task_tracker`,
`static_calculator`, and `markdown_previewer`. They require:

- `read_sandbox_local_contract`
- `read_task_card`
- `scaffold_expected_files`
- `validate_static_artifacts`
- `journal_and_trace_result`
- `cite_touched_paths`

The project-birth stdlib Python scenarios are `python_notes_cli`,
`csv_cleaner_cli`, and `config_validator_cli`. They require:

- `read_sandbox_local_contract`
- `read_task_card`
- `scaffold_expected_files`
- `validate_python_artifacts`
- `journal_and_trace_result`
- `cite_touched_paths`

The edit-after-feedback scenario is `task_tracker_filter_update`. It uses the
`feature_addition` template and requires:

- `read_sandbox_local_contract`
- `read_task_card`
- `preserve_existing_task_lifecycle`
- `add_filter_feature`
- `validate_static_artifacts`
- `journal_and_trace_result`
- `cite_touched_paths`

All current scenarios allow:

- `checkpoint_private_git`

All current scenarios forbid:

- `read_parent_contract`
- `raw_shell`
- `dependency_install`
- `outside_root_write`

---

## First Teaching Change

Tranche 15 changes the Teaching Sandbox harness so generated sandbox projects
write a complete sandbox-local `_docs/builder_constraint_contract.md` instead
of copying the repository pointer document. The task card and agent prompt also
state that the model must not read `CONTRACT.md` or parent paths.

The desired live-model behavior is:

1. Read `_docs/builder_constraint_contract.md`.
2. Read `_docs/TASK_CARD.md`.
3. Scaffold the expected files under the sandbox root.
4. Validate through harness checks.
5. Cite touched paths in the final claim.

The model does not need broader filesystem authority to satisfy this. It needs
clearer local doctrine.

## Control-File Integrity

Tranche 17A adds the code-level companion to the task-card doctrine. In
Teaching Sandbox runs, the harness passes `_docs/TASK_CARD.md` and
`_docs/builder_constraint_contract.md` as protected paths into the local
sidecar. The write-capable text tools reject attempts to modify those paths
with `control_file_tamper`.

This preserves the sandbox's usefulness as a disposable practice project while
making one boundary explicit: an agent may write app artifacts under the
sandbox root, but it may not rewrite the files that define the assignment or
authority boundary for the run.

## Multiline Tool-Call Content

Tranche 17B adds a second trace-tuning lesson from `compare_runs`: several live
practice runs expressed valid scaffold intent but placed literal multiline file
content inside JSON string values, producing `malformed_tool_call` before the
tool schema could run.

Task cards should continue teaching valid JSON, especially escaped `\n`
sequences for generated HTML, CSS, JavaScript, Python, README, and sample-data
content. `local_sidecar_agent` now has a narrow tolerance for raw newline,
carriage-return, and tab characters inside JSON strings, but that is a recovery
rail, not the desired style. The desired behavior is still a single fenced JSON
object whose `content` values are valid JSON strings.
