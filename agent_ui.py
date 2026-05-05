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
    choose_model,
    default_input_from_schema,
    dispatch_tool,
    format_json,
    is_mutating_tool,
    load_tool_metadata,
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
        notebook.add(self.agent_tab, text="Agent Console")
        notebook.add(self.tool_tab, text="Tool Lab")
        self._build_agent_tab()
        self._build_tool_tab()

    def _build_agent_tab(self) -> None:
        left = ttk.Frame(self.agent_tab)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        right = ttk.Frame(self.agent_tab)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.project_var = tk.StringVar(value=sanitize_path_text(str(self.toolbox_root), toolbox_root=self.toolbox_root))
        self.base_url_var = tk.StringVar(value="http://localhost:11434")
        self.planner_model_var = tk.StringVar()
        self.response_model_var = tk.StringVar()
        self.timeout_var = tk.StringVar(value="60")
        self.rounds_var = tk.StringVar(value="4")
        self.confirm_mutations_var = tk.BooleanVar(value=False)
        self.confirm_checkpoint_var = tk.BooleanVar(value=False)
        self.checkpoint_var = tk.BooleanVar(value=True)
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
        self._entry(left, "Timeout seconds", self.timeout_var)
        self._entry(left, "Max tool rounds", self.rounds_var)
        ttk.Checkbutton(left, text="Confirm mutations", variable=self.confirm_mutations_var).pack(anchor=tk.W, pady=(4, 0))
        ttk.Checkbutton(left, text="Confirm checkpoint", variable=self.confirm_checkpoint_var).pack(anchor=tk.W)
        ttk.Checkbutton(left, text="Checkpoint after run", variable=self.checkpoint_var).pack(anchor=tk.W)

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
        self.planner_model_var.set(choose_model(self.model_names, ["qwen2.5-coder", "qwen2.5"], ""))
        self.response_model_var.set(choose_model(self.model_names, ["qwen3.5", "qwen3"], ""))
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
            )
        except Exception as exc:
            messagebox.showerror(".dev-tools", str(exc))
            return
        self.agent_status_var.set("Agent running...")
        self.run_btn.configure(state=tk.DISABLED)
        self._threaded(lambda: self._run_agent_worker(payload))

    def _run_agent_worker(self, payload: dict[str, Any]) -> None:
        try:
            result = dispatch_tool(self.toolbox_root, "local_sidecar_agent", payload)
        except Exception as exc:
            result = {"status": "error", "result": {"message": str(exc)}}
        self.root.after(0, lambda: self._finish_agent_run(result))

    def _finish_agent_run(self, result: dict[str, Any]) -> None:
        self.run_btn.configure(state=tk.NORMAL if self.model_names else tk.DISABLED)
        status = result.get("status", "unknown")
        if status == "approval_required":
            self.agent_status_var.set("Approval required. Review output, then rerun with the needed confirmation toggle.")
        else:
            self.agent_status_var.set(f"Agent finished: {status}")
        self._set_text(self.agent_output, format_json(result, project_root=self._project_root(), toolbox_root=self.toolbox_root))

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
    )
    assert payload["action"] == "run"
    assert "<toolbox_root>" in sanitize_path_text(str(ROOT / "README.md"), toolbox_root=ROOT)
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
