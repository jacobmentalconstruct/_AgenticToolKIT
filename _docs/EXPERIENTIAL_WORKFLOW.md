# Experiential Workflow

_Status: active onboarding and collaboration doctrine for the toolbox itself_

This note explains what it feels like to use `.dev-tools` as a living toolbox,
not just a folder full of utilities.

The README, contract, manifests, vendoring guide, and package docs describe the
mechanics. This document describes the rhythm those pieces create when humans
and agents actually use the toolbox across many sessions and many target
projects.

## One-Sentence Summary

We do not use this toolbox as a grab bag of scripts. We use it as a governed
four-surface system where manifests provide orientation, builder tools support
inspection and patching, packages and templates move cleanly into projects, and
documentation keeps the work resumable.

## What This Workflow Is Trying To Prevent

Without a clear regimen, a toolbox like this drifts in predictable ways:

- new sessions guess at what the toolbox contains
- helper code leaks into project runtime by accident
- docs fall behind the actual architecture
- people copy whole folders when only one surface should be vended
- agents read random files instead of orienting from manifests and guides

This workflow exists to stop that.

## The Core Surfaces And What They Do

### 1. README.md: the architectural front door

Role:

- names the four-surface architecture
- shows builder tools, packed authorities, vendable packages, and templates
- provides the primary human overview

Experientially, this is where the toolbox stops looking like a directory tree
and starts looking like a designed system.

### 2. CONTRACT.md: the toolbox's own laws

Role:

- defines the tool contract
- defines the journal contract
- defines the UI contract
- defines the project-local convention created by initialization

Experientially, this is what keeps changes honest. It explains what a valid tool
looks like, how the shared store behaves, and what should remain stable.

### 3. toolbox_manifest.json and tool_manifest.json: fast machine orientation

Role:

- tell a fresh agent what exists
- classify the tiers and tools
- reduce cold-start wandering

Experientially, these manifests are the fastest way for a new agent to recover
the structure of the toolbox without reading half the repo first.

### 4. _docs/AGENT_GUIDE.md: the playbook

Role:

- gives the working loops
- explains tool selection
- explains token economy and verification habits

Experientially, this is where a new builder learns how to move with the
toolbox, not just what files exist inside it.

### 5. VENDORING.md: the trust-boundary guide

Role:

- explains what stays in the toolbox
- explains what moves into target projects
- explains the thin authority shim install path

Experientially, this is one of the most important anti-drift surfaces in the
whole repo. It prevents the “just copy the whole thing over” mistake.

### 6. _docs/DEV_LOG.md: the human-readable memory trail

Role:

- records major changes to the toolbox itself
- explains why the architecture moved
- gives future sessions a concise continuation surface

Experientially, this is the fast “what happened here recently?” document.

### 7. Package and authority readmes: the local deep dives

Role:

- explain a specific vendable package or packed authority
- provide local install, launch, and smoke-test details

Experientially, these are the surfaces you read after you have already decided
which tier you are working in.

## The Real Working Loop

This is the practical collaboration loop the toolbox wants people to follow.

### Step 1: Orient from the top, not from the weeds

For a human:

- open `START_HERE.html`
- read `README.md`
- read `CONTRACT.md` and `VENDORING.md`

For an agent:

- read `toolbox_manifest.json`
- read `tool_manifest.json`
- read `_docs/AGENT_GUIDE.md`

This keeps a new session from spending time rediscovering what the repo already
states clearly.

### Step 2: Choose the right surface

Before writing or copying anything, decide which surface fits the task:

- builder tool
- packed authority
- vendable package
- vendable document

This is where a lot of hidden mess gets avoided. The wrong surface choice
causes coupling, drift, and confusing installs later.

### Step 3: Work inside the trust boundaries

During implementation or onboarding:

- keep builder logic in the toolbox
- keep vendable payloads self-contained
- keep target projects independent after vendoring
- keep docs synced with the real architecture

The important discipline is not only “make it work.” It is “make it work in the
right place.”

### Step 4: Verify before celebrating

The toolbox is not complete because the story sounds good. It is complete when
the relevant verification has happened:

- `python src/smoke_test.py`
- package-local `smoke_test.py`
- manifest review
- launch-path checks
- install-path checks

Experientially, this matters because a toolbox is mostly leverage. Broken
leverage spreads confusion quickly.

### Step 5: Leave the next session a clean return path

When meaningful work lands:

- update `README.md` if the architecture or entry story changed
- update `VENDORING.md` if the install story changed
- update `_docs/DEV_LOG.md` with the why behind the change
- add or refresh guide surfaces when the onboarding story changes

That is how the toolbox stays teachable over time.

## Why The Microsite Matters

This repo now includes an offline onboarding microsite because the first
experience matters.

If someone can open one file and understand:

1. what this toolbox is
2. how the four surfaces differ
3. what to read next
4. how humans and agents stay in sync
5. how vendoring avoids hidden dependency drift

then the deeper docs become much easier to trust and use.

The microsite is not a separate truth surface. It is a friendlier entrance into
the truth surfaces that already live in the repo.

## The Human-Agent Relationship In Practice

This toolbox works best when:

- the human supplies intent, scope, and judgment
- the agent supplies structured orientation, execution, and verification
- the docs carry continuity across pauses
- the manifests reduce rediscovery cost

In plain language:

- the human says what matters
- the toolbox says what exists
- the agent chooses the right path
- the docs make the result resumable

## Short Version

The workflow works because the toolbox gives long-running collaboration five
things at once:

- a clear front door
- stable boundaries
- reusable capabilities
- verification paths
- continuity surfaces

That is what turns `.dev-tools` from “helpful files” into a real toolbox.
