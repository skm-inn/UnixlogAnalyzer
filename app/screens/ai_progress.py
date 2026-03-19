"""Screen 8 — AI analysis with live streaming output."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, Log, Static
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual import work

from app.core.ai_analyzer import (
    detect_ai_tier,
    assemble_log_content,
    stream_huggingface,
    stream_ollama,
    export_prompt,
    save_analysis_report,
)


class AIProgressScreen(Screen):
    DEFAULT_CSS = """
    AIProgressScreen {
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
    #ai-panel {
        width: 88%;
        height: 1fr;
        border: solid $border;
        background: $panel;
        padding: 1 2;
        margin: 1 0;
    }
    #phase-label {
        color: $accent;
        padding: 0 0 1 0;
    }
    #stream-log {
        height: 1fr;
        border: solid $border;
        background: $background;
    }
    #btn-row {
        align: center middle;
        height: 5;
        padding: 1 0;
        dock: bottom;
    }
    #btn-done { min-width: 16; }
    """

    _analysis_text: str = ""

    def compose(self) -> ComposeResult:
        yield Static("AI Analysis — Processing", id="header")
        with Vertical(id="ai-panel"):
            yield Label("Preparing log content…", id="phase-label")
            yield Log(id="stream-log", highlight=True, markup=False)
            with Horizontal(id="btn-row"):
                yield Button("View Report ►", id="btn-done", variant="primary", disabled=True)
        yield Static("Please wait — analysis may take 30-120 seconds", id="footer")

    def on_mount(self) -> None:
        self._run_analysis()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-done":
            from app.screens.ai_report import AIReportScreen
            self.app.push_screen(AIReportScreen())

    @work(thread=True)
    def _run_analysis(self) -> None:
        folder = self.app.lookup_folder
        term = self.app.search_term
        ctx = getattr(self.app, "user_context", "")
        tier = detect_ai_tier()

        # Phase 1: assemble log content
        self.call_from_thread(
            self.query_one("#phase-label", Label).update,
            "Assembling log content…",
        )
        log_content = assemble_log_content(folder, term)

        if tier == "prompt_export":
            self.call_from_thread(
                self.query_one("#phase-label", Label).update,
                "Exporting prompt file (no AI available)…",
            )
            out = export_prompt(folder, term, ctx, log_content)
            self.call_from_thread(
                self._append_log,
                f"No AI engine detected.\n\nPrompt file saved:\n{out}\n\n"
                "Copy this file and paste its contents into ChatGPT / Claude.ai / Gemini.",
            )
            self.app.analysis_text = ""
            self.app.prompt_export_path = str(out)
            self.call_from_thread(self._finish)
            return

        # Phase 2: stream from AI
        tier_names = {
            "huggingface": "HuggingFace Inference API",
            "ollama": "Ollama Local Model",
        }
        self.call_from_thread(
            self.query_one("#phase-label", Label).update,
            f"Streaming analysis from  {tier_names.get(tier, tier)}…",
        )

        collected = []
        stream_fn = stream_huggingface if tier == "huggingface" else stream_ollama

        for chunk in stream_fn(log_content, ctx, term):
            collected.append(chunk)
            self.call_from_thread(self._append_log, chunk)

        full_text = "".join(collected)

        # Phase 3: save report
        self.call_from_thread(
            self.query_one("#phase-label", Label).update,
            "Saving report…",
        )
        report_path = save_analysis_report(folder, full_text, term, tier, ctx)
        self.app.analysis_text = full_text
        self.app.report_path = str(report_path)

        self.call_from_thread(
            self._append_log,
            f"\n\n[Report saved: {report_path}]",
        )
        self.call_from_thread(self._finish)

    def _append_log(self, text: str) -> None:
        self.query_one("#stream-log", Log).write(text)

    def _finish(self) -> None:
        self.query_one("#phase-label", Label).update("[green]✓  Analysis complete![/green]")
        self.query_one("#btn-done", Button).disabled = False
        self.query_one("#btn-done").focus()
