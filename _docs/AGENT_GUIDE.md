# Agent Operations Guide

_How to actually use this toolbox. Not a reference manual — a playbook._

You have access to a large toolkit. Most of it you will never need in a single
session. This guide teaches you which tools to reach for, when, and why — so you
spend tokens on building, not fumbling.

---

## The Two Rules

1. **Orient before you build.** Every session starts with introspection. You
   cannot write good code for a project you have not measured.
2. **Journal as you go.** If you learned something, decided something, or
   changed something — write it down. The next agent (or the next you) starts
   from your journal, not from scratch.

---

## Session Startup (Every Time)

When you arrive at a project with `.dev-tools` installed, do this first:

```
1. Read toolbox_manifest.json          → know what is available
2. Read tool_manifest.json             → know the builder tools by name
3. journal_query (last 5 entries)      → pick up where the last session left off
4. constraint_query (your task profile)→ load only the rules that apply to your task
```

This costs almost nothing and prevents the two most expensive mistakes: building
something that already exists, and violating a constraint you did not know about.

---

## The Four Workflow Loops

Every task you do fits one of these patterns. Learn the loop, not the tool list.

### Loop 1: Orient → Plan → Build → Verify

_The standard build cycle. Use for any feature, fix, or refactor._

```
ORIENT
  file_tree_snapshot        → understand the project shape
  import_graph_mapper       → see how modules connect
  sqlite_schema_inspector   → see what data structures exist
  journal_query             → read prior decisions and context

PLAN
  python_complexity_scorer  → find the messiest code (refactor targets)
  module_decomp_planner     → plan how to break up large modules
  domain_boundary_audit     → check if your plan crosses domain lines
  constraint_query           → load task-relevant rules before writing code

BUILD
  (your normal coding work)
  tokenizing_patcher        → apply patches that survive whitespace drift
  test_scaffold_generator   → generate test stubs for new code

VERIFY
  scan_blocking_calls       → catch UI-blocking calls before they ship
  dead_code_finder          → catch unused code before it rots
  import_graph_mapper       → confirm you did not create circular imports
  smoke_test_runner         → run all smoke tests in one pass
  journal_write             → record what you built and why
```

### Loop 2: Investigate → Diagnose → Fix → Confirm

_The debug cycle. Use when something is broken or behaving wrong._

```
INVESTIGATE
  journal_query             → was this area changed recently?
  sqlite_schema_inspector   → is the DB schema what we expect?
  schema_diff_tool          → did the schema drift from baseline?
  import_graph_mapper       → are dependencies tangled?

DIAGNOSE
  python_complexity_scorer  → is the function too complex to reason about?
  domain_boundary_audit     → is the bug at a domain crossing point?
  tkinter_widget_tree       → (for UI bugs) is the widget hierarchy wrong?
  dead_code_finder          → is the "broken" code even being called?

FIX
  (your normal fix work)
  tokenizing_patcher        → apply the fix as a clean patch

CONFIRM
  smoke_test_runner         → does everything still pass?
  journal_write             → record the root cause and fix
```

### Loop 3: Audit → Score → Decompose → Restructure

_The refactoring cycle. Use when the codebase needs structural improvement._

```
AUDIT
  file_tree_snapshot        → full project inventory
  python_complexity_scorer  → rank every function by complexity
  import_graph_mapper       → find circular dependencies
  dead_code_finder          → find unused definitions to remove
  domain_boundary_audit     → find functions reaching across domains

SCORE
  (review the complexity scorer output)
  (sort by composite_score descending)
  (identify the top 3-5 decomposition targets)

DECOMPOSE
  module_decomp_planner     → get concrete extraction plan for each target
  test_scaffold_generator   → generate test stubs BEFORE refactoring

RESTRUCTURE
  (move code according to the plan)
  tokenizing_patcher        → apply structural patches cleanly
  import_graph_mapper       → verify the graph improved
  smoke_test_runner         → verify nothing broke
  journal_write             → record the rationale
```

### Loop 4: Onboard → Configure → Validate

_The project setup cycle. Use when starting a new project or installing tools._

```
ONBOARD
  (use install.py or authority_install to vend .dev-tools into the project)
  journal_init              → create the project journal database
  journal_acknowledge       → accept the builder constraint contract
  constraint_query (profile: scaffolding) → load setup-phase rules

CONFIGURE
  journal_scaffold          → generate project directory layout
  (set up dependencies, entry points, config files)

VALIDATE
  file_tree_snapshot        → confirm the project structure is correct
  smoke_test_runner         → run all available smoke tests
  journal_write             → record the project bootstrap decisions
```

---

## Tool Selection Cheat Sheet

_"I need to…" → use this tool._

| I need to… | Tool |
|---|---|
| Understand the project file layout | `file_tree_snapshot` |
| See how Python modules depend on each other | `import_graph_mapper` |
| Inspect a SQLite database structure | `sqlite_schema_inspector` |
| Compare two database versions | `schema_diff_tool` |
| Find the most complex functions | `python_complexity_scorer` |
| Plan how to split a large module | `module_decomp_planner` |
| Check for domain boundary violations | `domain_boundary_audit` |
| Find unused code to clean up | `dead_code_finder` |
| Find blocking calls in async/UI code | `scan_blocking_calls` |
| Map a Tkinter widget hierarchy | `tkinter_widget_tree` |
| Apply a patch that survives whitespace changes | `tokenizing_patcher` |
| Generate test stubs for new code | `test_scaffold_generator` |
| Run all smoke tests at once | `smoke_test_runner` |
| Read what happened last session | `journal_query` |
| Record a decision or finding | `journal_write` |
| Load rules for my current task | `constraint_query` |
| Install tools into a new project | `authority_install` or `install.py` |

---

## Token Economy: How to Be Efficient

These tools exist so you do not waste tokens reading files you do not need,
writing code that already exists, or debugging problems you could have prevented.

### Cheap Orientation Beats Expensive Recovery

Reading `file_tree_snapshot` output costs ~200 tokens. Reading 15 wrong files
hunting for a function costs ~3,000 tokens. **Always orient first.**

### Chain, Do Not Scatter

Bad (5 separate tool calls, 5 round trips):
```
import_graph_mapper → read output → think → dead_code_finder → read output →
think → python_complexity_scorer → read output → think → …
```

Good (orient once, plan once, build once):
```
Run import_graph_mapper, dead_code_finder, python_complexity_scorer together.
Read all three outputs. Form one plan. Execute the plan. Verify.
```

The analysis tools are **read-only and fast**. Run them in parallel at the start
of a session to get the full picture, then reason from the combined output.

### Journal Saves Future Tokens

Writing a 50-token journal entry now saves the next session 500 tokens of
re-investigation. Every decision you record is a decision no one has to remake.

Write journal entries for:
- Architectural decisions ("We split module X because of circular imports")
- Dead ends ("Approach Y did not work because of Z")
- Discoveries ("Table W has an undocumented column used by feature V")
- Session handoffs ("I finished X, next session should do Y")

### Constraints Save Rework Tokens

Loading `constraint_query` with your task profile at session start costs ~100
tokens. Violating a constraint you did not know about, then discovering and
fixing it later, costs 500-2,000 tokens. **Load constraints before building.**

Task profiles available: `ui_implementation`, `core_implementation`,
`refactoring`, `sourcing_extraction`, `documentation`, `cleanup`,
`tool_creation`, `scaffolding`.

---

## Narrative Walkthrough: A Real Session

_An agent is asked to add a settings dialog to a Tkinter application._

### Phase 1: Orient (30 seconds, ~300 tokens)

```
→ journal_query: {"project_root": ".", "limit": 5}
  Last entry: "Finished main dashboard layout. Settings dialog is next.
  User wants dark theme consistency. See _docs/DESIGN.md for color palette."

→ file_tree_snapshot: {"project_root": ".", "max_depth": 3}
  src/ui/main_window.py (340 lines)
  src/ui/dashboard.py (280 lines)
  src/ui/theme.py (45 lines)
  src/data/settings_store.py (120 lines)

→ constraint_query: {"profile": "ui_implementation"}
  18 constraints loaded. Key ones:
  - HARD_BLOCK: "UI must remain responsive — no blocking calls on main thread"
  - PUSHBACK: "New UI surfaces must reuse the project's existing theme"
  - ADVISORY: "Prefer composition over inheritance for widget hierarchies"
```

The agent now knows: there IS a theme module, there IS a settings store, the
last session specifically said "settings dialog is next," and the constraints
say to reuse the theme and avoid blocking calls.

_Without these tools, the agent would have read 8-10 files trying to figure
this out, and might have missed the constraint about blocking calls entirely._

### Phase 2: Analyze (20 seconds, ~200 tokens)

```
→ tkinter_widget_tree: {"target": "src/ui/main_window.py"}
  Root: MainWindow(tk.Tk)
  ├── MenuBar (tk.Menu)
  ├── DashboardFrame (ttk.Frame)
  └── StatusBar (ttk.Frame)

→ import_graph_mapper: {"project_root": "src/"}
  ui/main_window.py imports: ui/dashboard, ui/theme, data/settings_store
  No circular dependencies.

→ python_complexity_scorer: {"target": "src/ui/main_window.py"}
  MainWindow.__init__: score 6.5 (manageable)
  MainWindow._build_menu: score 4.2 (simple)
```

The agent now knows exactly where the settings dialog fits in the widget tree,
what the import graph looks like, and that the main window is not overly complex.

### Phase 3: Build

The agent writes `src/ui/settings_dialog.py`, using `theme.py` for colors,
`settings_store.py` for persistence, and following the widget composition
pattern from `dashboard.py`.

```
→ test_scaffold_generator: {"source_file": "src/ui/settings_dialog.py"}
  Generated: 6 test stubs for SettingsDialog methods
```

### Phase 4: Verify (15 seconds, ~150 tokens)

```
→ scan_blocking_calls: {"target": "src/ui/settings_dialog.py"}
  No blocking calls found. ✓

→ import_graph_mapper: {"project_root": "src/"}
  No new circular dependencies. ✓

→ smoke_test_runner: {}
  All smoke tests pass. ✓

→ journal_write: {
    "project_root": ".",
    "title": "Settings dialog implemented",
    "body": "Added src/ui/settings_dialog.py. Uses theme.py for dark theme,
    settings_store.py for persistence. Accessible from MenuBar → Settings.
    Test stubs generated. No blocking calls. Next: wire up actual preference
    fields (font size, export path, auto-save interval).",
    "kind": "decision",
    "tags": ["ui", "settings"]
  }
```

**Total introspection cost: ~650 tokens, ~65 seconds.**
**Prevented: ~2,000 tokens of blind file reading, zero rework from constraint
violations, complete context for the next session.**

---

## Session Handoff Protocol

When you are ending a session or running low on context:

1. **Write a journal entry** summarizing what you accomplished and what remains.
2. **Be specific** about next steps — file names, function names, decisions pending.
3. **Record any discoveries** that are not obvious from the code itself.
4. **Note any constraints** you bumped into or intentionally deferred.

The next agent starts from `journal_query` and picks up where you left off. If
your handoff entry is good, they skip the entire orientation phase.

---

## Common Mistakes

| Mistake | Cost | Prevention |
|---|---|---|
| Starting to code without reading the journal | Rebuild context from scratch (~500 tokens) | Always `journal_query` first |
| Not loading constraints for your task type | Rework when constraint violated (~1,000 tokens) | Always `constraint_query` at session start |
| Reading files one by one to understand structure | Slow, incomplete picture (~2,000 tokens) | Use `file_tree_snapshot` + `import_graph_mapper` |
| Skipping verification after changes | Bugs ship, next session pays for it | `smoke_test_runner` + `scan_blocking_calls` before done |
| Not writing a handoff journal entry | Next session repeats your orientation work | Always `journal_write` at session end |
| Manually hunting for dead code | Unreliable, slow | `dead_code_finder` gives the complete list |
| Guessing at module dependencies | Wrong assumptions → wrong architecture | `import_graph_mapper` shows the real graph |
| Patching code that drifted from expected whitespace | Patch fails, manual recovery | `tokenizing_patcher` is whitespace-immune |

---

## Quick Reference: Tool Contract

Every builder tool follows the same interface:

```bash
# Get tool metadata and input schema
python src/tools/<tool>.py metadata

# Run with arguments
python src/tools/<tool>.py run --input-json '{"key": "value"}'
```

All tools return a JSON envelope:
```json
{
  "status": "ok",
  "tool": "tool_name",
  "input": { ... },
  "result": { ... }
}
```

All tools are also available via MCP: `python src/mcp_server.py`

---

_This guide is part of the .dev-tools universal agent toolbox.
See README.md for the full architecture overview._
