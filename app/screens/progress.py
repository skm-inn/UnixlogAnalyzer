"""Screen 4 — Search progress with live stats."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, ProgressBar, Static
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual import work

from app.core.searcher import count_files, search_logs


class SearchProgressScreen(Screen):
    DEFAULT_CSS = """
    SearchProgressScreen {
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
    #progress-panel {
        width: 66;
        border: solid $border;
        background: $panel;
        padding: 2 3;
        margin: 1 0;
    }
    .section-label {
        color: $accent;
        padding: 0 0 1 0;
    }
    ProgressBar {
        margin-bottom: 1;
    }
    #current-file {
        color: $text-muted;
        padding: 0 0 1 0;
        overflow: hidden;
        height: 1;
    }
    #stats-row {
        height: 3;
        padding: 1 0;
    }
    #stat-files {
        width: 1fr;
        color: $text;
    }
    #stat-matches {
        width: 1fr;
        color: $success;
    }
    #btn-row {
        align: center middle;
        height: 5;
        padding: 1 0;
    }
    #btn-cancel { min-width: 16; }
    """

    files_scanned: reactive[int] = reactive(0)
    total_files: reactive[int] = reactive(0)
    matches_found: reactive[int] = reactive(0)
    _cancelled: bool = False

    def compose(self) -> ComposeResult:
        yield Static("Step 3 of 3  —  Searching", id="header")
        with Vertical(id="progress-panel"):
            yield Label("Discovering files…", classes="section-label", id="phase-label")
            yield ProgressBar(total=100, show_eta=False, id="main-bar")
            yield Label("", id="current-file")
            with Horizontal(id="stats-row"):
                yield Label("Files: 0 / 0", id="stat-files")
                yield Label("Matches: 0", id="stat-matches")
            with Horizontal(id="btn-row"):
                yield Button("✕  Cancel", id="btn-cancel", variant="error")
        yield Static("Please wait — do not close the terminal", id="footer")

    def on_mount(self) -> None:
        self._run_search()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self._cancelled = True
            self.app.pop_screen()

    def watch_files_scanned(self, value: int) -> None:
        self.query_one("#stat-files", Label).update(
            f"Files: {value} / {self.total_files}"
        )
        if self.total_files > 0:
            self.query_one("#main-bar", ProgressBar).progress = value

    def watch_total_files(self, value: int) -> None:
        self.query_one("#stat-files", Label).update(
            f"Files: {self.files_scanned} / {value}"
        )
        if value > 0:
            self.query_one("#main-bar", ProgressBar).total = value

    def watch_matches_found(self, value: int) -> None:
        self.query_one("#stat-matches", Label).update(f"Matches: {value}")

    def _on_file_scanned(self, filepath: str) -> None:
        """Called from background thread for each file scanned."""
        self.call_from_thread(setattr, self, "files_scanned", self.files_scanned + 1)
        short = filepath[-58:] if len(filepath) > 58 else filepath
        self.call_from_thread(
            self.query_one("#current-file", Label).update, short
        )

    @work(thread=True)
    def _run_search(self) -> None:
        paths = self.app.log_paths
        term = self.app.search_term
        pattern = self.app.file_pattern or ""

        # Phase 1: count files
        total = count_files(paths, pattern)
        self.call_from_thread(setattr, self, "total_files", max(total, 1))

        # Phase 2: search
        self.call_from_thread(
            self.query_one("#phase-label", Label).update,
            f"Searching for  [bold yellow]*{term}*[/bold yellow]",
        )

        matches = []
        for filepath, lineno, line_text in search_logs(
            paths, term, pattern, progress_callback=self._on_file_scanned
        ):
            if self._cancelled:
                return
            matches.append((filepath, lineno, line_text))
            self.call_from_thread(setattr, self, "matches_found", len(matches))

        if self._cancelled:
            return

        self.app.matches = matches
        self.call_from_thread(self._go_to_results)

    def _go_to_results(self) -> None:
        from app.screens.results import ResultsScreen
        self.app.push_screen(ResultsScreen())
