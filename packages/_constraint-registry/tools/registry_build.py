"""
FILE: registry_build.py
ROLE: Build the constraint registry SQLite database from the seed data.
WHAT IT DOES:
  - Creates constraint_registry.sqlite3 with the full ACU table and task_profiles table
  - Seeds all atomic constraint units decomposed from the Builder Constraint Contract
  - Seeds pre-built task profiles for common agent work types
HOW TO USE:
  - python _constraint-registry/tools/registry_build.py metadata
  - python _constraint-registry/tools/registry_build.py run --input-json "{}"
  - python _constraint-registry/tools/registry_build.py run --input-json "{\"db_path\": \"path/to/output.sqlite3\"}"
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import standard_main, tool_result, tool_error

FILE_METADATA = {
    "tool_name": "registry_build",
    "version": "1.0.0",
    "entrypoint": "tools/registry_build.py",
    "category": "bootstrap",
    "summary": "Build or rebuild the constraint registry SQLite database from seed data.",
    "mcp_name": "registry_build",
    "input_schema": {
        "type": "object",
        "properties": {
            "db_path": {
                "type": "string",
                "description": "Path to the output SQLite file. Defaults to <package>/constraint_registry.sqlite3"
            },
            "force": {
                "type": "boolean",
                "default": False,
                "description": "If true, drop and rebuild existing tables."
            }
        }
    }
}

PACKAGE_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS constraint_units (
    uid          TEXT PRIMARY KEY,
    section      TEXT NOT NULL,
    subsection   TEXT NOT NULL DEFAULT '',
    title        TEXT NOT NULL,
    domain_tags  TEXT NOT NULL DEFAULT '[]',
    severity     TEXT NOT NULL DEFAULT 'ADVISORY',
    tier         TEXT NOT NULL DEFAULT 'letter',
    instruction  TEXT NOT NULL,
    full_text    TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS task_profiles (
    profile_id   TEXT PRIMARY KEY,
    description  TEXT NOT NULL,
    constraint_uids TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS registry_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

# ---------------------------------------------------------------------------
# Seed Data: Atomic Constraint Units
# ---------------------------------------------------------------------------

SEED_ACUS: list[dict] = [
    # ── Preamble ──────────────────────────────────────────────────────────
    {
        "uid": "BCC-PRE-1",
        "section": "Contract Use Preamble",
        "title": "Contract is governing discipline",
        "domain_tags": ["meta", "governance"],
        "severity": "HARD_BLOCK",
        "tier": "spirit",
        "instruction": "This contract is the governing build discipline, not a suggestion set or style guide. When convenience conflicts with contract discipline, prefer the contract unless the user explicitly authorizes deviation."
    },
    {
        "uid": "BCC-PRE-2",
        "section": "Contract Use Preamble",
        "title": "Pushback over blind compliance",
        "domain_tags": ["meta", "governance", "pushback"],
        "severity": "PUSHBACK",
        "tier": "spirit",
        "instruction": "When a user request conflicts with long-term application health, apply the pushback rule: clarify intent, warn about consequences, and propose a stronger path."
    },

    # ── Workflow Discipline Amendment ─────────────────────────────────────
    {
        "uid": "BCC-WF-A",
        "section": "Workflow Discipline Amendment",
        "subsection": "A",
        "title": "Stable constraint-field rule",
        "domain_tags": ["meta", "continuity", "governance"],
        "severity": "HARD_BLOCK",
        "tier": "spirit",
        "instruction": "Preserve and work within the active constraint field (contract, doctrine, journal records, tranche boundaries, non-goals). Do not discard these because a new prompt begins."
    },
    {
        "uid": "BCC-WF-B",
        "section": "Workflow Discipline Amendment",
        "subsection": "B",
        "title": "Tranche-boundary rule",
        "domain_tags": ["meta", "planning", "scope"],
        "severity": "PUSHBACK",
        "tier": "spirit",
        "instruction": "Execute work in bounded tranches. Before substantial implementation, identify the current scope, what is out of scope, and what constitutes a clean completion point."
    },
    {
        "uid": "BCC-WF-C",
        "section": "Workflow Discipline Amendment",
        "subsection": "C",
        "title": "Phase-separation rule",
        "domain_tags": ["meta", "planning", "scope"],
        "severity": "PUSHBACK",
        "tier": "spirit",
        "instruction": "Preserve distinctions between scaffold work, implementation work, integration work, cleanup work, and polish. Do not silently collapse these phases into one pass."
    },
    {
        "uid": "BCC-WF-D",
        "section": "Workflow Discipline Amendment",
        "subsection": "D",
        "title": "Explicit non-goal rule",
        "domain_tags": ["meta", "scope"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Each tranche should carry explicit non-goals. Treat non-goals as active constraints. Prefer leaving a deferred area untouched over partially expanding it."
    },
    {
        "uid": "BCC-WF-E",
        "section": "Workflow Discipline Amendment",
        "subsection": "E",
        "title": "Owner-first decomposition rule",
        "domain_tags": ["ownership", "structure", "refactoring"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "When refactoring, move behavior to the most natural owner. If no natural owner exists, prefer leaving behavior in place over inventing a vague new layer or premature abstraction."
    },
    {
        "uid": "BCC-WF-F",
        "section": "Workflow Discipline Amendment",
        "subsection": "F",
        "title": "Truth-layer separation rule",
        "domain_tags": ["structure", "data", "ownership"],
        "severity": "PUSHBACK",
        "tier": "spirit",
        "instruction": "Preserve distinctions between builder-memory truth, design/configuration truth, and runtime-consumed truth. Do not blur these layers in storage or implementation."
    },
    {
        "uid": "BCC-WF-G",
        "section": "Workflow Discipline Amendment",
        "subsection": "G",
        "title": "Review-loop sharpening rule",
        "domain_tags": ["meta", "continuity", "review"],
        "severity": "ADVISORY",
        "tier": "spirit",
        "instruction": "Use review findings and successful workflow patterns to sharpen doctrine and constraints for future tranches."
    },
    {
        "uid": "BCC-WF-H",
        "section": "Workflow Discipline Amendment",
        "subsection": "H",
        "title": "Continuity rule",
        "domain_tags": ["meta", "continuity"],
        "severity": "PUSHBACK",
        "tier": "spirit",
        "instruction": "Prefer continuity across sessions. When a guardrail or discipline proves repeatedly useful, record it into durable builder-memory or contract surfaces."
    },

    # ── Required Documentation ────────────────────────────────────────────
    {
        "uid": "BCC-DOC-1",
        "section": "Required Project Documentation",
        "title": "Minimal documentation set",
        "domain_tags": ["docs", "structure"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Maintain a minimal but sufficient documentation set under _docs/. Required: ARCHITECTURE.md (blueprint/design), _AppJOURNAL/ + _journalDB/ (operational memory). Recommended: SOURCE_PROVENANCE.md, TOOLS.md, TESTING.md, MIGRATION.md when warranted."
    },
    {
        "uid": "BCC-DOC-2",
        "section": "Required Project Documentation",
        "title": "No documentation theater",
        "domain_tags": ["docs", "quality"],
        "severity": "ADVISORY",
        "tier": "letter",
        "instruction": "Documents should exist because they preserve continuity, reduce ambiguity, or improve maintainability. Do not create documentation for theater or bureaucratic bulk."
    },

    # ── 1. Mission ────────────────────────────────────────────────────────
    {
        "uid": "BCC-1.0",
        "section": "1. Mission",
        "title": "Build self-contained application per blueprint",
        "domain_tags": ["meta", "governance", "structure"],
        "severity": "HARD_BLOCK",
        "tier": "spirit",
        "instruction": "Build a fully self-contained application inside the target project root according to the user's blueprint and scaffold. Do not invent a new architecture when one has been provided."
    },
    {
        "uid": "BCC-1.1",
        "section": "1. Mission",
        "title": "Prefer original implementation",
        "domain_tags": ["sourcing", "quality"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Prefer original implementation over borrowed logic. Borrowed logic is disallowed by default and may only be used under strict exception conditions: behavior cannot be feasibly rewritten, logic is functionally necessary, rewrite risks correctness, borrowed material can be re-homed, provenance is recorded, and no lighter extraction suffices."
    },

    # ── 2. Root Boundary Rules ────────────────────────────────────────────
    {
        "uid": "BCC-2.0",
        "section": "2. Root Boundary Rules",
        "title": "Confined to project root",
        "domain_tags": ["boundary", "structure"],
        "severity": "HARD_BLOCK",
        "tier": "gate",
        "instruction": "The builder is confined to the current project root folder and its subfolders. Everything inside is the build domain. Writing outside is prohibited unless explicitly authorized."
    },
    {
        "uid": "BCC-2.1",
        "section": "2. Root Boundary Rules",
        "subsection": "2.1",
        "title": "Canonical project structure",
        "domain_tags": ["structure", "ui", "core"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Canonical structure: src/app.py (entry point, app state), src/ui/ (UI code), src/core/ (engine/backend), _docs/ (all project docs except README.md and LICENSE.md). Root: README.md, LICENSE.md, requirements.txt, setup_env.bat, run.bat."
    },
    {
        "uid": "BCC-2.2",
        "section": "2. Root Boundary Rules",
        "subsection": "2.2",
        "title": "Documentation boundary",
        "domain_tags": ["docs", "boundary", "structure"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "All project documents other than README.md and LICENSE.md live under _docs/. Do not place junk, scratch debris, or undocumented clutter there."
    },
    {
        "uid": "BCC-2.3",
        "section": "2. Root Boundary Rules",
        "subsection": "2.3",
        "title": "App journal rules",
        "domain_tags": ["docs", "journal", "continuity"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Maintain the app journal as an append-only development record. Record what changed, why, and notable decisions after each meaningful phase. Do not delete prior entries. Overwrite only when user explicitly instructs."
    },
    {
        "uid": "BCC-2.4",
        "section": "2. Root Boundary Rules",
        "subsection": "2.4",
        "title": "External boundary restrictions",
        "domain_tags": ["boundary", "dependency", "vendoring"],
        "severity": "HARD_BLOCK",
        "tier": "gate",
        "instruction": "The project is self-contained and vendorable. No runtime connection to sibling apps, external project folders, or adjacent repositories. No runtime imports, symlinks, or file-path dependencies outside the project root."
    },
    {
        "uid": "BCC-2.5",
        "section": "2. Root Boundary Rules",
        "subsection": "2.5",
        "title": "Environmental dependency rule",
        "domain_tags": ["dependency", "vendoring"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "The project may assume only normal environmental prerequisites (Python, OS, declared package dependencies). Avoid unnecessary external dependencies or coupling to other apps."
    },

    # ── 3. Required Project Layout ────────────────────────────────────────
    {
        "uid": "BCC-3.0",
        "section": "3. Required Project Layout",
        "title": "Core scaffold is mandatory",
        "domain_tags": ["structure", "ui", "core"],
        "severity": "HARD_BLOCK",
        "tier": "letter",
        "instruction": "Required core structure: src/app.py, src/ui/, src/core/. These ensure the application clusters around entry/state, user interface, and backend/engine."
    },
    {
        "uid": "BCC-3.1",
        "section": "3. Required Project Layout",
        "subsection": "3.1",
        "title": "Scaffold intent",
        "domain_tags": ["structure"],
        "severity": "ADVISORY",
        "tier": "spirit",
        "instruction": "The scaffold provides enough structure for understandable logical groupings without inventing new project geometry. Preserve clarity, strong grouping, easy inspection, and stable extension."
    },
    {
        "uid": "BCC-3.2",
        "section": "3. Required Project Layout",
        "subsection": "3.2",
        "title": "Approved top-level folders",
        "domain_tags": ["structure"],
        "severity": "ADVISORY",
        "tier": "letter",
        "instruction": "Pre-approved top-level folders: tests/, assets/, logs/, data/, scripts/, config/. Create only those warranted by real project needs."
    },
    {
        "uid": "BCC-3.3",
        "section": "3. Required Project Layout",
        "subsection": "3.3",
        "title": "New top-level folder justification",
        "domain_tags": ["structure"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "A new top-level folder is a structural decision, not casual convenience. Justified only when the responsibility does not fit existing areas, placing it there would reduce clarity, and the new folder provides a stable domain boundary."
    },
    {
        "uid": "BCC-3.4",
        "section": "3. Required Project Layout",
        "subsection": "3.4",
        "title": "Build in place preference",
        "domain_tags": ["structure", "scaffold"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "When the user has created the scaffold, build directly into it. Scaffold instantiation is not license to redesign the project layout."
    },
    {
        "uid": "BCC-3.5",
        "section": "3. Required Project Layout",
        "subsection": "3.5",
        "title": "Expansion rule",
        "domain_tags": ["structure", "scaffold"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "The scaffold may be extended conservatively. Entry remains entry, UI remains UI, core remains core. New areas must remain legible as logical systems, not ad hoc accumulation."
    },

    # ── 4. Ownership Rules ────────────────────────────────────────────────
    {
        "uid": "BCC-4.1",
        "section": "4. Ownership Rules",
        "subsection": "4.1",
        "title": "Single-domain rule",
        "domain_tags": ["ownership", "structure", "ui", "core"],
        "severity": "HARD_BLOCK",
        "tier": "letter",
        "instruction": "Logic components are single-domain by default. A component owns one clear domain of responsibility. No mixing UI + business logic, storage + rendering, or orchestration + deep domain implementation in the same component."
    },
    {
        "uid": "BCC-4.2",
        "section": "4. Ownership Rules",
        "subsection": "4.2",
        "title": "Ownership clarity requirement",
        "domain_tags": ["ownership", "structure"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "If you cannot clearly state a component's domain owner, it is not correctly placed. Split it, relocate it, or defer until ownership can be resolved. Do not hide unresolved ownership in catch-all files."
    },
    {
        "uid": "BCC-4.3",
        "section": "4. Ownership Rules",
        "subsection": "4.3",
        "title": "Manager layer rule",
        "domain_tags": ["ownership", "structure", "coordination"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Managers may bridge normally 2 domains, at most 3 when tightly justified. Managers coordinate, they do not absorb full implementation logic of the domains they bridge."
    },
    {
        "uid": "BCC-4.4",
        "section": "4. Ownership Rules",
        "subsection": "4.4",
        "title": "Orchestrator rule",
        "domain_tags": ["ownership", "structure", "ui", "core", "coordination"],
        "severity": "HARD_BLOCK",
        "tier": "letter",
        "instruction": "Orchestrators are strictly bound to either UI side or CORE side. No free-floating orchestrators mixing UI and CORE ownership into one control surface."
    },
    {
        "uid": "BCC-4.5",
        "section": "4. Ownership Rules",
        "subsection": "4.5",
        "title": "File and module placement rule",
        "domain_tags": ["ownership", "structure", "ui", "core"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Place files according to ownership and hierarchy. UI-owned files in src/ui/, CORE-owned in src/core/, root ops at project root, docs under _docs/. Directory placement, ownership, and architectural role must agree."
    },
    {
        "uid": "BCC-4.6",
        "section": "4. Ownership Rules",
        "subsection": "4.6",
        "title": "Adapters and bridges",
        "domain_tags": ["ownership", "structure"],
        "severity": "ADVISORY",
        "tier": "letter",
        "instruction": "Adapters and bridges are not permanent ownership excuses. Temporary bridges must remain narrow and explicitly transitional."
    },
    {
        "uid": "BCC-4.7",
        "section": "4. Ownership Rules",
        "subsection": "4.7",
        "title": "General ownership principle",
        "domain_tags": ["ownership"],
        "severity": "PUSHBACK",
        "tier": "spirit",
        "instruction": "The ownership test: a component belongs to one domain, a manager coordinates a small cluster of adjacent domains, an orchestrator is bounded to UI or CORE. Anything broader is a structural warning."
    },

    # ── 5. Dependency Rules ───────────────────────────────────────────────
    {
        "uid": "BCC-5.1",
        "section": "5. Dependency Rules",
        "subsection": "5.1",
        "title": "Composition root rule",
        "domain_tags": ["dependency", "structure", "core"],
        "severity": "HARD_BLOCK",
        "tier": "letter",
        "instruction": "src/app.py is the composition root and canonical app-state authority. It bootstraps the runtime, registers orchestrators, and monitors lifecycle. Do not create competing top-level state authorities without explicit approval."
    },
    {
        "uid": "BCC-5.2",
        "section": "5. Dependency Rules",
        "subsection": "5.2",
        "title": "Runtime control graph model",
        "domain_tags": ["dependency", "structure", "coordination"],
        "severity": "ADVISORY",
        "tier": "spirit",
        "instruction": "A lean runtime graph is approved as an architectural substrate: declared node identity, bounded routing, controlled message traversal, isolated local state, root-owned global state, append-only event logging. It is a control graph, not an excuse for uncontrolled shared mutation."
    },
    {
        "uid": "BCC-5.5",
        "section": "5. Dependency Rules",
        "subsection": "5.5",
        "title": "Message traversal rule",
        "domain_tags": ["dependency", "coordination"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Prefer explicit message traversal over arbitrary node-to-node mutation or hidden side-channel coupling. Message routes must be declared or permitted by the graph authority."
    },
    {
        "uid": "BCC-5.6",
        "section": "5. Dependency Rules",
        "subsection": "5.6",
        "title": "Event ledger rule",
        "domain_tags": ["dependency", "data", "logging"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Append-only SQLite event ledger is approved for dispatch history, tracing, and debugging. Do not falsely represent append-only logging as full event sourcing unless replay, reconstruction, snapshotting, and reducers are actually implemented."
    },
    {
        "uid": "BCC-5.7",
        "section": "5. Dependency Rules",
        "subsection": "5.7",
        "title": "Layered routing rule",
        "domain_tags": ["dependency", "structure", "coordination"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Dependency flow follows the hierarchy: app.py -> orchestrators -> managers -> owned parts. Lower-level parts do not reach upward or sideways outside approved routes."
    },
    {
        "uid": "BCC-5.9",
        "section": "5. Dependency Rules",
        "subsection": "5.9",
        "title": "Practical prototype caveat",
        "domain_tags": ["dependency", "structure"],
        "severity": "ADVISORY",
        "tier": "spirit",
        "instruction": "The runtime graph prototype is lean but partial. If evolving it further, later define: mutation authority, state-slice ownership, replay semantics, snapshotting, sync/async boundaries, error semantics, schema versioning."
    },

    # ── 6. Safe Sourcing / Extraction Rules ───────────────────────────────
    {
        "uid": "BCC-6.1",
        "section": "6. Safe Sourcing Rules",
        "subsection": "6.1",
        "title": "Sandbox workspace model",
        "domain_tags": ["boundary", "sourcing"],
        "severity": "HARD_BLOCK",
        "tier": "letter",
        "instruction": "The current project folder is the only authorized write domain. The builder may inspect approved reference locations in the sandbox but shall write only inside the current project."
    },
    {
        "uid": "BCC-6.2",
        "section": "6. Safe Sourcing Rules",
        "subsection": "6.2",
        "title": "Approved reference sources",
        "domain_tags": ["sourcing", "boundary"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Approved reference sources: _PARTS/ (prior projects/logic fragments), _dev_tools/ (local dev tools), and _docs/ within the current project. Treat as reference, not runtime dependencies."
    },
    {
        "uid": "BCC-6.4",
        "section": "6. Safe Sourcing Rules",
        "subsection": "6.4",
        "title": "Reference-only rule",
        "domain_tags": ["sourcing", "dependency", "boundary"],
        "severity": "HARD_BLOCK",
        "tier": "gate",
        "instruction": "Do not make the project depend on _PARTS/, _dev_tools/, or sibling projects at runtime. No runtime imports, symlinks, or path dependencies to external sources. All borrowed logic must be re-homed."
    },
    {
        "uid": "BCC-6.5",
        "section": "6. Safe Sourcing Rules",
        "subsection": "6.5",
        "title": "Preferred sourcing order",
        "domain_tags": ["sourcing", "quality"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Sourcing preference order: (1) original implementation, (2) bounded rewrite informed by reference, (3) narrow structured extraction of smallest viable hunk, (4) larger transplant only under strict exception conditions."
    },
    {
        "uid": "BCC-6.6",
        "section": "6. Safe Sourcing Rules",
        "subsection": "6.6",
        "title": "Bounded extraction rule",
        "domain_tags": ["sourcing"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "When extracting reference logic, copy only structured hunks: clear ownership, necessary purpose, bounded size, capable of re-homing. Avoid pulling excess surrounding code or dependency chains."
    },
    {
        "uid": "BCC-6.8",
        "section": "6. Safe Sourcing Rules",
        "subsection": "6.8",
        "title": "Re-homing and cleanup rule",
        "domain_tags": ["sourcing", "quality", "ownership"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Borrowed logic must be re-homed into the local project, placed by ownership, renamed to fit the scaffold, cleaned of debris, stripped of old-environment coupling, and brought into contract compliance."
    },
    {
        "uid": "BCC-6.9",
        "section": "6. Safe Sourcing Rules",
        "subsection": "6.9",
        "title": "Provenance recording rule",
        "domain_tags": ["sourcing", "docs"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "When logic is extracted or transplanted from reference sources, record provenance in _docs/: source location, borrowed unit, destination owner, reason, whether rewritten/extracted/transplanted, and cleanup performed."
    },
    {
        "uid": "BCC-6.10",
        "section": "6. Safe Sourcing Rules",
        "subsection": "6.10",
        "title": "Off-limits write rule",
        "domain_tags": ["boundary", "sourcing"],
        "severity": "HARD_BLOCK",
        "tier": "gate",
        "instruction": "Do not modify _PARTS/, _dev_tools/, sibling project folders, or any non-target sandbox contents as part of building the current project."
    },

    # ── 7. Dev Tool Reference Rules ───────────────────────────────────────
    {
        "uid": "BCC-7.1",
        "section": "7. Dev Tool Rules",
        "subsection": "7.1",
        "title": "Approved use of dev tools",
        "domain_tags": ["tools", "sourcing"],
        "severity": "ADVISORY",
        "tier": "letter",
        "instruction": "May inspect dev tools for reference, use them during development, copy logic that complies with ownership/dependency/sourcing rules, and derive new local tools. Do not treat _dev_tools/ as a permanent runtime dependency."
    },
    {
        "uid": "BCC-7.2",
        "section": "7. Dev Tool Rules",
        "subsection": "7.2",
        "title": "Copy/transplant rule for dev tools",
        "domain_tags": ["tools", "sourcing", "ownership"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Logic from _dev_tools/ may be copied only when compliant with project rules. Must be re-homed, fit the scaffold, obey ownership, avoid hidden dependency on original tool environment."
    },
    {
        "uid": "BCC-7.3",
        "section": "7. Dev Tool Rules",
        "subsection": "7.3",
        "title": "Tool-building encouragement",
        "domain_tags": ["tools", "quality"],
        "severity": "ADVISORY",
        "tier": "spirit",
        "instruction": "Create new local tools when doing so improves token efficiency, reduces repeated manual work, or makes recurring operations more reliable. Token awareness should drive the decision."
    },
    {
        "uid": "BCC-7.4",
        "section": "7. Dev Tool Rules",
        "subsection": "7.4",
        "title": "CLI accessibility rule",
        "domain_tags": ["tools"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Any newly created reusable tool shall provide command-line access so any agent can invoke it consistently."
    },
    {
        "uid": "BCC-7.5",
        "section": "7. Dev Tool Rules",
        "subsection": "7.5",
        "title": "Project-local effect rule",
        "domain_tags": ["tools", "boundary"],
        "severity": "HARD_BLOCK",
        "tier": "gate",
        "instruction": "Tools shall have effects confined to the current project folder unless the user explicitly authorizes wider scope."
    },
    {
        "uid": "BCC-7.8",
        "section": "7. Dev Tool Rules",
        "subsection": "7.8",
        "title": "Documentation rule for project tools",
        "domain_tags": ["tools", "docs"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "When creating or incorporating a dev tool, document it under _docs/ and append a journal entry: purpose, scope of effect, CLI entry pattern, model/runtime assumptions, and operational constraints."
    },
    {
        "uid": "BCC-7.9",
        "section": "7. Dev Tool Rules",
        "subsection": "7.9",
        "title": "Tool legacy / shared utility rule",
        "domain_tags": ["tools", "boundary"],
        "severity": "ADVISORY",
        "tier": "letter",
        "instruction": "If a tool is useful beyond the immediate project, it may be placed in sandbox _dev_tools/ for future agents. This is a narrow exception to the write boundary, not license for broad sandbox changes. Tools must be clearly marked with enough metadata for another agent to discover and invoke them."
    },
    {
        "uid": "BCC-7.10",
        "section": "7. Dev Tool Rules",
        "subsection": "7.10",
        "title": "Same-core-rules principle",
        "domain_tags": ["tools", "governance"],
        "severity": "PUSHBACK",
        "tier": "spirit",
        "instruction": "_dev_tools/ is not exempt from the project's core architectural rules. All logic derived from it remains subject to boundary, ownership, dependency, sourcing, quality, and prohibited behavior rules."
    },

    # ── 8. Support File Proposal Rules ────────────────────────────────────
    {
        "uid": "BCC-8.1",
        "section": "8. Support File Rules",
        "subsection": "8.1",
        "title": "General creation rule",
        "domain_tags": ["structure", "ownership"],
        "severity": "ADVISORY",
        "tier": "letter",
        "instruction": "Create support files or folders when they serve a real structural need and align with ownership/hierarchy/dependency/boundary rules. Do not avoid creating a needed file merely to appear minimal."
    },
    {
        "uid": "BCC-8.2",
        "section": "8. Support File Rules",
        "subsection": "8.2",
        "title": "Balance rule",
        "domain_tags": ["structure", "quality"],
        "severity": "ADVISORY",
        "tier": "spirit",
        "instruction": "Files should balance minimality, non-fragility, cleanliness, efficiency, and clarity to other agents. Do not pursue extreme minimalism when it causes brittleness, nor excessive decomposition when it creates sprawl."
    },
    {
        "uid": "BCC-8.5",
        "section": "8. Support File Rules",
        "subsection": "8.5",
        "title": "Temporary and dead-file cleanup",
        "domain_tags": ["cleanup", "structure"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Active duty to clean up temporary, unused, obsolete, and scratch files when safe. Cleanup must be conservative. When uncertain, preserve the file or record the cleanup candidate in documentation rather than risk erroneous deletion."
    },
    {
        "uid": "BCC-8.6",
        "section": "8. Support File Rules",
        "subsection": "8.6",
        "title": "No-error-prune rule",
        "domain_tags": ["cleanup"],
        "severity": "HARD_BLOCK",
        "tier": "gate",
        "instruction": "Nothing shall be pruned by accident. Before deleting, verify: the item is temporary/obsolete/unused/replaced, removing it will not break the project, and the deletion aligns with user intent."
    },

    # ── 9. Code Quality Rules ─────────────────────────────────────────────
    {
        "uid": "BCC-9.1",
        "section": "9. Code Quality Rules",
        "subsection": "9.1",
        "title": "Logging instead of print",
        "domain_tags": ["quality", "logging"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "No print()-based debugging or operational output in the application. Use proper logging. print() only in narrowly justified one-off tooling or throwaway contexts."
    },
    {
        "uid": "BCC-9.2",
        "section": "9. Code Quality Rules",
        "subsection": "9.2",
        "title": "Full logging rule",
        "domain_tags": ["quality", "logging"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Implement full logging: startup/shutdown, lifecycle transitions, orchestration actions, manager events, errors/warnings, meaningful state changes, tool execution, and cleanup actions. Structured and useful, not noisy spam."
    },
    {
        "uid": "BCC-9.3",
        "section": "9. Code Quality Rules",
        "subsection": "9.3",
        "title": "Graceful failure rule",
        "domain_tags": ["quality", "error-handling"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Failures happen gracefully: clear exception handling, meaningful logs, diagnostic preservation, safe shutdown paths, no corruption of state or files."
    },
    {
        "uid": "BCC-9.4",
        "section": "9. Code Quality Rules",
        "subsection": "9.4",
        "title": "Testing and task-checklist rule",
        "domain_tags": ["quality", "testing"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Use robust testing to verify meaningful logic. Use task checklists to track interruptible work. Especially important in token-limited workflows where interruptions are realistic."
    },
    {
        "uid": "BCC-9.5",
        "section": "9. Code Quality Rules",
        "subsection": "9.5",
        "title": "Central configuration rule",
        "domain_tags": ["quality", "structure", "data"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Centralize configuration. Prefer a clear central config model over scattered ad hoc settings. Configuration values should be discoverable, intentionally owned, and easy to inspect."
    },
    {
        "uid": "BCC-9.6",
        "section": "9. Code Quality Rules",
        "subsection": "9.6",
        "title": "No hidden globals or magic constants",
        "domain_tags": ["quality"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Avoid hidden globals and unexplained magic constants. Constants should be named, owned, and placed where their role is legible. If a constant affects behavior, make it explicit."
    },
    {
        "uid": "BCC-9.7",
        "section": "9. Code Quality Rules",
        "subsection": "9.7",
        "title": "Type and schema discipline",
        "domain_tags": ["quality"],
        "severity": "ADVISORY",
        "tier": "letter",
        "instruction": "Prefer typed structures where they improve clarity and safety: typed config objects, message envelopes, state slices, dataclasses. Use typing deliberately where structure matters, not as ceremony."
    },
    {
        "uid": "BCC-9.9",
        "section": "9. Code Quality Rules",
        "subsection": "9.9",
        "title": "Structural quality principle",
        "domain_tags": ["quality", "ownership", "structure"],
        "severity": "PUSHBACK",
        "tier": "spirit",
        "instruction": "Code quality includes: ownership clarity, stable file placement, clean routing, explicit state handling, safe cleanup, testability, recoverability after interruption, and legibility to future agents."
    },

    # ── 10. Reporting / Phase Output Rules ────────────────────────────────
    {
        "uid": "BCC-10.1",
        "section": "10. Reporting Rules",
        "subsection": "10.1",
        "title": "Journal entry format",
        "domain_tags": ["docs", "journal", "reporting"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Journal entries are date-stamped, time-stamped, with meaningful identifiers. Record: files changed, summary of what changed, relevant implementation notes. Summaries must be concise but complete; no cut-off shorthand."
    },
    {
        "uid": "BCC-10.2",
        "section": "10. Reporting Rules",
        "subsection": "10.2",
        "title": "File-change recording",
        "domain_tags": ["docs", "journal", "reporting"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Record all files changed for each meaningful work phase: created, modified, relocated, or deleted. Another agent should be able to reconstruct what was touched without ambiguity."
    },
    {
        "uid": "BCC-10.5",
        "section": "10. Reporting Rules",
        "subsection": "10.5",
        "title": "Backlog ownership",
        "domain_tags": ["docs", "journal", "planning"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "Unresolved issues, deferred work, next steps, and deferred cleanup belong in the app journal backlog surface. The journal is the operational continuation surface."
    },
    {
        "uid": "BCC-10.8",
        "section": "10. Reporting Rules",
        "subsection": "10.8",
        "title": "Decision priority and pushback rule",
        "domain_tags": ["meta", "governance", "pushback", "quality"],
        "severity": "HARD_BLOCK",
        "tier": "spirit",
        "instruction": "Decision priority: (1) correctness and structural integrity, (2) contract compliance, (3) real user intent, (4) cleanest implementation, (5) token efficiency, (6) surface preferences only when they do not damage the system. If a request is structurally unsound, push back clearly, verify intent, warn about consequences, propose a stronger alternative."
    },

    # ── 11. Prohibited Behaviors ──────────────────────────────────────────
    {
        "uid": "BCC-11.1",
        "section": "11. Prohibited Behaviors",
        "subsection": "11.1",
        "title": "Contract-first prohibition",
        "domain_tags": ["meta", "governance"],
        "severity": "HARD_BLOCK",
        "tier": "spirit",
        "instruction": "If a behavior violates any section of this contract (mission, boundary, ownership, dependency, sourcing, tooling, support-file, quality, or reporting rules), that behavior is prohibited."
    },
    {
        "uid": "BCC-11.2",
        "section": "11. Prohibited Behaviors",
        "subsection": "11.2",
        "title": "Non-listed behavior rule",
        "domain_tags": ["meta", "governance"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "If a behavior is not explicitly authorized by this contract, it requires user approval before proceeding. Silence in the contract is not blanket permission for structural deviation."
    },
    {
        "uid": "BCC-11.3",
        "section": "11. Prohibited Behaviors",
        "subsection": "11.3",
        "title": "Approval gate rule",
        "domain_tags": ["meta", "governance"],
        "severity": "PUSHBACK",
        "tier": "letter",
        "instruction": "When encountering an action not clearly covered by the contract that could materially affect structure, boundaries, dependency, sourcing, or maintainability: pause, surface it, seek user approval."
    },
]

# ---------------------------------------------------------------------------
# Seed Data: Task Profiles
# ---------------------------------------------------------------------------

SEED_PROFILES: list[dict] = [
    {
        "profile_id": "ui_implementation",
        "description": "Agent is writing or modifying UI code under src/ui/.",
        "constraint_uids": [
            "BCC-2.0", "BCC-2.4", "BCC-3.0", "BCC-4.1", "BCC-4.4",
            "BCC-4.5", "BCC-5.7", "BCC-9.1", "BCC-9.3", "BCC-8.6"
        ]
    },
    {
        "profile_id": "core_implementation",
        "description": "Agent is writing or modifying backend/engine code under src/core/.",
        "constraint_uids": [
            "BCC-2.0", "BCC-2.4", "BCC-3.0", "BCC-4.1", "BCC-4.3",
            "BCC-4.4", "BCC-5.1", "BCC-5.7", "BCC-9.1", "BCC-9.3",
            "BCC-9.5", "BCC-9.6"
        ]
    },
    {
        "profile_id": "refactoring",
        "description": "Agent is refactoring, decomposing, or reorganizing existing code.",
        "constraint_uids": [
            "BCC-WF-B", "BCC-WF-C", "BCC-WF-E", "BCC-4.1", "BCC-4.2",
            "BCC-4.5", "BCC-4.7", "BCC-3.5", "BCC-8.5", "BCC-8.6",
            "BCC-9.9", "BCC-10.2"
        ]
    },
    {
        "profile_id": "sourcing_extraction",
        "description": "Agent is borrowing, extracting, or transplanting logic from reference sources.",
        "constraint_uids": [
            "BCC-1.1", "BCC-6.1", "BCC-6.2", "BCC-6.4", "BCC-6.5",
            "BCC-6.6", "BCC-6.8", "BCC-6.9", "BCC-6.10", "BCC-7.1",
            "BCC-7.2"
        ]
    },
    {
        "profile_id": "documentation",
        "description": "Agent is creating or updating project documentation.",
        "constraint_uids": [
            "BCC-DOC-1", "BCC-DOC-2", "BCC-2.2", "BCC-2.3", "BCC-10.1",
            "BCC-10.2", "BCC-10.5"
        ]
    },
    {
        "profile_id": "cleanup",
        "description": "Agent is cleaning up files, removing dead code, or reorganizing.",
        "constraint_uids": [
            "BCC-WF-D", "BCC-8.5", "BCC-8.6", "BCC-10.2", "BCC-10.5",
            "BCC-11.3"
        ]
    },
    {
        "profile_id": "tool_creation",
        "description": "Agent is creating or incorporating development tools.",
        "constraint_uids": [
            "BCC-7.1", "BCC-7.3", "BCC-7.4", "BCC-7.5", "BCC-7.8",
            "BCC-7.9", "BCC-7.10", "BCC-2.0"
        ]
    },
    {
        "profile_id": "scaffolding",
        "description": "Agent is setting up initial project structure or extending the scaffold.",
        "constraint_uids": [
            "BCC-1.0", "BCC-2.1", "BCC-3.0", "BCC-3.1", "BCC-3.2",
            "BCC-3.3", "BCC-3.4", "BCC-3.5", "BCC-DOC-1"
        ]
    },
]


# ---------------------------------------------------------------------------
# Build logic
# ---------------------------------------------------------------------------

def _build_db(db_path: Path, force: bool = False) -> dict:
    """Create and populate the constraint registry database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")

    if force:
        conn.execute("DROP TABLE IF EXISTS constraint_units")
        conn.execute("DROP TABLE IF EXISTS task_profiles")
        conn.execute("DROP TABLE IF EXISTS registry_meta")

    conn.executescript(SCHEMA_SQL)

    # Seed ACUs
    acu_count = 0
    for acu in SEED_ACUS:
        conn.execute(
            """INSERT OR REPLACE INTO constraint_units
               (uid, section, subsection, title, domain_tags, severity, tier, instruction, full_text)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                acu["uid"],
                acu["section"],
                acu.get("subsection", ""),
                acu["title"],
                json.dumps(acu["domain_tags"]),
                acu["severity"],
                acu["tier"],
                acu["instruction"],
                acu.get("full_text", ""),
            ),
        )
        acu_count += 1

    # Seed task profiles
    profile_count = 0
    for prof in SEED_PROFILES:
        conn.execute(
            """INSERT OR REPLACE INTO task_profiles
               (profile_id, description, constraint_uids)
               VALUES (?, ?, ?)""",
            (
                prof["profile_id"],
                prof["description"],
                json.dumps(prof["constraint_uids"]),
            ),
        )
        profile_count += 1

    # Meta
    conn.execute(
        "INSERT OR REPLACE INTO registry_meta (key, value) VALUES (?, ?)",
        ("schema_version", "1.0.0"),
    )
    conn.execute(
        "INSERT OR REPLACE INTO registry_meta (key, value) VALUES (?, ?)",
        ("source_document", "Builder Constraint Contract (BCC)"),
    )

    conn.commit()
    conn.close()

    return {
        "db_path": str(db_path),
        "constraint_units": acu_count,
        "task_profiles": profile_count,
        "severity_counts": {
            "HARD_BLOCK": sum(1 for a in SEED_ACUS if a["severity"] == "HARD_BLOCK"),
            "PUSHBACK": sum(1 for a in SEED_ACUS if a["severity"] == "PUSHBACK"),
            "ADVISORY": sum(1 for a in SEED_ACUS if a["severity"] == "ADVISORY"),
        },
        "tier_counts": {
            "spirit": sum(1 for a in SEED_ACUS if a["tier"] == "spirit"),
            "letter": sum(1 for a in SEED_ACUS if a["tier"] == "letter"),
            "gate": sum(1 for a in SEED_ACUS if a["tier"] == "gate"),
        },
    }


def run(arguments: dict) -> dict:
    db_path = Path(arguments.get("db_path") or (PACKAGE_ROOT / "constraint_registry.sqlite3"))
    force = arguments.get("force", False)

    try:
        stats = _build_db(db_path, force=force)
        return tool_result(FILE_METADATA["tool_name"], arguments, stats)
    except Exception as exc:
        return tool_error(FILE_METADATA["tool_name"], arguments, str(exc))


if __name__ == "__main__":
    standard_main(FILE_METADATA, run)
