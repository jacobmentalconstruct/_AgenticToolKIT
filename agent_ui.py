"""Desktop operator UI for the local sidecar agent and toolbox tools."""

from __future__ import annotations

import argparse
import json
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lib.operator_ui_support import (  # noqa: E402
    agent_payload,
    agent_recovery_status,
    apply_recovery_decision,
    choose_model,
    default_input_from_schema,
    dispatch_tool,
    format_json,
    is_mutating_tool,
    load_tool_metadata,
    recovery_decisions,
    sanitize_path_text,
    tool_index,
)
from tools.local_sidecar_agent import DEFAULT_ALLOWED_TOOLS  # noqa: E402


THEME = {
    "bg": "#171a1f",
    "panel": "#1d2128",
    "field": "#22262d",
    "fg": "#e8edf5",
    "muted": "#8c97a6",
    "accent": "#35507a",
    "accent_hover": "#4a6a9a",
    "success": "#86efac",
    "warning": "#fbbf24",
    "error": "#f87171",
    "button": "#2a3140",
    "button_hover": "#35507a",
    "border": "#334155",
}

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI Semibold", 10)
FONT_HEADING = ("Segoe UI Semibold", 14)
FONT_MONO = ("Consolas", 9)


def apply_theme(root: tk.Tk) -> None:
    root.configure(bg=THEME["bg"])
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(".", background=THEME["bg"], foreground=THEME["fg"], fieldbackground=THEME["field"], font=FONT)
    style.configure("TFrame", background=THEME["bg"])
    style.configure("Panel.TFrame", background=THEME["panel"])
    style.configure("TLabel", background=THEME["bg"], foreground=THEME["fg"], font=FONT)
    style.configure("Panel.TLabel", background=THEME["panel"], foreground=THEME["fg"], font=FONT)
    style.configure("Heading.TLabel", background=THEME["bg"], foreground=THEME["fg"], font=FONT_HEADING)
    style.configure("Muted.TLabel", background=THEME["bg"], foreground=THEME["muted"], font=FONT)
    style.configure("TButton", background=THEME["button"], foreground=THEME["fg"], padding=(10, 5), font=FONT)
    style.map("TButton", background=[("active", THEME["button_hover"])])
    style.configure("Accent.TButton", background=THEME["accent"], foreground="#ffffff", padding=(14, 6), font=FONT_BOLD)
    style.map("Accent.TButton", background=[("active", THEME["accent_hover"])])
    style.configure("TEntry", fieldbackground=THEME["field"], foreground=THEME["fg"], insertcolor=THEME["fg"], font=FONT)
    style.configure("TCheckbutton", background=THEME["bg"], foreground=THEME["fg"], font=FONT)
    style.map("TCheckbutton", background=[("active", THEME["bg"])])
    style.configure("TCombobox", fieldbackground=THEME["field"], foreground=THEME["fg"], font=FONT)
    style.configure("TNotebook", background=THEME["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=THEME["button"], foreground=THEME["fg"], padding=(12, 6))
    style.map("TNotebook.Tab", background=[("selected", THEME["accent"])])


class OperatorUI:
    def __init__(self, root: tk.Tk, toolbox_root: Path) -> None:
        self.root = root
        self.toolbox_root = toolbox_root
        self.project_root_path = str(toolbox_root)
        self.tools = tool_index(toolbox_root)
        self.tool_metadata: dict[str, dict[str, Any]] = {}
        self.model_names: list[str] = []
        self.last_agent_payload: dict[str, Any] = {}
        self.last_agent_result: dict[str, Any] = {}
        self.agent_running = False
        self.agent_started_at = 0.0

        self.root.title(".dev-tools Agent Operator")
        self.root.geometry("1060x760")
        self.root.minsize(860, 620)
        apply_theme(self.root)
        self._build()

    def _build(self) -> None:
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main, text=".dev-tools Agent Operator", style="Heading.TLabel").pack(anchor=tk.W)
        ttk.Label(
            main,
            text="Run the guarded local agent and test toolbox tools without raw terminal parity.",
            style="Muted.TLabel",
        ).pack(anchor=tk.W, pady=(2, 10))

        notebook = ttk.Notebook(main)
        notebook.pack(fill=tk.BOTH, expand=True)
        self.agent_tab = ttk.Frame(notebook, padding=12)
        self.tool_tab = ttk.Frame(notebook, padding=12)
        self.evidence_tab = ttk.Frame(notebook, padding=12)
        self.teaching_tab = ttk.Frame(notebook, padding=12)
        notebook.add(self.agent_tab, text="Agent Console")
        notebook.add(self.tool_tab, text="Tool Lab")
        notebook.add(self.evidence_tab, text="Evidence Shelf")
        notebook.add(self.teaching_tab, text="Teaching Lab")
        self._build_agent_tab()
        self._build_tool_tab()
        self._build_evidence_tab()
        self._build_teaching_tab()

    def _build_agent_tab(self) -> None:
        left = ttk.Frame(self.agent_tab)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        right = ttk.Frame(self.agent_tab)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.project_var = tk.StringVar(value=sanitize_path_text(str(self.toolbox_root), toolbox_root=self.toolbox_root))
        self.base_url_var = tk.StringVar(value="http://localhost:11434")
        self.planner_model_var = tk.StringVar()
        self.response_model_var = tk.StringVar()
        self.recovery_model_var = tk.StringVar()
        self.timeout_var = tk.StringVar(value="60")
        self.rounds_var = tk.StringVar(value="4")
        self.session_id_var = tk.StringVar(value="default")
        self.window_turns_var = tk.StringVar(value="8")
        self.confirm_mutations_var = tk.BooleanVar(value=False)
        self.confirm_checkpoint_var = tk.BooleanVar(value=False)
        self.confirm_evidence_var = tk.BooleanVar(value=False)
        self.heartbeat_var = tk.BooleanVar(value=True)
        self.recovery_model_enabled_var = tk.BooleanVar(value=False)
        self.planning_workspace_var = tk.BooleanVar(value=False)
        self.checkpoint_var = tk.BooleanVar(value=True)
        self.use_evidence_var = tk.BooleanVar(value=True)
        self.claim_enforcement_var = tk.StringVar(value="warn")
        self.recovery_decision_var = tk.StringVar()
        self.agent_status_var = tk.StringVar(value="Refresh models to enable agent runs.")
        self.allowed_tool_vars: dict[str, tk.BooleanVar] = {}

        self._field_with_browse(left, "Project root", self.project_var, self._browse_project)
        self._entry(left, "Ollama base URL", self.base_url_var)
        model_row = ttk.Frame(left)
        model_row.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(model_row, text="Refresh Models", command=self._refresh_models).pack(side=tk.LEFT)
        ttk.Button(model_row, text="Status", command=self._agent_status).pack(side=tk.LEFT, padx=(8, 0))
        self._combo(left, "Planner model", self.planner_model_var)
        self.planner_combo = self._last_combo
        self._combo(left, "Response model", self.response_model_var)
        self.response_combo = self._last_combo
        self._combo(left, "Recovery model", self.recovery_model_var)
        self.recovery_combo = self._last_combo
        self._entry(left, "Timeout seconds", self.timeout_var)
        self._entry(left, "Max tool rounds", self.rounds_var)
        self._entry(left, "Session ID", self.session_id_var)
        self._entry(left, "Evidence window turns", self.window_turns_var)
        self._combo(left, "Claim enforcement", self.claim_enforcement_var)
        self.claim_combo = self._last_combo
        self.claim_combo.configure(values=["warn", "require_citation"])
        ttk.Checkbutton(left, text="Confirm mutations", variable=self.confirm_mutations_var).pack(anchor=tk.W, pady=(4, 0))
        ttk.Checkbutton(left, text="Confirm checkpoint", variable=self.confirm_checkpoint_var).pack(anchor=tk.W)
        ttk.Checkbutton(left, text="Confirm evidence archive", variable=self.confirm_evidence_var).pack(anchor=tk.W)
        ttk.Checkbutton(left, text="Heartbeat while running", variable=self.heartbeat_var).pack(anchor=tk.W)
        ttk.Checkbutton(left, text="Use recovery model advice", variable=self.recovery_model_enabled_var).pack(anchor=tk.W)
        ttk.Checkbutton(left, text="Plan in runtime workspace", variable=self.planning_workspace_var).pack(anchor=tk.W)
        ttk.Checkbutton(left, text="Checkpoint after run", variable=self.checkpoint_var).pack(anchor=tk.W)
        ttk.Checkbutton(left, text="Use Evidence Shelf", variable=self.use_evidence_var).pack(anchor=tk.W)

        ttk.Label(left, text="Allowed agent tools", style="Muted.TLabel").pack(anchor=tk.W, pady=(12, 4))
        tool_box = tk.Frame(left, bg=THEME["bg"])
        tool_box.pack(fill=tk.BOTH, expand=True)
        for tool_name in sorted(DEFAULT_ALLOWED_TOOLS):
            var = tk.BooleanVar(value=True)
            self.allowed_tool_vars[tool_name] = var
            ttk.Checkbutton(tool_box, text=tool_name, variable=var).pack(anchor=tk.W)

        ttk.Label(right, text="Task prompt", style="Muted.TLabel").pack(anchor=tk.W)
        self.prompt_text = self._text(right, height=7)
        self.prompt_text.insert("1.0", "Inspect this project and suggest the safest next step.")

        actions = ttk.Frame(right)
        actions.pack(fill=tk.X, pady=(8, 8))
        self.run_btn = ttk.Button(actions, text="Run Agent", style="Accent.TButton", command=self._run_agent, state=tk.DISABLED)
        self.run_btn.pack(side=tk.LEFT)
        ttk.Button(actions, text="Clear Output", command=lambda: self._set_text(self.agent_output, "")).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(actions, textvariable=self.agent_status_var, style="Muted.TLabel").pack(side=tk.RIGHT)
        recovery_row = ttk.Frame(right)
        recovery_row.pack(fill=tk.X, pady=(0, 8))
        self.recovery_decision_combo = ttk.Combobox(
            recovery_row,
            textvariable=self.recovery_decision_var,
            values=[],
            state="readonly",
            width=32,
        )
        self.recovery_decision_combo.pack(side=tk.LEFT)
        self.apply_decision_btn = ttk.Button(
            recovery_row,
            text="Apply Decision",
            command=self._apply_recovery_decision,
            state=tk.DISABLED,
        )
        self.apply_decision_btn.pack(side=tk.LEFT, padx=(8, 0))
        self.retry_timeout_btn = ttk.Button(
            recovery_row,
            text="Retry + Timeout",
            command=lambda: self._apply_recovery_decision("retry_longer_timeout"),
            state=tk.DISABLED,
        )
        self.retry_timeout_btn.pack(side=tk.LEFT, padx=(8, 0))

        ttk.Label(right, text="Sanitized output", style="Muted.TLabel").pack(anchor=tk.W)
        self.agent_output = self._text(right, height=22)

    def _build_tool_tab(self) -> None:
        left = ttk.Frame(self.tool_tab)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        right = ttk.Frame(self.tool_tab)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tool_var = tk.StringVar()
        self.tool_confirm_var = tk.BooleanVar(value=False)
        self.tool_status_var = tk.StringVar(value="Choose a tool.")

        ttk.Label(left, text="Tool", style="Muted.TLabel").pack(anchor=tk.W)
        self.tool_combo = ttk.Combobox(left, textvariable=self.tool_var, values=sorted(self.tools), state="readonly", width=34)
        self.tool_combo.pack(fill=tk.X, pady=(0, 8))
        self.tool_combo.bind("<<ComboboxSelected>>", lambda _event: self._load_selected_tool())
        ttk.Checkbutton(left, text="Permit side-effecting tool run", variable=self.tool_confirm_var).pack(anchor=tk.W, pady=(0, 8))
        ttk.Button(left, text="Load Default Input", command=self._load_selected_tool).pack(fill=tk.X)
        ttk.Button(left, text="Run Tool", style="Accent.TButton", command=self._run_tool).pack(fill=tk.X, pady=(8, 0))
        ttk.Label(left, textvariable=self.tool_status_var, style="Muted.TLabel", wraplength=260).pack(anchor=tk.W, pady=(10, 0))

        ttk.Label(right, text="Metadata and schema", style="Muted.TLabel").pack(anchor=tk.W)
        self.tool_schema_output = self._text(right, height=10)
        ttk.Label(right, text="Input JSON", style="Muted.TLabel").pack(anchor=tk.W, pady=(8, 0))
        self.tool_input = self._text(right, height=10)
        ttk.Label(right, text="Sanitized result", style="Muted.TLabel").pack(anchor=tk.W, pady=(8, 0))
        self.tool_output = self._text(right, height=12)
        if self.tools:
            self.tool_var.set(sorted(self.tools)[0])
            self._load_selected_tool()

    def _build_evidence_tab(self) -> None:
        left = ttk.Frame(self.evidence_tab)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        right = ttk.Frame(self.evidence_tab)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.evidence_session_var = tk.StringVar(value="default")
        self.evidence_query_var = tk.StringVar()
        self.evidence_item_var = tk.StringVar()
        self.evidence_mode_var = tk.StringVar(value="summary")
        self.evidence_limit_var = tk.StringVar(value="10")
        self.evidence_confirm_var = tk.BooleanVar(value=False)
        self.evidence_status_var = tk.StringVar(value="Evidence Shelf is ready.")

        self._entry(left, "Session ID", self.evidence_session_var)
        self._entry(left, "Search query", self.evidence_query_var)
        self._entry(left, "Evidence item ID", self.evidence_item_var)
        self._entry(left, "Limit", self.evidence_limit_var)
        self._combo(left, "Get mode", self.evidence_mode_var)
        self.evidence_mode_combo = self._last_combo
        self.evidence_mode_combo.configure(values=["summary", "verbatim"])
        ttk.Checkbutton(left, text="Permit evidence writes/exports", variable=self.evidence_confirm_var).pack(anchor=tk.W, pady=(4, 8))
        ttk.Button(left, text="Init Bag", command=lambda: self._run_evidence_action("init")).pack(fill=tk.X)
        ttk.Button(left, text="Load Shelf", command=lambda: self._run_evidence_action("shelf")).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(left, text="Search Bag", command=lambda: self._run_evidence_action("search")).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(left, text="Get Item", command=lambda: self._run_evidence_action("get")).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(left, text="Export Shelf", style="Accent.TButton", command=lambda: self._run_evidence_action("export")).pack(fill=tk.X, pady=(8, 0))
        ttk.Label(left, textvariable=self.evidence_status_var, style="Muted.TLabel", wraplength=260).pack(anchor=tk.W, pady=(10, 0))

        ttk.Label(right, text="Sanitized Evidence Shelf output", style="Muted.TLabel").pack(anchor=tk.W)
        self.evidence_output = self._text(right, height=34)

    def _build_teaching_tab(self) -> None:
        left = ttk.Frame(self.teaching_tab)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        right = ttk.Frame(self.teaching_tab)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.teaching_scenario_var = tk.StringVar(value="static_task_tracker")
        self.teaching_run_id_var = tk.StringVar()
        self.teaching_session_var = tk.StringVar(value="teaching-default")
        self.teaching_confirm_var = tk.BooleanVar(value=False)
        self.teaching_status_var = tk.StringVar(value="Teaching Lab is ready.")
        self.teaching_poll_active = False
        self.teaching_scenarios: list[str] = ["static_task_tracker", "python_notes_cli"]

        self._combo(left, "Scenario", self.teaching_scenario_var)
        self.teaching_scenario_combo = self._last_combo
        self.teaching_scenario_combo.configure(values=self.teaching_scenarios)
        self._entry(left, "Run ID", self.teaching_run_id_var)
        self._entry(left, "Session ID", self.teaching_session_var)
        ttk.Checkbutton(left, text="Permit sandbox writes/runs", variable=self.teaching_confirm_var).pack(anchor=tk.W, pady=(4, 8))
        ttk.Button(left, text="Refresh Scenarios", command=self._teaching_refresh).pack(fill=tk.X)
        ttk.Button(left, text="Plan Scenario", command=lambda: self._run_teaching_action("plan")).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(left, text="Create Sandbox", command=lambda: self._run_teaching_action("create_project")).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(left, text="Run Agent", command=lambda: self._run_teaching_action("run_agent")).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(left, text="Verify", command=lambda: self._run_teaching_action("verify_project")).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(left, text="Score", command=lambda: self._run_teaching_action("score")).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(left, text="Run Scenario", style="Accent.TButton", command=lambda: self._run_teaching_action("run_scenario")).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(left, text="Export Scorecard", command=lambda: self._run_teaching_action("export")).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(left, text="Latest Status", command=lambda: self._run_teaching_action("latest_status")).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(left, text="Tail Events", command=lambda: self._run_teaching_action("tail_events")).pack(fill=tk.X, pady=(8, 0))
        ttk.Label(left, textvariable=self.teaching_status_var, style="Muted.TLabel", wraplength=260).pack(anchor=tk.W, pady=(10, 0))

        ttk.Label(right, text="Sanitized Teaching Lab output", style="Muted.TLabel").pack(anchor=tk.W)
        self.teaching_output = self._text(right, height=34)

    def _entry(self, parent: ttk.Frame, label: str, variable: tk.StringVar) -> None:
        ttk.Label(parent, text=label, style="Muted.TLabel").pack(anchor=tk.W)
        ttk.Entry(parent, textvariable=variable, width=36).pack(fill=tk.X, pady=(0, 8))

    def _combo(self, parent: ttk.Frame, label: str, variable: tk.StringVar) -> None:
        ttk.Label(parent, text=label, style="Muted.TLabel").pack(anchor=tk.W)
        combo = ttk.Combobox(parent, textvariable=variable, values=[], state="readonly", width=34)
        combo.pack(fill=tk.X, pady=(0, 8))
        self._last_combo = combo

    def _field_with_browse(self, parent: ttk.Frame, label: str, variable: tk.StringVar, command) -> None:
        ttk.Label(parent, text=label, style="Muted.TLabel").pack(anchor=tk.W)
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=(0, 8))
        ttk.Entry(row, textvariable=variable, width=28, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text="Browse", command=command).pack(side=tk.RIGHT, padx=(6, 0))

    def _text(self, parent: ttk.Frame, height: int) -> tk.Text:
        frame = tk.Frame(parent, bg=THEME["border"], bd=1)
        frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        text = tk.Text(
            frame,
            height=height,
            bg=THEME["panel"],
            fg=THEME["fg"],
            insertbackground=THEME["fg"],
            font=FONT_MONO,
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            padx=8,
            pady=8,
        )
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return text

    def _set_text(self, widget: tk.Text, value: str) -> None:
        widget.delete("1.0", tk.END)
        widget.insert("1.0", value)

    def _browse_project(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.project_root_path or str(self.toolbox_root))
        if selected:
            self.project_root_path = selected
            self.project_var.set(sanitize_path_text(selected, project_root=selected, toolbox_root=self.toolbox_root))

    def _project_root(self) -> str:
        return self.project_root_path

    def _refresh_models(self) -> None:
        self.agent_status_var.set("Refreshing models...")
        self.run_btn.configure(state=tk.DISABLED)
        self._threaded(self._refresh_models_worker)

    def _refresh_models_worker(self) -> None:
        result = dispatch_tool(self.toolbox_root, "local_sidecar_agent", {
            "action": "models",
            "project_root": self._project_root(),
            "ollama_base_url": self.base_url_var.get(),
            "timeout_seconds": 10,
        })
        payload = result.get("result", {}) if isinstance(result, dict) else {}
        models = payload.get("models", []) if isinstance(payload, dict) else []
        if not isinstance(models, list):
            models = []
        self.model_names = [str(item) for item in models]
        self.root.after(0, lambda: self._apply_models(result))

    def _apply_models(self, result: dict[str, Any]) -> None:
        self.planner_combo.configure(values=self.model_names)
        self.response_combo.configure(values=self.model_names)
        self.recovery_combo.configure(values=self.model_names)
        self.planner_model_var.set(choose_model(self.model_names, ["qwen2.5-coder", "qwen2.5"], ""))
        self.response_model_var.set(choose_model(self.model_names, ["qwen3.5", "qwen3"], ""))
        self.recovery_model_var.set(choose_model(self.model_names, ["qwen3.5", "qwen3"], ""))
        if self.model_names:
            self.agent_status_var.set(f"{len(self.model_names)} models available.")
            self.run_btn.configure(state=tk.NORMAL)
        else:
            self.agent_status_var.set("No Ollama models available. Refresh after starting Ollama.")
            self.run_btn.configure(state=tk.DISABLED)
        self._set_text(self.agent_output, format_json(result, project_root=self._project_root(), toolbox_root=self.toolbox_root))

    def _agent_status(self) -> None:
        self._threaded(lambda: self._agent_status_worker())

    def _agent_status_worker(self) -> None:
        result = dispatch_tool(self.toolbox_root, "local_sidecar_agent", {
            "action": "status",
            "project_root": self._project_root(),
            "allowed_tools": self._allowed_tools(),
        })
        self.root.after(0, lambda: self._set_text(
            self.agent_output,
            format_json(result, project_root=self._project_root(), toolbox_root=self.toolbox_root),
        ))

    def _run_agent(self) -> None:
        if not self.planner_model_var.get() or not self.response_model_var.get():
            messagebox.showwarning(".dev-tools", "Refresh Ollama models before running the agent.")
            return
        try:
            payload = agent_payload(
                project_root=self._project_root(),
                prompt=self.prompt_text.get("1.0", tk.END).strip(),
                ollama_base_url=self.base_url_var.get(),
                planner_model=self.planner_model_var.get(),
                response_model=self.response_model_var.get(),
                allowed_tools=self._allowed_tools(),
                timeout_seconds=int(self.timeout_var.get() or "60"),
                max_tool_rounds=int(self.rounds_var.get() or "4"),
                confirm_mutations=self.confirm_mutations_var.get(),
                confirm_checkpoint=self.confirm_checkpoint_var.get(),
                checkpoint=self.checkpoint_var.get(),
                confirm_evidence=self.confirm_evidence_var.get(),
                heartbeat=self.heartbeat_var.get(),
                use_recovery_model=self.recovery_model_enabled_var.get(),
                recovery_model=self.recovery_model_var.get(),
                claim_enforcement=self.claim_enforcement_var.get() or "warn",
                planning_workspace=self.planning_workspace_var.get(),
                use_evidence_shelf=self.use_evidence_var.get(),
                window_turns=int(self.window_turns_var.get() or "8"),
                session_id=self.session_id_var.get().strip(),
            )
        except Exception as exc:
            messagebox.showerror(".dev-tools", str(exc))
            return
        self.last_agent_payload = payload
        self.agent_status_var.set("Agent running...")
        self.agent_running = True
        import time
        self.agent_started_at = time.time()
        self.run_btn.configure(state=tk.DISABLED)
        self._pulse_agent_status()
        self._threaded(lambda: self._run_agent_worker(payload))

    def _run_agent_worker(self, payload: dict[str, Any]) -> None:
        try:
            result = dispatch_tool(self.toolbox_root, "local_sidecar_agent", payload)
        except Exception as exc:
            result = {"status": "error", "result": {"message": str(exc)}}
        self.root.after(0, lambda: self._finish_agent_run(result))

    def _finish_agent_run(self, result: dict[str, Any]) -> None:
        self.agent_running = False
        self.last_agent_result = result
        self.run_btn.configure(state=tk.NORMAL if self.model_names else tk.DISABLED)
        self.agent_status_var.set(agent_recovery_status(result))
        self._populate_recovery_decisions(result)
        self._set_text(self.agent_output, format_json(result, project_root=self._project_root(), toolbox_root=self.toolbox_root))

    def _pulse_agent_status(self) -> None:
        if not self.agent_running:
            return
        import time
        elapsed = int(time.time() - self.agent_started_at)
        self.agent_status_var.set(f"Agent running... {elapsed}s")
        self.root.after(1000, self._pulse_agent_status)

    def _populate_recovery_decisions(self, result: dict[str, Any]) -> None:
        decisions = recovery_decisions(result)
        labels = [f"{item.get('id')} - {item.get('label', item.get('id'))}" for item in decisions]
        self.recovery_decision_combo.configure(values=labels)
        self.recovery_decision_var.set(labels[0] if labels else "")
        state = tk.NORMAL if labels else tk.DISABLED
        self.apply_decision_btn.configure(state=state)
        retry_available = any(item.get("id") == "retry_longer_timeout" for item in decisions)
        self.retry_timeout_btn.configure(state=tk.NORMAL if retry_available else tk.DISABLED)

    def _apply_recovery_decision(self, decision_id: str | None = None) -> None:
        decisions = recovery_decisions(self.last_agent_result)
        selected = decision_id or self.recovery_decision_var.get().split(" - ", 1)[0]
        decision = next((item for item in decisions if item.get("id") == selected), None)
        if not decision:
            return
        kind = str(decision.get("kind", ""))
        if kind == "refresh_models":
            self._refresh_models()
            return
        if decision.get("id") == "confirm_mutations":
            self.confirm_mutations_var.set(True)
        payload = apply_recovery_decision(self.last_agent_payload, decision)
        if not payload or kind in {"operator", "stop"}:
            self.agent_status_var.set(str(decision.get("label", "Decision recorded.")))
            return
        self.timeout_var.set(str(payload.get("timeout_seconds", self.timeout_var.get())))
        self.last_agent_payload = payload
        self.agent_status_var.set(f"Applying decision: {decision.get('label', selected)}")
        self.agent_running = True
        import time
        self.agent_started_at = time.time()
        self.run_btn.configure(state=tk.DISABLED)
        self._pulse_agent_status()
        self._threaded(lambda: self._run_agent_worker(payload))

    def _allowed_tools(self) -> list[str]:
        return [name for name, var in self.allowed_tool_vars.items() if var.get()]

    def _load_selected_tool(self) -> None:
        name = self.tool_var.get()
        if not name:
            return
        try:
            tool = self.tools[name]
            metadata = self.tool_metadata.get(name) or load_tool_metadata(self.toolbox_root, tool)
            self.tool_metadata[name] = metadata
            schema = metadata.get("input_schema", {})
            default_input = default_input_from_schema(schema, self._project_root())
            self._set_text(self.tool_schema_output, format_json({
                "tool": name,
                "category": tool.get("category"),
                "summary": metadata.get("summary"),
                "mutating": is_mutating_tool(tool),
                "input_schema": schema,
            }, toolbox_root=self.toolbox_root))
            self._set_text(self.tool_input, format_json(default_input, project_root=self._project_root(), toolbox_root=self.toolbox_root))
            side_effect = "side-effecting" if is_mutating_tool(tool) else "read-only or low-risk"
            self.tool_status_var.set(f"Loaded {name} ({side_effect}).")
        except Exception as exc:
            self.tool_status_var.set(str(exc))

    def _run_tool(self) -> None:
        name = self.tool_var.get()
        if not name:
            return
        tool = self.tools[name]
        if is_mutating_tool(tool) and not self.tool_confirm_var.get():
            messagebox.showwarning(".dev-tools", "This tool may mutate state. Check the side-effect confirmation box first.")
            return
        try:
            arguments = json.loads(self.tool_input.get("1.0", tk.END))
            if not isinstance(arguments, dict):
                raise ValueError("Input JSON must be an object.")
        except Exception as exc:
            messagebox.showerror(".dev-tools", str(exc))
            return
        arguments = self._desanitize_tool_input(arguments)
        self.tool_status_var.set(f"Running {name}...")
        self._threaded(lambda: self._run_tool_worker(name, arguments))

    def _run_tool_worker(self, name: str, arguments: dict[str, Any]) -> None:
        try:
            result = dispatch_tool(self.toolbox_root, name, arguments)
        except Exception as exc:
            result = {"status": "error", "tool": name, "result": {"message": str(exc)}}
        self.root.after(0, lambda: self._finish_tool_run(name, result))

    def _finish_tool_run(self, name: str, result: dict[str, Any]) -> None:
        self.tool_status_var.set(f"{name} finished: {result.get('status', 'unknown')}")
        self._set_text(self.tool_output, format_json(result, project_root=self._project_root(), toolbox_root=self.toolbox_root))

    def _run_evidence_action(self, action: str) -> None:
        if action in {"init", "export"} and not self.evidence_confirm_var.get():
            messagebox.showwarning(".dev-tools", "Evidence writes and exports require the evidence confirmation box.")
            return
        try:
            payload: dict[str, Any] = {
                "project_root": self._project_root(),
                "action": action,
                "session_id": self.evidence_session_var.get().strip() or "default",
                "limit": int(self.evidence_limit_var.get() or "10"),
            }
            if action in {"init", "export"}:
                payload["confirm"] = True
            if action == "search":
                payload["query"] = self.evidence_query_var.get()
            if action == "get":
                payload["item_id"] = self.evidence_item_var.get()
                payload["mode"] = self.evidence_mode_var.get()
            if action == "export":
                payload["format"] = "markdown"
        except Exception as exc:
            messagebox.showerror(".dev-tools", str(exc))
            return
        self.evidence_status_var.set(f"Running evidence {action}...")
        self._threaded(lambda: self._run_evidence_worker(action, payload))

    def _run_evidence_worker(self, action: str, payload: dict[str, Any]) -> None:
        try:
            result = dispatch_tool(self.toolbox_root, "session_evidence_store", payload)
        except Exception as exc:
            result = {"status": "error", "tool": "session_evidence_store", "result": {"message": str(exc)}}
        self.root.after(0, lambda: self._finish_evidence_run(action, result))

    def _finish_evidence_run(self, action: str, result: dict[str, Any]) -> None:
        self.evidence_status_var.set(f"Evidence {action} finished: {result.get('status', 'unknown')}")
        self._set_text(self.evidence_output, format_json(result, project_root=self._project_root(), toolbox_root=self.toolbox_root))

    def _teaching_refresh(self) -> None:
        self.teaching_status_var.set("Refreshing teaching scenarios...")
        self._threaded(self._teaching_refresh_worker)

    def _teaching_refresh_worker(self) -> None:
        try:
            result = dispatch_tool(self.toolbox_root, "teaching_sandbox_harness", {
                "project_root": self._project_root(),
                "action": "list_scenarios",
            })
        except Exception as exc:
            result = {"status": "error", "tool": "teaching_sandbox_harness", "result": {"message": str(exc)}}
        self.root.after(0, lambda: self._finish_teaching_refresh(result))

    def _finish_teaching_refresh(self, result: dict[str, Any]) -> None:
        scenarios = result.get("result", {}).get("scenarios", []) if isinstance(result.get("result"), dict) else []
        names = [str(item.get("scenario_id")) for item in scenarios if isinstance(item, dict) and item.get("scenario_id")]
        if names:
            self.teaching_scenarios = names
            self.teaching_scenario_combo.configure(values=names)
            if self.teaching_scenario_var.get() not in names:
                self.teaching_scenario_var.set(names[0])
        self.teaching_status_var.set(f"Scenario refresh finished: {result.get('status', 'unknown')}")
        self._set_text(self.teaching_output, format_json(result, project_root=self._project_root(), toolbox_root=self.toolbox_root))

    def _run_teaching_action(self, action: str) -> None:
        mutating = action in {"create_project", "run_agent", "run_scenario", "export", "export_review"}
        if mutating and not self.teaching_confirm_var.get():
            messagebox.showwarning(".dev-tools", "Sandbox writes and runs require the teaching confirmation box.")
            return
        payload: dict[str, Any] = {
            "project_root": self._project_root(),
            "action": action,
            "scenario_id": self.teaching_scenario_var.get() or "static_task_tracker",
            "session_id": self.teaching_session_var.get().strip() or "teaching-default",
        }
        run_id = self.teaching_run_id_var.get().strip()
        if run_id:
            payload["run_id"] = run_id
        if mutating:
            payload["confirm"] = True
        if action in {"run_agent", "run_scenario"}:
            payload.update({
                "ollama_base_url": self.base_url_var.get(),
                "planner_model": self.planner_model_var.get() or "qwen2.5-coder:7b",
                "response_model": self.response_model_var.get() or "qwen3.5:4b",
                "timeout_seconds": int(self.timeout_var.get() or "60"),
                "max_tool_rounds": int(self.rounds_var.get() or "4"),
                "preflight": False,
            })
        if action == "export":
            payload["format"] = "markdown"
        self.teaching_status_var.set(f"Running teaching {action}...")
        if action in {"run_agent", "run_scenario"}:
            self.teaching_poll_active = True
            self._schedule_teaching_status_poll()
        self._threaded(lambda: self._run_teaching_worker(action, payload))

    def _run_teaching_worker(self, action: str, payload: dict[str, Any]) -> None:
        try:
            result = dispatch_tool(self.toolbox_root, "teaching_sandbox_harness", payload)
        except Exception as exc:
            result = {"status": "error", "tool": "teaching_sandbox_harness", "result": {"message": str(exc)}}
        self.root.after(0, lambda: self._finish_teaching_run(action, result))

    def _finish_teaching_run(self, action: str, result: dict[str, Any]) -> None:
        self.teaching_poll_active = False
        self.teaching_status_var.set(f"Teaching {action} finished: {result.get('status', 'unknown')}")
        payload = result.get("result", {}) if isinstance(result.get("result"), dict) else {}
        run_id = payload.get("run_id")
        if not run_id and isinstance(payload.get("project"), dict):
            run_id = payload["project"].get("run_id")
        if run_id:
            self.teaching_run_id_var.set(str(run_id))
        self._set_text(self.teaching_output, format_json(result, project_root=self._project_root(), toolbox_root=self.toolbox_root))

    def _schedule_teaching_status_poll(self) -> None:
        if not self.teaching_poll_active:
            return
        self._threaded(self._teaching_status_poll_worker)
        self.root.after(1500, self._schedule_teaching_status_poll)

    def _teaching_status_poll_worker(self) -> None:
        payload: dict[str, Any] = {
            "project_root": self._project_root(),
            "action": "latest_status",
        }
        run_id = self.teaching_run_id_var.get().strip()
        if run_id:
            payload["run_id"] = run_id
        try:
            result = dispatch_tool(self.toolbox_root, "teaching_sandbox_harness", payload)
        except Exception as exc:
            result = {"status": "error", "tool": "teaching_sandbox_harness", "result": {"message": str(exc)}}
        self.root.after(0, lambda: self._finish_teaching_status_poll(result))

    def _finish_teaching_status_poll(self, result: dict[str, Any]) -> None:
        if not self.teaching_poll_active:
            return
        payload = result.get("result", {}) if isinstance(result.get("result"), dict) else {}
        latest = payload.get("latest_event", {}) if isinstance(payload, dict) else {}
        if isinstance(latest, dict) and latest:
            phase = latest.get("phase", "")
            status = latest.get("status", "")
            run_id = latest.get("run_id", "")
            self.teaching_status_var.set(f"Teaching run {run_id}: {phase} {status}")

    def _desanitize_tool_input(self, value: Any) -> Any:
        if isinstance(value, str):
            return (
                value.replace("<project_root>", self._project_root())
                .replace("<toolbox_root>", str(self.toolbox_root))
            )
        if isinstance(value, list):
            return [self._desanitize_tool_input(item) for item in value]
        if isinstance(value, dict):
            return {key: self._desanitize_tool_input(item) for key, item in value.items()}
        return value

    def _threaded(self, target) -> None:
        threading.Thread(target=target, daemon=True).start()


def self_test() -> int:
    from lib.operator_ui_support import scan_privacy_leaks

    tools = tool_index(ROOT)
    assert "local_sidecar_agent" in tools
    assert "session_evidence_store" in tools
    assert "teaching_sandbox_harness" in tools
    assert choose_model(["tiny:1", "qwen2.5-coder:7b"], ["qwen2.5-coder"], "fallback") == "qwen2.5-coder:7b"
    payload = agent_payload(
        project_root=str(ROOT),
        prompt="hello",
        ollama_base_url="http://localhost:11434",
        planner_model="qwen2.5-coder:7b",
        response_model="qwen3.5:4b",
        allowed_tools=["text_file_reader"],
        timeout_seconds=10,
        max_tool_rounds=1,
        confirm_mutations=False,
        confirm_checkpoint=False,
        checkpoint=True,
        confirm_evidence=True,
        heartbeat=True,
        use_recovery_model=True,
        recovery_model="qwen3.5:4b",
        claim_enforcement="require_citation",
        planning_workspace=True,
        use_evidence_shelf=True,
        window_turns=8,
        session_id="self-test",
    )
    assert payload["action"] == "run"
    assert payload["session_id"] == "self-test"
    assert payload["heartbeat"] is True
    assert payload["claim_enforcement"] == "require_citation"
    assert "Timed out" in agent_recovery_status({
        "status": "error",
        "result": {
            "recovery": {
                "class": "request_timeout",
                "next_actions": ["increase_timeout", "retry_run"],
                "decisions": [{"id": "retry_longer_timeout", "patch": {"timeout_seconds": 120}}],
            }
        },
    })
    retry = apply_recovery_decision(payload, {"id": "retry_longer_timeout", "patch": {"timeout_seconds": 120}})
    assert retry["timeout_seconds"] == 120
    assert "<toolbox_root>" in sanitize_path_text(str(ROOT / "README.md"), toolbox_root=ROOT)
    scenarios = dispatch_tool(ROOT, "teaching_sandbox_harness", {"project_root": str(ROOT), "action": "list_scenarios"})
    assert scenarios["status"] == "ok"
    assert any(item["scenario_id"] == "static_task_tracker" for item in scenarios["result"]["scenarios"])
    docs = [ROOT / "README.md", ROOT / "_docs" / "TODO.md"]
    assert isinstance(scan_privacy_leaks(docs), list)
    print("agent_ui self-test passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Launch the .dev-tools local agent operator UI.")
    parser.add_argument("--self-test", action="store_true", help="Run headless helper checks.")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    root = tk.Tk()
    OperatorUI(root, ROOT)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
