"""Screen 2 — Log path input (up to 5 paths)."""

import os

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static
from textual.containers import Vertical, Horizontal

from app.utils.validators import validate_path
from app.utils.clipboard import ClipboardInput

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
        width: 84;
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
        width: 10;
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
    .browse-btn {
        width: 12;
        margin-left: 1;
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
            yield Label(
                "Enter up to 5 log directory paths  (Path 1 is required):"
                "  Type a path  OR  click [Browse]",
                id="hint",
            )
            for i in range(1, NUM_PATHS + 1):
                with Horizontal(classes="path-row"):
                    required = " *" if i == 1 else "  "
                    yield Label(f"Path {i}{required}", classes="path-label")
                    yield ClipboardInput(
                        placeholder=f"/var/log/path{i}",
                        id=f"path-{i}",
                        classes="path-input",
                    )
                    yield Label("", id=f"icon-{i}", classes="status-icon")
                    yield Button(
                        "Browse",
                        id=f"browse-{i}",
                        classes="browse-btn",
                    )
            with Horizontal(id="btn-row"):
                yield Button("◄ Back", id="btn-back")
                yield Button("Validate & Next ►", id="btn-next", variant="primary")
        yield Static(
            "Tab: next field  ·  Browse: pick folder  ·  Shift+Ins / right-click: paste  ·  Ctrl+Q: quit",
            id="footer",
        )

    def on_mount(self) -> None:
        self.query_one("#path-1", ClipboardInput).focus()

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
        bid = event.button.id
        if bid == "btn-back":
            self.app.pop_screen()
        elif bid == "btn-next":
            self._try_next()
        elif bid and bid.startswith("browse-"):
            idx = bid.split("-")[1]
            self._open_browser(idx)

    def _open_browser(self, idx: str) -> None:
        """Open the directory browser modal for path slot `idx`."""
        from app.screens.browse import BrowseScreen

        current = self.query_one(f"#path-{idx}", ClipboardInput).value.strip()
        # Start the tree at the current value (if valid) or the filesystem root
        if current and os.path.isdir(current):
            start = current
        else:
            start = "/"

        def _on_selected(path: str) -> None:
            if path:
                inp = self.query_one(f"#path-{idx}", ClipboardInput)
                inp.value = path
                inp.focus()
                self._validate_input(inp)

        self.app.push_screen(BrowseScreen(start), _on_selected)

    def _try_next(self) -> None:
        paths = []
        for i in range(1, NUM_PATHS + 1):
            val = self.query_one(f"#path-{i}", ClipboardInput).value.strip()
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
