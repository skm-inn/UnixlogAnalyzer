"""Directory browser modal — lets the user navigate and pick a log folder."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Label, Static
from textual.containers import Vertical, Horizontal


class BrowseScreen(ModalScreen):
    """Full-screen directory picker.  Dismisses with the selected path (str) or None."""

    DEFAULT_CSS = """
    BrowseScreen {
        align: center middle;
    }
    #browse-dialog {
        width: 84;
        height: 30;
        border: double $accent;
        background: $panel;
        padding: 1 2;
    }
    #browse-title {
        color: $accent;
        content-align: center middle;
        height: 2;
        border-bottom: solid $border;
        margin-bottom: 1;
    }
    #dir-tree {
        height: 1fr;
        border: solid $border;
        background: $background;
    }
    #selected-label {
        color: $text-muted;
        height: 2;
        padding: 1 0 0 0;
        overflow: hidden;
    }
    #browse-btn-row {
        align: center middle;
        height: 4;
        padding: 1 0 0 0;
    }
    #btn-browse-cancel { margin-right: 2; }
    #btn-browse-select { min-width: 16; }
    """

    def __init__(self, start_path: str = "/") -> None:
        super().__init__()
        self._start_path = start_path or "/"
        self._selected: str = ""

    def compose(self) -> ComposeResult:
        with Vertical(id="browse-dialog"):
            yield Static("Browse — Select a Log Directory", id="browse-title")
            yield DirectoryTree(self._start_path, id="dir-tree")
            yield Label(
                "Navigate the tree and select a directory",
                id="selected-label",
            )
            with Horizontal(id="browse-btn-row"):
                yield Button("Cancel", id="btn-browse-cancel")
                yield Button(
                    "Select ►",
                    id="btn-browse-select",
                    variant="primary",
                    disabled=True,
                )

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        self._selected = str(event.path)
        short = (
            self._selected[-70:] if len(self._selected) > 70 else self._selected
        )
        self.query_one("#selected-label", Label).update(
            f"[green]Selected:[/green]  {short}"
        )
        self.query_one("#btn-browse-select", Button).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-browse-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-browse-select":
            self.dismiss(self._selected if self._selected else None)
