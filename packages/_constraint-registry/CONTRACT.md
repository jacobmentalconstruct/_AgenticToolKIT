# Contract

## Package Purpose

`_constraint-registry` is the machine-readable projection of the Builder
Constraint Contract (BCC). It enables surgical injection of task-relevant
constraints into agent prompts without requiring models to parse the full
document.

## Tool Contract

Every tool follows the `FILE_METADATA + run(arguments)` pattern:

```python
FILE_METADATA = {
    "tool_name": "...",
    "version": "...",
    "entrypoint": "tools/...",
    "category": "...",
    "summary": "...",
    "mcp_name": "...",
    "input_schema": { ... },
}

def run(arguments: dict) -> dict:
    ...
```

### CLI Modes

```bash
python tools/<tool>.py metadata          # show metadata
python tools/<tool>.py run --input-json   # run with inline JSON
python tools/<tool>.py run --input-file   # run with JSON file
```

### Result Envelope

```json
{
  "status": "ok",
  "tool": "constraint_query",
  "input": { ... },
  "result": { ... }
}
```

## Registry Schema

### constraint_units

| Column | Type | Purpose |
|--------|------|---------|
| uid | TEXT PK | Stable identifier (e.g. BCC-4.1) |
| section | TEXT | Source section in the BCC |
| subsection | TEXT | Subsection number |
| title | TEXT | Human-readable rule name |
| domain_tags | JSON array | Searchable domain tags |
| severity | TEXT | HARD_BLOCK, PUSHBACK, or ADVISORY |
| tier | TEXT | spirit, letter, or gate |
| instruction | TEXT | Distilled rule text |
| full_text | TEXT | Original verbose contract text (optional) |

### task_profiles

| Column | Type | Purpose |
|--------|------|---------|
| profile_id | TEXT PK | Profile name (e.g. ui_implementation) |
| description | TEXT | What this profile covers |
| constraint_uids | JSON array | UIDs of constraints in this profile |

## Vendoring Rule

This package is vendable. It discovers its own location at runtime via
`Path(__file__).resolve()`. No hardcoded paths. No project-specific assumptions.
