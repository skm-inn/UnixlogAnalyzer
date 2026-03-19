"""Screen 2 — Log path input (up to 5 paths)."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static
from textual.containers import Vertical, Horizontal

from app.utils.validators import validate_path

NUM_PATHS = 5


class LogPathsScreen(Screen):
    DEFAULT_CSS = """
    LogPathsScreen {
        align: center middle;
    }
    #header {
        dock: top;
        height: 3;
        background: $panel;
        color: $accent;
        content-align: center middle;
        padding: 0 2;
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
        width: 72;
        border: solid $border;
        background: $panel;
        padding: 1 2;
        margin: 1 0;
    }
    .path-row {
        height: 3;
        margin-bottom: 1;
    }
    .path-label {
        width: 12;
        content-align: left middle;
        color: $text-muted;
    }
    .path-input {
        width: 1fr;
    }
    .status-icon {
        width: 4;
        content-align: center middle;
    }
    #hint {
        color: $text-muted;
        padding: 1 0 0 0;
    }
    #btn-row {
        align: center middle;
        height: 5;
        padding: 1 0;
    }
    #btn-back { margin-right: 2; }
    #btn-next { min-width: 20; }
    """

    def compose(self) -> ComposeResult:
        yield Static("Step 1 of 3  —  Log File Paths", id="header")
        with Vertical(id="form-panel"):
            yield Label("Enter up to 5 log directory paths  (Path 1 is required):", id="hint")
            for i in range(1, NUM_PATHS + 1):
                with Horizontal(classes="path-row"):
                    required = " *" if i == 1 else "  "
                    yield Label(f"Path {i}{required}", classes="path-label")
                    yield Input(
                        placeholder=f"/var/log/path{i}",
                        id=f"path-{i}",
                        classes="path-input",
                    )
                    yield Label("", id=f"icon-{i}", classes="status-icon")
            with Horizontal(id="btn-row"):
                yield Button("◄ Back", id="btn-back")
                yield Button("Validate & Next ►", id="btn-next", variant="primary")
        yield Static("Tab: next field  ·  Ctrl+Q: quit  ·  F1: help", id="footer")

    def on_input_changed(self, event: Input.Changed) -> None:
        self._validate_input(event.input)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._try_next()

    def _validate_input(self, inp: Input) -> None:
        idx = inp.id.split("-")[1]
        icon = self.query_one(f"#icon-{idx}", Label)
        value = inp.value.strip()
        if not value:
            icon.update("")
            inp.remove_class("invalid-input")
            return
        valid, _ = validate_path(value)
        if valid:
            icon.update("[green]✓[/green]")
            inp.remove_class("invalid-input")
        else:
            icon.update("[red]✗[/red]")
            inp.add_class("invalid-input")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-next":
            self._try_next()

    def _try_next(self) -> None:
        paths = []
        for i in range(1, NUM_PATHS + 1):
            val = self.query_one(f"#path-{i}", Input).value.strip()
            if val:
                ok, _ = validate_path(val)
                if ok:
                    paths.append(val)

        if not paths:
            self.notify("Please enter at least one valid path.", severity="error")
            return

        self.app.log_paths = paths
        from app.screens.criteria import SearchCriteriaScreen
        self.app.push_screen(SearchCriteriaScreen())
