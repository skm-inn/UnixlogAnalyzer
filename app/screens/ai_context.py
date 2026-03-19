"""Screen 7 — AI context input + tier detection."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static, TextArea
from textual.containers import Vertical, Horizontal

from app.core.ai_analyzer import detect_ai_tier, get_tier_label


class AIContextScreen(Screen):
    DEFAULT_CSS = """
    AIContextScreen {
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
    #ctx-panel {
        width: 70;
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
    TextArea {
        height: 5;
        margin-bottom: 1;
    }
    #tier-box {
        border: solid $border;
        padding: 1 2;
        margin-bottom: 1;
    }
    #tier-label {
        color: $accent;
    }
    #tier-desc {
        color: $text-muted;
    }
    #btn-row {
        align: center middle;
        height: 5;
        padding: 1 0;
    }
    #btn-back   { margin-right: 2; }
    #btn-analyze { min-width: 20; }
    """

    def compose(self) -> ComposeResult:
        tier = detect_ai_tier()
        tier_lbl = get_tier_label(tier)

        tier_descs = {
            "huggingface": "Uses HuggingFace Inference API — requires HUGGINGFACE_API_TOKEN.",
            "ollama": "Uses Ollama local model — no internet required.",
            "prompt_export": "No AI available — will export a ready-to-paste prompt file.",
        }

        yield Static("AI Analysis — Context", id="header")
        with Vertical(id="ctx-panel"):
            yield Label("System Context  (optional)", classes="field-label")
            yield Label(
                "Describe the server/application type to help the AI give better analysis.",
                classes="field-note",
            )
            yield TextArea(id="context-input")

            with Vertical(id="tier-box"):
                yield Label(f"AI Engine:  [bold]{tier_lbl}[/bold]", id="tier-label")
                yield Label(tier_descs.get(tier, ""), id="tier-desc")

            with Horizontal(id="btn-row"):
                yield Button("◄ Back", id="btn-back")
                yield Button("Analyze ►", id="btn-analyze", variant="primary")
        yield Static("Tab: next field  ·  Ctrl+Q: quit  ·  F1: help", id="footer")

    def on_mount(self) -> None:
        self.query_one("#context-input", TextArea).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-analyze":
            ctx = self.query_one("#context-input", TextArea).text.strip()
            self.app.user_context = ctx
            from app.screens.ai_progress import AIProgressScreen
            self.app.push_screen(AIProgressScreen())
