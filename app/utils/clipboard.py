"""OS clipboard access for Textual Input widgets.

Textual's built-in Ctrl+V reads from the app's internal clipboard
(whatever was cut/copied inside the TUI), not the OS clipboard.
This module provides an Input subclass that reads from the OS clipboard
via xclip / xsel / wl-paste / pbpaste, with a clear fallback message.
"""

import subprocess
from textual.widgets import Input
from textual.events import Paste


def _read_os_clipboard() -> str | None:
    """Try each platform clipboard tool and return text, or None on failure."""
    commands = [
        ["xclip", "-o", "-selection", "clipboard"],   # X11 (most Linux desktops)
        ["xsel", "--clipboard", "--output"],           # X11 alternative
        ["wl-paste", "--no-newline"],                  # Wayland
        ["pbpaste"],                                   # macOS
    ]
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return None


class ClipboardInput(Input):
    """Input widget with OS clipboard paste support (Ctrl+V)."""

    def action_paste(self) -> None:
        """Override: read from OS clipboard, then fall back to Textual clipboard."""
        text = _read_os_clipboard()
        if text is not None:
            # Strip trailing newline but preserve internal whitespace
            self.insert_text_at_cursor(text.rstrip("\n"))
        else:
            # Fallback: use Textual's internal clipboard (copy/cut within app)
            internal = self.app.clipboard
            if internal:
                self.insert_text_at_cursor(internal)
            else:
                self.notify(
                    "Could not read system clipboard.\n"
                    "Try: right-click → Paste  ·  Ctrl+Shift+V  ·  middle-click",
                    severity="warning",
                    timeout=5,
                )

    def _on_paste(self, event: Paste) -> None:
        """Handle terminal bracketed-paste sequences (right-click / Ctrl+Shift+V)."""
        if event.text:
            # Take only the first line (paths don't span multiple lines)
            line = event.text.splitlines()[0] if event.text.splitlines() else event.text
            selection = self.selection
            if selection.is_empty:
                self.insert_text_at_cursor(line)
            else:
                self.replace(line, *selection)
        event.stop()
