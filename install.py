"""
FILE: install.py
ROLE: Tkinter installer UI for vendoring .dev-tools into a target project.
WHAT IT DOES:
  - Presents a simple dark-themed UI to pick a target project folder
  - Shows a preview of what will be installed
  - Installs the full .dev-tools sidecar payload into the target
  - Reports success/failure with a log of installed files
HOW TO USE:
  - python install.py
"""

from __future__ import annotations

import sys
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

# Ensure src/ is importable
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# ── Theme ───────────────────────────────────────────────────────────

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

    style.configure(".", background=THEME["bg"], foreground=THEME["fg"],
                    fieldbackground=THEME["field"], font=FONT)
    style.configure("TFrame", background=THEME["bg"])
    style.configure("TLabel", background=THEME["bg"], foreground=THEME["fg"], font=FONT)
    style.configure("Heading.TLabel", background=THEME["bg"], foreground=THEME["fg"], font=FONT_HEADING)
    style.configure("Muted.TLabel", background=THEME["bg"], foreground=THEME["muted"], font=FONT)
    style.configure("Success.TLabel", background=THEME["bg"], foreground=THEME["success"], font=FONT_BOLD)
    style.configure("Error.TLabel", background=THEME["bg"], foreground=THEME["error"], font=FONT_BOLD)
    style.configure("TButton", background=THEME["button"], foreground=THEME["fg"],
                    padding=(12, 6), font=FONT)
    style.map("TButton", background=[("active", THEME["button_hover"])])
    style.configure("Accent.TButton", background=THEME["accent"], foreground="#ffffff",
                    padding=(16, 8), font=FONT_BOLD)
    style.map("Accent.TButton", background=[("active", THEME["accent_hover"])])
    style.configure("TEntry", fieldbackground=THEME["field"], foreground=THEME["fg"],
                    insertcolor=THEME["fg"], font=FONT)
    style.configure("TCheckbutton", background=THEME["bg"], foreground=THEME["fg"], font=FONT)
    style.map("TCheckbutton", background=[("active", THEME["bg"])])


# ── Installer App ──────────────────────────────────────────────────

class InstallerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(".dev-tools Installer")
        self.root.geometry("680x560")
        self.root.minsize(580, 480)
        self.root.resizable(True, True)
        apply_theme(self.root)

        self._build_ui()

    def _build_ui(self) -> None:
        # Main container with padding
        main = ttk.Frame(self.root, padding=24)
        main.pack(fill=tk.BOTH, expand=True)

        # ── Header ──
        ttk.Label(main, text=".dev-tools Installer", style="Heading.TLabel").pack(anchor=tk.W)
        ttk.Label(
            main,
            text="Install the full .dev-tools sidecar into a new or existing project.",
            style="Muted.TLabel",
        ).pack(anchor=tk.W, pady=(2, 16))

        # ── Separator ──
        sep = tk.Frame(main, height=1, bg=THEME["border"])
        sep.pack(fill=tk.X, pady=(0, 16))

        # ── Target folder picker ──
        picker_frame = ttk.Frame(main)
        picker_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(picker_frame, text="Target project folder:").pack(anchor=tk.W, pady=(0, 4))

        row = ttk.Frame(picker_frame)
        row.pack(fill=tk.X)

        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(row, textvariable=self.path_var, font=FONT)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        browse_btn = ttk.Button(row, text="Browse…", command=self._browse)
        browse_btn.pack(side=tk.RIGHT)

        # ── Options ──
        opts_frame = ttk.Frame(main)
        opts_frame.pack(fill=tk.X, pady=(8, 12))

        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            opts_frame, text="Overwrite existing files", variable=self.overwrite_var
        ).pack(anchor=tk.W)

        # ── Action buttons ──
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(0, 12))

        self.preview_btn = ttk.Button(btn_frame, text="Preview", command=self._preview)
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.install_btn = ttk.Button(btn_frame, text="Install", style="Accent.TButton",
                                       command=self._install)
        self.install_btn.pack(side=tk.LEFT)

        self.status_label = ttk.Label(btn_frame, text="", style="Muted.TLabel")
        self.status_label.pack(side=tk.RIGHT)

        # ── Log output ──
        ttk.Label(main, text="Output:", style="Muted.TLabel").pack(anchor=tk.W, pady=(4, 4))

        log_frame = tk.Frame(main, bg=THEME["border"], bd=1, relief=tk.FLAT)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_frame,
            bg=THEME["panel"],
            fg=THEME["fg"],
            insertbackground=THEME["fg"],
            font=FONT_MONO,
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            padx=8,
            pady=8,
            state=tk.DISABLED,
        )
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tag colors for log output
        self.log_text.tag_configure("success", foreground=THEME["success"])
        self.log_text.tag_configure("error", foreground=THEME["error"])
        self.log_text.tag_configure("warning", foreground=THEME["warning"])
        self.log_text.tag_configure("muted", foreground=THEME["muted"])
        self.log_text.tag_configure("heading", foreground=THEME["fg"], font=FONT_BOLD)

    def _log(self, text: str, tag: str = "") -> None:
        self.log_text.configure(state=tk.NORMAL)
        if tag:
            self.log_text.insert(tk.END, text + "\n", tag)
        else:
            self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _clear_log(self) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _browse(self) -> None:
        folder = filedialog.askdirectory(title="Select project folder")
        if folder:
            self.path_var.set(folder)

    def _validate_path(self) -> Path | None:
        raw = self.path_var.get().strip()
        if not raw:
            self._log("Please select a target project folder.", "error")
            return None
        target = Path(raw)
        if not target.is_dir():
            self._log(f"Not a directory: {target}", "error")
            return None
        return target

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.preview_btn.configure(state=state)
        self.install_btn.configure(state=state)
        self.path_entry.configure(state=state)
        if busy:
            self.status_label.configure(text="Working…", style="Muted.TLabel")
        else:
            self.status_label.configure(text="")

    def _preview(self) -> None:
        target = self._validate_path()
        if not target:
            return
        self._clear_log()
        self._log("Preview — what will be installed:", "heading")
        self._log(f"  Target: {target}", "muted")
        self._log(f"  Sidecar: {target / '.dev-tools'}", "muted")
        self._log("")

        self._set_busy(True)
        threading.Thread(target=self._run_preview, args=(target,), daemon=True).start()

    def _run_preview(self, target: Path) -> None:
        try:
            from lib.sidecar_release import install_sidecar
            result = install_sidecar(
                str(target), overwrite=self.overwrite_var.get(), preview=True
            )
            self.root.after(0, self._show_preview_result, result)
        except Exception as exc:
            self.root.after(0, self._show_error, str(exc))

    def _show_preview_result(self, result: dict) -> None:
        self._log("Files that would be installed:", "heading")
        for f in result["files"]:
            status = f["status"]
            path = f["path"]
            if status == "would_create":
                self._log(f"  + {path}", "success")
            elif status == "would_overwrite":
                self._log(f"  ! {path} (would overwrite)", "warning")
            elif status == "skipped":
                self._log(f"  ~ {path} (exists, would skip)", "warning")
            else:
                self._log(f"  ? {path} ({status})", "muted")
        self._log("")
        self._log(f"Manifest: {result.get('manifest_path', '')}", "muted")
        self._log(f"Excluded top-level entries: {len(result.get('excluded_top_level_entries', []))}", "muted")
        self._log("")
        self._log("Ready to install. Press Install to proceed.", "success")
        self._set_busy(False)

    def _install(self) -> None:
        target = self._validate_path()
        if not target:
            return
        self._clear_log()
        self._log("Installing .dev-tools sidecar…", "heading")
        self._log(f"  Target: {target}", "muted")
        self._log("")

        self._set_busy(True)
        threading.Thread(target=self._run_install, args=(target,), daemon=True).start()

    def _run_install(self, target: Path) -> None:
        try:
            from lib.sidecar_release import install_sidecar
            result = install_sidecar(
                str(target), overwrite=self.overwrite_var.get(), preview=False
            )
            self.root.after(0, self._show_install_result, result, target)
        except Exception as exc:
            self.root.after(0, self._show_error, str(exc))

    def _show_install_result(self, result: dict, target: Path) -> None:
        created = 0
        skipped = 0
        for f in result["files"]:
            status = f["status"]
            path = f["path"]
            if status in ("created", "overwritten"):
                self._log(f"  ✓ {path}", "success")
                created += 1
            elif status == "skipped":
                self._log(f"  ~ {path} (skipped)", "warning")
                skipped += 1
            else:
                self._log(f"  ? {path} ({status})", "muted")

        self._log("")
        self._log(f"Done! {created} files installed, {skipped} skipped.", "success")
        self._log("")
        self._log("Installed sidecar location:", "heading")
        self._log(f"  {result['sidecar_dir']}", "muted")
        self._log("")
        self._log("Next steps:", "heading")
        self._log(f"  cd \"{target}\"")
        self._log("  open .dev-tools/START_HERE.html")
        self._log("  python .dev-tools/src/tools/project_setup.py run --input-json \"{\\\"action\\\": \\\"audit\\\", \\\"project_root\\\": \\\".\\\"}\"")
        self._log("")
        self.status_label.configure(text="Installed ✓", style="Success.TLabel")
        self.preview_btn.configure(state="normal")
        self.install_btn.configure(state="normal")
        self.path_entry.configure(state="normal")

    def _show_error(self, message: str) -> None:
        self._log(f"Error: {message}", "error")
        self.status_label.configure(text="Failed", style="Error.TLabel")
        self.preview_btn.configure(state="normal")
        self.install_btn.configure(state="normal")
        self.path_entry.configure(state="normal")


def main() -> int:
    root = tk.Tk()
    InstallerApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
