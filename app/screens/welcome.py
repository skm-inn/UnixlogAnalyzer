"""Screen 1 — Welcome / splash screen."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, Static


BANNER = """
 ██╗      ██████╗  ██████╗      █████╗ ███╗   ██╗ █████╗ ██╗  ██╗   ██╗███████╗███████╗██████╗
 ██║     ██╔═══██╗██╔════╝     ██╔══██╗████╗  ██║██╔══██╗██║  ╚██╗ ██╔╝╚════██║██╔════╝██╔══██╗
 ██║     ██║   ██║██║  ███╗    ███████║██╔██╗ ██║███████║██║   ╚████╔╝     ██╔╝█████╗  ██████╔╝
 ██║     ██║   ██║██║   ██║    ██╔══██║██║╚██╗██║██╔══██║██║    ╚██╔╝     ██╔╝ ██╔══╝  ██╔══██╗
 ███████╗╚██████╔╝╚██████╔╝    ██║  ██║██║ ╚████║██║  ██║███████╗██║      ██║  ███████╗██║  ██║
 ╚══════╝ ╚═════╝  ╚═════╝     ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝      ╚═╝  ╚══════╝╚═╝  ╚═╝
"""


class WelcomeScreen(Screen):
    BINDINGS = [("enter", "start", "Start")]

    DEFAULT_CSS = """
    WelcomeScreen {
        align: center middle;
    }
    #banner {
        color: $accent;
        text-align: center;
        padding: 1 2;
    }
    #tagline {
        color: $text-muted;
        text-align: center;
        padding: 0 2;
    }
    #version {
        color: $text-muted;
        text-align: center;
        padding: 0 2 1 2;
    }
    #start-btn {
        margin: 2 auto;
        min-width: 24;
    }
    #hint {
        color: $text-muted;
        text-align: center;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(BANNER, id="banner")
        yield Label("Unix Log Search & AI Analysis Tool", id="tagline")
        yield Label("v1.0.0  ·  github.com/skm-inn/UnixlogAnalyzer", id="version")
        yield Button("▶  Start", id="start-btn", variant="primary")
        yield Label("Ctrl+Q: Quit  ·  F1: Help", id="hint")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-btn":
            self.action_start()

    def action_start(self) -> None:
        from app.screens.paths import LogPathsScreen
        self.app.push_screen(LogPathsScreen())
