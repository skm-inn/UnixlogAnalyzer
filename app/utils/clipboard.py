"""OS clipboard access for Textual Input widgets.

Uses pyperclip (cross-platform: Windows, Linux X11/Wayland, macOS) as the
primary clipboard source.  Falls back to the Textual internal clipboard, then
to terminal bracketed-paste (Ctrl+Shift+V / right-click) which always works.
"""

from typing import Optional
from textual.widgets import Input
from textual.events import Paste


def _read_os_clipboard() -> Optional[str]:
    """Return OS clipboard text, or None if unavailable."""
    # 1. Try pyperclip (works on Windows, Linux desktop, macOS)
    try:
        import pyperclip
        text = pyperclip.paste()
        if text:
            return text
    except Exception:
        pass

    # 2. Fallback: subprocess clipboard tools for headless Linux/SSH
    import subprocess
    commands = [
        ["xclip", "-o", "-selection", "clipboard"],   # X11
        ["xsel", "--clipboard", "--output"],           # X11 alternative
        ["wl-paste", "--no-newline"],                  # Wayland
        ["pbpaste"],                                   # macOS
    ]
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue

    return None


class ClipboardInput(Input):
    """Input widget with OS clipboard paste support (Ctrl+V)."""

    def action_paste(self) -> None:
        """Paste from OS clipboard (pyperclip → subprocess tools → app clipboard)."""
        text = _read_os_clipboard()
        if text is not None:
            self.insert_text_at_cursor(text.rstrip("\n"))
            return

        # Last resort: Textual's internal clipboard (only set by cut/copy in-app)
        internal = self.app.clipboard
        if internal:
            self.insert_text_at_cursor(internal)
        else:
            self.notify(
                "Could not read system clipboard.\n"
                "Use Ctrl+Shift+V  or  right-click → Paste  in your terminal.",
                severity="warning",
                timeout=5,
            )
