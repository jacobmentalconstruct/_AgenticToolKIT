# .dev-tools — Universal Agent Toolbox

A project-agnostic toolbox designed to be vendored into any project for use by
human developers and AI agents. Contains builder tools for working ON projects,
vendable packages for installing INTO projects, and reusable document templates.

Everything here is portable, self-contained, and free of project-specific
coupling. If you move this folder, it still works.

---

## Start Here

If you want the friendliest onboarding path from a copied folder, open:

- `START_HERE.html`
- `OPEN_ME_FIRST.bat` (Windows)
- `OPEN_ME_FIRST.command` (macOS)

| If you are... | Read this first |
|---------------|-----------------|
| A human seeing this toolbox for the first time | `START_HERE.html` → then this file |
| An agent entering for the first time | `toolbox_manifest.json` → then `_docs/AGENT_GUIDE.md` |
| A human wanting the full picture | This file, then `CONTRACT.md` and `VENDORING.md` |
| An agent about to build a project | `_docs/AGENT_GUIDE.md` — workflow loops and tool selection |
| Looking to vend tools into a project | `VENDORING.md` — vendoring guide for all three tiers |
| Wanting the lived workflow behind the mechanics | `_docs/EXPERIENTIAL_WORKFLOW.md` |
| Looking for the dev history | `_docs/DEV_LOG.md` |

---

## Four-Surface Architecture

### Tier 1: Builder Tools (`src/tools/`)

Analysis, patching, and audit tools that **stay in the toolbox**. Agents use
these to work ON target projects without modifying the toolbox itself.

| Tool | Category | Purpose |
|------|----------|---------|
| `journal_init` | bootstrap | Initialize a journal database |
| `journal_manifest` | introspection | Read tool/package manifests |
| `journal_write` | write | Write entries to the journal |
| `journal_query` | query | Query journal entries |
| `journal_export` | export | Export journal data |
| `journal_acknowledge` | contract | Acknowledge contract terms |
| `journal_actions` | ledger | Track action items |
| `journal_scaffold` | scaffold | Scaffold project layouts |
| `journal_pack` | packing | Pack journal into DB |
| `journal_snapshot` | snapshot | Snapshot journal state |
| `authority_build` | packaging | Build packed authority DB |
| `authority_install` | install | Install shim into target project |
| `module_decomp_planner` | architecture | AST-based module decomposition planning |
| `tokenizing_patcher` | editing | Whitespace-immune hunk-based patching |
| `domain_boundary_audit` | analysis | Detect domain boundary violations |
| `scan_blocking_calls` | analysis | Scan for UI-blocking calls |
| `sqlite_schema_inspector` | introspection | Inspect SQLite schema, tables, indexes, sample rows |
| `import_graph_mapper` | analysis | Map Python import dependency graph with cycle detection |
| `tkinter_widget_tree` | analysis | Map Tkinter widget hierarchy, geometry, and bindings |
| `builderset_authority_build` | packaging | Build the packed BuilderSET authority DB from the live repo |
| `builderset_authority_manifest` | introspection | Inspect the packed BuilderSET authority manifest and schema |
| `builderset_authority_query` | introspection | Query packed BuilderSET files without hydrating them |
| `builderset_authority_prepare_runtime` | runtime | Hydrate or reuse the packed BuilderSET runtime cache |
| `builderset_authority_export` | export | Export selected packed BuilderSET files on demand |
| `builderset_authority_launch` | runtime | Describe or probe packed BuilderSET launch surfaces |

Every tool follows the same contract: `FILE_METADATA` dict + `run(arguments)`
function + `standard_main()` CLI. See `CONTRACT.md` for the full mechanical
specification.

### Tier 2: Packed Authorities (`authorities/`)

Toolbox-resident codices that are preserved as SQLite artifacts and run from a
managed runtime cache.

| Authority | Purpose |
|-----------|---------|
| `_builderset-authority/` | Packed SQLite authority for BuilderSET with runtime/reference classes and cache-backed execution |

See [`authorities/README.md`](authorities/README.md) for the overview and
[`authorities/_builderset-authority/README.md`](authorities/_builderset-authority/README.md)
for the BuilderSET-specific surface.

### Tier 3: Vendable Packages (`packages/`)

Self-contained subprojects that get **installed into** target projects. Each
package has its own MCP server, CLI tools, smoke test, and documentation.

| Package | Purpose |
|---------|---------|
| `_app-journal/` | SQLite-backed shared journal with Tkinter UI and MCP access |
| `_manifold-mcp/` | Reversible text-evidence-hypergraph with evidence bags |
| `_ollama-prompt-lab/` | Local prompt evaluation and Ollama model comparison |
| `_constraint-registry/` | Atomic constraint registry for surgical rule injection into agent prompts |

See [`packages/README.md`](packages/README.md) for vendoring instructions.

### Tier 4: Vendable Documents (`templates/`)

Project-agnostic templates and reference docs that can be copied into any new
project as starting points.

| Template | Purpose |
|----------|---------|
| `_BuilderConstraintCONTRACT/` | The full Builder Constraint Contract — governance for agent-driven development |

See [`templates/README.md`](templates/README.md) for details.

---

## Agent Entry (Zero Context)

If you are an agent arriving with no prior context:

1. **Read `toolbox_manifest.json`** — it indexes all three tiers and tells you
   what is available.
2. **Read `CONTRACT.md`** if you are about to build or modify a project — it
   defines the rules you operate under.
3. **Read `VENDORING.md`** if you need to install tools or packages into a
   target project.
4. **Choose** from builder tools or vendable packages based on your task.
5. **Open** the chosen area's `tool_manifest.json` and `README.md` for
   specifics.

---

## Human Entry

```powershell
run.bat          # Windows
./run.sh         # Linux/macOS
```

## MCP Server

```powershell
python src/mcp_server.py
```

Exposes all 25 builder tools over MCP stdio transport.

## Self-Test

```powershell
python src/smoke_test.py
```

---

## Typical Workflow

1. **Build** the packed authority DB:
   ```
   python src/tools/authority_build.py run --input-json "{}"
   ```

2. **Build** the packed BuilderSET authority:
   ```
   python src/tools/builderset_authority_build.py run --input-json "{}"
   ```

3. **Hydrate** the BuilderSET runtime cache:
   ```
   python src/tools/builderset_authority_prepare_runtime.py run --input-json "{}"
   ```

4. **Install** the thin shim into a target project:
   ```
   python src/tools/authority_install.py run --input-json "{\"target_project_root\": \"C:\\path\\to\\project\"}"
   ```

5. **Vend a package** by copying from `packages/` into the target project:
   ```
   cp -r packages/_app-journal <target>/.dev-tools/_app-journal
   ```

6. **Vend templates** by copying from `templates/` as needed.

---

## Key Documents

| Document | What It Covers |
|----------|---------------|
| `CONTRACT.md` | Builder Constraint Contract — the governing discipline for agents |
| `VENDORING.md` | How to vend tools, packages, and templates into target projects |
| `toolbox_manifest.json` | Machine-readable index of all tiers and packages |
| `tool_manifest.json` | Machine-readable index of all builder tools |
| `_docs/EXPERIENTIAL_WORKFLOW.md` | Human-agent workflow rhythm and onboarding doctrine |
| `_docs/DEV_LOG.md` | Development history and change log |
| `_docs/BLUEPRINT.md` | App-journal architecture blueprint |
| `LICENSE.md` | Source-available reference license |

---

## License

Source-Available Reference License. You may read, study, and learn from this
code. Copying, distribution, and commercial use require written authorization.
See [`LICENSE.md`](LICENSE.md) for full terms.
