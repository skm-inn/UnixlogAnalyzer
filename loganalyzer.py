#!/usr/bin/env python3
"""LogAnalyzer — Unix Log Search & AI Analysis Tool.

Entry point:  python loganalyzer.py
"""

from textual.app import App, ComposeResult
from textual.widgets import Static
from pathlib import Path
from typing import List, Optional, Tuple


class LogAnalyzerApp(App):
    """Main TUI application."""

    TITLE = "LogAnalyzer"
    CSS = """
    /* ── Global dark GitHub palette ───────────────────────────────────── */
    Screen {
        background: #0d1117;
    }

    /* ── Textual theme variable overrides ─────────────────────────────── */
    $background:  #0d1117;
    $surface:     #161b22;
    $panel:       #161b22;
    $border:      #30363d;
    $accent:      #58a6ff;
    $success:     #3fb950;
    $warning:     #d29922;
    $error:       #f85149;
    $text:        #c9d1d9;
    $text-muted:  #8b949e;

    /* ── Buttons ───────────────────────────────────────────────────────── */
    Button {
        background: #21262d;
        color: $text;
        border: solid $border;
    }
    Button:hover {
        background: #30363d;
    }
    Button.-primary {
        background: #1f6feb;
        color: #ffffff;
        border: solid #388bfd;
    }
    Button.-primary:hover {
        background: #388bfd;
    }
    Button.-error {
        background: #da3633;
        color: #ffffff;
        border: solid #f85149;
    }
    Button.-error:hover {
        background: #f85149;
    }
    Button:disabled {
        background: #21262d;
        color: $text-muted;
        border: solid #21262d;
    }

    /* ── Inputs ────────────────────────────────────────────────────────── */
    Input {
        background: #0d1117;
        border: solid $border;
        color: $text;
    }
    Input:focus {
        border: solid $accent;
    }
    Input.invalid-input {
        border: solid $error;
    }

    /* ── TextArea ──────────────────────────────────────────────────────── */
    TextArea {
        background: #0d1117;
        border: solid $border;
        color: $text;
    }
    TextArea:focus {
        border: solid $accent;
    }

    /* ── DataTable ─────────────────────────────────────────────────────── */
    DataTable {
        background: #0d1117;
        color: $text;
    }
    DataTable > .datatable--header {
        background: #161b22;
        color: $accent;
    }
    DataTable > .datatable--cursor {
        background: #1f6feb;
        color: #ffffff;
    }
    DataTable > .datatable--even-row {
        background: #0d1117;
    }
    DataTable > .datatable--odd-row {
        background: #161b22;
    }

    /* ── ProgressBar ───────────────────────────────────────────────────── */
    ProgressBar > .bar--bar {
        color: $accent;
    }
    ProgressBar > .bar--complete {
        color: $success;
    }

    /* ── Log ───────────────────────────────────────────────────────────── */
    Log {
        background: #0d1117;
        color: $text;
        border: solid $border;
    }

    /* ── Markdown ──────────────────────────────────────────────────────── */
    Markdown {
        background: #0d1117;
        color: $text;
    }
    Markdown H1, Markdown H2, Markdown H3 {
        color: $accent;
    }
    Markdown CodeBlock {
        background: #161b22;
        border: solid $border;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("f1", "help", "Help"),
    ]

    # ── Application state shared across screens ────────────────────────
    log_paths: List[str] = []
    search_term: str = ""
    file_pattern: str = ""
    matches: List[Tuple[str, int, str]] = []
    lookup_folder: Optional[Path] = None
    user_context: str = ""
    analysis_text: str = ""
    report_path: str = ""
    prompt_export_path: str = ""

    def on_mount(self) -> None:
        from app.screens.welcome import WelcomeScreen
        self.push_screen(WelcomeScreen())

    def action_help(self) -> None:
        self.notify(
            "LogAnalyzer v1.0.0\n"
            "Tab: next field  ·  Ctrl+Q: quit  ·  ↑↓: scroll tables",
            severity="information",
            timeout=5,
        )


def main() -> None:
    app = LogAnalyzerApp()
    app.run()


if __name__ == "__main__":
    main()
