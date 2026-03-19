"""Screen 9 — AI report viewer."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, Markdown, Static
from textual.containers import Vertical, Horizontal, ScrollableContainer


class AIReportScreen(Screen):
    DEFAULT_CSS = """
    AIReportScreen {
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
    #report-panel {
        width: 90%;
        height: 1fr;
        border: solid $border;
        background: $panel;
        padding: 0 1;
        margin: 1 0;
    }
    #report-scroll {
        height: 1fr;
    }
    Markdown {
        padding: 1 2;
    }
    #btn-row {
        align: center middle;
        height: 5;
        padding: 1 0;
        dock: bottom;
    }
    #btn-back { margin-right: 2; }
    #btn-new  { min-width: 20; }
    """

    def compose(self) -> ComposeResult:
        analysis = getattr(self.app, "analysis_text", "")
        prompt_path = getattr(self.app, "prompt_export_path", "")
        report_path = getattr(self.app, "report_path", "")

        if analysis:
            content = analysis
            header_text = "AI Analysis Report"
        elif prompt_path:
            content = (
                f"# Prompt Export\n\nNo AI engine was available.\n\n"
                f"A ready-to-paste prompt has been saved:\n\n"
                f"```\n{prompt_path}\n```\n\n"
                f"Copy that file and paste it into ChatGPT / Claude.ai / Gemini."
            )
            header_text = "Prompt Export"
        else:
            content = "No analysis available."
            header_text = "AI Report"

        if report_path:
            save_note = f"\n\n---\n*Saved to: `{report_path}`*"
            content += save_note

        yield Static(header_text, id="header")
        with Vertical(id="report-panel"):
            with ScrollableContainer(id="report-scroll"):
                yield Markdown(content, id="report-md")
            with Horizontal(id="btn-row"):
                yield Button("◄ Back", id="btn-back")
                yield Button("▶  New Search", id="btn-new", variant="primary")
        yield Static("↑↓: scroll  ·  Ctrl+Q: quit", id="footer")

    def on_mount(self) -> None:
        self.query_one("#report-scroll", ScrollableContainer).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-new":
            while len(self.app.screen_stack) > 1:
                self.app.pop_screen()
