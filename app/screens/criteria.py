"""Screen 3 — Search criteria: term + optional file pattern."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static
from textual.containers import Vertical, Horizontal

from app.utils.validators import validate_file_pattern


class SearchCriteriaScreen(Screen):
    DEFAULT_CSS = """
    SearchCriteriaScreen {
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
    #form-panel {
        width: 66;
        border: solid $border;
        background: $panel;
        padding: 2 3;
        margin: 1 0;
    }
    .field-label {
        color: $text-muted;
        padding: 0 0 0 0;
    }
    .field-note {
        color: $text-muted;
        padding: 0 0 1 0;
    }
    Input {
        margin-bottom: 1;
    }
    #preview {
        color: $accent;
        padding: 1 0;
        border-top: solid $border;
        margin-top: 1;
    }
    #btn-row {
        align: center middle;
        height: 5;
        padding: 1 0;
    }
    #btn-back { margin-right: 2; }
    #btn-search { min-width: 16; }
    """

    def compose(self) -> ComposeResult:
        yield Static("Step 2 of 3  —  Search Criteria", id="header")
        with Vertical(id="form-panel"):
            yield Label("Search Term  *", classes="field-label")
            yield Label(
                "Searched as  *term*  (case-insensitive substring match)",
                classes="field-note",
            )
            yield Input(placeholder="e.g. ERROR", id="term-input")

            yield Label("File Name Filter  (optional)", classes="field-label")
            yield Label(
                "e.g. *.log  app_*.log  debug*  — leave blank to search all files",
                classes="field-note",
            )
            yield Input(placeholder="*.log", id="pattern-input")

            yield Label("", id="preview")

            with Horizontal(id="btn-row"):
                yield Button("◄ Back", id="btn-back")
                yield Button("Search ►", id="btn-search", variant="primary")

        yield Static("Tab: next field  ·  Ctrl+Q: quit  ·  F1: help", id="footer")

    def on_mount(self) -> None:
        self.query_one("#term-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._update_preview()

    def _update_preview(self) -> None:
        term = self.query_one("#term-input", Input).value.strip()
        pat = self.query_one("#pattern-input", Input).value.strip()
        preview = self.query_one("#preview", Label)
        if not term:
            preview.update("")
            return
        pat_str = f"  in  [bold]{pat}[/bold] files" if pat else "  in  all files"
        preview.update(f"Will search for  [bold yellow]*{term}*[/bold yellow]{pat_str}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-search":
            self._try_search()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._try_search()

    def _try_search(self) -> None:
        term = self.query_one("#term-input", Input).value.strip()
        if not term:
            self.notify("Please enter a search term.", severity="error")
            return
        pat = self.query_one("#pattern-input", Input).value.strip()
        ok, msg = validate_file_pattern(pat)
        if not ok:
            self.notify(f"Invalid pattern: {msg}", severity="error")
            return
        self.app.search_term = term
        self.app.file_pattern = pat if pat else ""
        from app.screens.progress import SearchProgressScreen
        self.app.push_screen(SearchProgressScreen())
