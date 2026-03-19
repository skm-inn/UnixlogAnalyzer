"""Screen 5 — Search results table."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, DataTable, Label, Static
from textual.containers import Vertical, Horizontal
from textual import work

import os
from pathlib import Path
from datetime import datetime


class ResultsScreen(Screen):
    DEFAULT_CSS = """
    ResultsScreen {
        align: center middle;
    }
    #header {
        dock: top;
        height: 3;
        background: $panel;
        color: $accent;
        content-align: center middle;
        border-bottom: solid $border;
    }
    #footer {
        dock: bottom;
        height: 3;
        background: $panel;
        color: $text-muted;
        content-align: center middle;
        border-top: solid $border;
    }
    #results-panel {
        width: 90%;
        height: 1fr;
        border: solid $border;
        background: $panel;
        padding: 1 1;
        margin: 1 0;
    }
    #summary {
        color: $text-muted;
        padding: 0 0 1 0;
    }
    DataTable {
        height: 1fr;
    }
    #btn-row {
        align: center middle;
        height: 5;
        padding: 1 0;
        dock: bottom;
    }
    #btn-new-search { margin-right: 2; }
    #btn-export    { margin-right: 2; }
    #btn-copy      { margin-right: 2; }
    #btn-copy      { min-width: 20; }
    #btn-analyze   { min-width: 20; }
    """

    def compose(self) -> ComposeResult:
        matches = self.app.matches
        count = len(matches)
        files = len({m[0] for m in matches})
        term = self.app.search_term

        yield Static("Search Results", id="header")
        with Vertical(id="results-panel"):
            yield Label(
                f"Found  [bold yellow]{count}[/bold yellow]  match(es) in "
                f"[bold]{files}[/bold]  file(s)  —  term:  [bold yellow]*{term}*[/bold yellow]",
                id="summary",
            )
            yield DataTable(id="result-table", zebra_stripes=True)
            with Horizontal(id="btn-row"):
                yield Button("◄ New Search", id="btn-new-search")
                yield Button("Export TXT", id="btn-export")
                yield Button(
                    "Copy Files ►",
                    id="btn-copy",
                    variant="primary",
                    disabled=(count == 0),
                )
        yield Static(
            "↑↓: scroll  ·  Enter: select  ·  Tab: next button  ·  Ctrl+Q: quit",
            id="footer",
        )

    def on_mount(self) -> None:
        table = self.query_one("#result-table", DataTable)
        table.add_columns("File Path", "Line", "Matched Text")
        table.cursor_type = "row"

        for filepath, lineno, line_text in self.app.matches:
            short_path = self._shorten_path(filepath)
            display_line = line_text.strip()[:120]
            table.add_row(short_path, str(lineno), display_line, key=filepath)

        if not self.app.matches:
            table.add_row("—  No matches found  —", "", "")

        if self.app.matches:
            table.focus()

    def _shorten_path(self, path: str) -> str:
        """Shorten long paths for display."""
        parts = Path(path).parts
        if len(parts) <= 4:
            return path
        return os.path.join("…", *parts[-3:])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-new-search":
            # Pop back to welcome (clear the stack)
            while len(self.app.screen_stack) > 1:
                self.app.pop_screen()
        elif bid == "btn-export":
            self._export_report()
        elif bid == "btn-copy":
            from app.screens.copy_confirm import CopyConfirmScreen
            self.app.push_screen(CopyConfirmScreen())

    def _export_report(self) -> None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = Path("lookup") / f"search_report_{ts}.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"LogAnalyzer Search Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Search Term: *{self.app.search_term}*",
            f"Paths: {', '.join(self.app.log_paths)}",
            f"Pattern: {self.app.file_pattern or '(all files)'}",
            f"Total Matches: {len(self.app.matches)}",
            "",
            "-" * 80,
            "",
        ]
        for filepath, lineno, line_text in self.app.matches:
            lines.append(f"{filepath}:{lineno}: {line_text}")
        out.write_text("\n".join(lines), encoding="utf-8")
        self.notify(f"Report saved: {out}", severity="information")
