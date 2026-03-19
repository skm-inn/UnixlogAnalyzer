"""Screen 6 — Copy matched files to lookup folder."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, ProgressBar, Static
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual import work

from app.core.file_copier import copy_matched_files


class CopyConfirmScreen(Screen):
    DEFAULT_CSS = """
    CopyConfirmScreen {
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
    #copy-panel {
        width: 66;
        border: solid $border;
        background: $panel;
        padding: 2 3;
        margin: 1 0;
    }
    .info-label {
        color: $text-muted;
        padding: 0 0 1 0;
    }
    #dest-label {
        color: $accent;
        padding: 0 0 1 0;
    }
    ProgressBar {
        margin-bottom: 1;
    }
    #current-file {
        color: $text-muted;
        height: 1;
        overflow: hidden;
    }
    #status-label {
        color: $success;
        padding: 1 0 0 0;
    }
    #btn-row {
        align: center middle;
        height: 5;
        padding: 1 0;
    }
    #btn-back   { margin-right: 2; }
    #btn-start  { min-width: 20; }
    #btn-analyze { min-width: 20; }
    """

    copied: reactive[int] = reactive(0)
    total: reactive[int] = reactive(0)
    _done: bool = False

    def compose(self) -> ComposeResult:
        matches = self.app.matches
        unique = len({m[0] for m in matches})
        yield Static("Copy Matched Files", id="header")
        with Vertical(id="copy-panel"):
            yield Label(
                f"[bold]{unique}[/bold] unique file(s) will be copied to:",
                classes="info-label",
            )
            yield Label("lookup/<term>_<timestamp>/", id="dest-label")
            yield Label(
                "Source files are never modified — copy only.",
                classes="info-label",
            )
            yield ProgressBar(total=max(unique, 1), show_eta=False, id="copy-bar")
            yield Label("", id="current-file")
            yield Label("", id="status-label")
            with Horizontal(id="btn-row"):
                yield Button("◄ Back", id="btn-back")
                yield Button("▶  Start Copy", id="btn-start", variant="primary")
        yield Static("Files copied read-only — originals untouched", id="footer")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-back":
            self.app.pop_screen()
        elif bid == "btn-start":
            self.query_one("#btn-start").disabled = True
            self.query_one("#btn-back").disabled = True
            self._do_copy()
        elif bid == "btn-analyze":
            from app.screens.ai_context import AIContextScreen
            self.app.push_screen(AIContextScreen())

    def watch_copied(self, value: int) -> None:
        bar = self.query_one("#copy-bar", ProgressBar)
        bar.progress = value
        self.query_one("#status-label", Label).update(
            f"Copying… {value} / {self.total}"
        )

    def _progress_cb(self, idx: int, total: int, filepath: str) -> None:
        self.call_from_thread(setattr, self, "copied", idx)
        self.call_from_thread(setattr, self, "total", total)
        short = filepath[-58:] if len(filepath) > 58 else filepath
        self.call_from_thread(
            self.query_one("#current-file", Label).update, short
        )

    @work(thread=True)
    def _do_copy(self) -> None:
        dest = copy_matched_files(
            self.app.matches,
            self.app.log_paths,
            self.app.search_term,
            progress_callback=self._progress_cb,
        )
        self.app.lookup_folder = dest
        self.call_from_thread(self._on_copy_done, str(dest))

    def _on_copy_done(self, dest: str) -> None:
        self._done = True
        self.query_one("#status-label", Label).update(
            f"[green]✓  Done![/green]  Saved to  [bold]{dest}[/bold]"
        )
        self.query_one("#dest-label", Label).update(f"[bold]{dest}[/bold]")
        # Swap buttons
        btn_row = self.query_one("#btn-row", Horizontal)
        btn_row.remove_children()
        btn_row.mount(Button("◄ Back to Results", id="btn-back"))
        btn_row.mount(
            Button("Analyze & Recommend ►", id="btn-analyze", variant="primary")
        )
