# _constraint-registry

Atomic constraint registry for the **Builder Constraint Contract (BCC)**.

## What It Does

Decomposes the full 1,250-line BCC into ~65 **Atomic Constraint Units (ACUs)**
— each tagged by domain, severity, and tier — stored in a queryable SQLite
database. Pre-built **task profiles** assemble the right constraints for common
agent work types.

This enables **surgical injection**: instead of feeding a small model the
entire contract, you give it only the 5–10 rules relevant to its current task.

## Architecture

```
Full BCC (human-readable)
    ↓ decomposition
constraint_registry.sqlite3
    ├── constraint_units (65+ ACUs)
    │   ├── uid, section, title
    │   ├── domain_tags (ownership, ui, core, boundary, ...)
    │   ├── severity (HARD_BLOCK, PUSHBACK, ADVISORY)
    │   ├── tier (spirit, letter, gate)
    │   └── instruction (distilled rule text)
    └── task_profiles (8 profiles)
        ├── ui_implementation
        ├── core_implementation
        ├── refactoring
        ├── sourcing_extraction
        ├── documentation
        ├── cleanup
        ├── tool_creation
        └── scaffolding
```

## Tier System

| Tier | For | What It Provides |
|------|-----|------------------|
| `spirit` | Large reasoning models (14B+) | High-level intent and architectural philosophy |
| `letter` | Instruction/tool models (1.5B–7B) | Specific actionable rules |
| `gate` | Tiny/binary decision models | Hard yes/no boundary checks |

## Quick Start

```bash
# Build the registry
python tools/registry_build.py run --input-json "{}"

# Get constraints for a UI task
python tools/constraint_query.py run --input-json '{"profile": "ui_implementation"}'

# Get only HARD_BLOCK rules for ownership
python tools/constraint_query.py run --input-json '{"domain": "ownership", "severity": "HARD_BLOCK"}'

# Get gate-tier rules only (for small models)
python tools/constraint_query.py run --input-json '{"profile": "cleanup", "tier": "gate"}'

# List all available profiles
python tools/constraint_query.py run --input-json '{"list_profiles": true}'

# List all domain tags
python tools/constraint_query.py run --input-json '{"list_domains": true}'

# Registry statistics
python tools/constraint_query.py run --input-json '{"stats": true}'
```

## MCP Server

```bash
python mcp_server.py
```

Exposes `registry_build` and `constraint_query` over MCP stdio transport.

## Self-Test

```bash
python smoke_test.py
```

## Important Distinction

This package is the **vendable constraint registry** — it gets installed INTO
target projects so local agents can query the rules relevant to their tasks.

It is NOT the full working contract used by the top-level orchestrating agent
(that lives at `.dev-tools/CONTRACT.md` and never gets vended).
