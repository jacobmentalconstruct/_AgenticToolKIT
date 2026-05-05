# Builder Constraint Contract (BCC)
### *Architectural Governance for Local AI Co-Development*

## 🚀 Why This Matters (The "Why It Rocks" Factor)
Most AI-driven coding projects suffer from "Context Drift"—a slow degradation where the AI loses the plot, starts hallucinating dependencies, or turns your clean architecture into a "spaghetti-code" junk drawer.

The **Builder Constraint Contract** is my solution. It’s a governing discipline that transforms an LLM from a "helpful assistant" into a **Disciplined Lead Developer**.

### 🛠 Key Power Features:
*   **The Zero-Drift Mandate:** By enforcing a strict *Constraint Field*, the AI is legally (via prompt logic) barred from treating every turn as a "new universe." It respects the history, the journal, and the pre-defined project laws.
*   **True Vendorability:** Every project is built as a self-contained unit. No "hidden coupling" to external folders or sibling projects. If you move the folder, the app *still works*[cite: 1].
*   **The Composition Root Spine:** It anchors the entire runtime state in `src/app.py`, using a bounded control graph that makes debugging a breeze and state-tracking immutable[cite: 1].
*   **Human-in-the-Loop "Pushback":** The contract explicitly grants the AI permission to say "No." If a user request threatens the long-term health of the app, the AI is required to provide technical pushback and propose a stronger path[cite: 1].
*   **The App Journal (Persistent Memory):** An append-only SQLite ledger that acts as the "black box" flight recorder for the project, ensuring continuity even if you reset the AI's context window[cite: 1].

## 🎨 Creative Engineering
As a graphic designer and artist, I treat code like a composition. Structure is everything. The BCC ensures that:
1.  **UI remains UI** (cleanly isolated in `src/ui/`)[cite: 1].
2.  **Core remains Core** (engine logic is never muddied by interface concerns)[cite: 1].
3.  **Ownership is absolute** (if a component's domain can't be stated in one sentence, it’s refactored)[cite: 1].

---

## 🛑 Important: Read-Only Example
**This is a conceptual blueprint shared for educational study.**

This repository is an example of a "Lead Developer" prompt strategy. To encourage the development of unique, project-specific governance, this contract is provided under a **Non-Automated Use License**. 

*   **You MAY:** Study these patterns to build your own "System Instructions."
*   **You MAY NOT:** Directly ingest this file into an AI System's "System Prompt" or "Knowledge Base" for the purpose of automated project execution. 

*Make your own laws. Own your own architecture.*

---
*Created by the .dev-tools maintainer*
