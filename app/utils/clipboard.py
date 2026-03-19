"""OS clipboard access for Textual Input widgets.

HOW PASTE WORKS IN TEXTUAL OVER SSH (MobaXterm / PuTTY / etc.)
---------------------------------------------------------------
Textual binds Ctrl+V to action_paste(), which reads the app's INTERNAL
clipboard — it cannot access the remote user's OS clipboard over SSH.

The CORRECT way to paste over SSH is via terminal bracketed paste:
  - Right-click → Paste  (MobaXterm)
  - Shift+Insert          (MobaXterm / most SSH terminals)
  - Middle-click          (X11 terminals)

These send the text as an escape sequence (\x1b[200~…\x1b[201~) which
Textual's built-in _on_paste handler receives and inserts correctly.

For LOCAL (non-SSH) use, pyperclip reads the real OS clipboard on
Windows, Linux desktop (X11/Wayland), and macOS — so Ctrl+V works.
"""

import os
from typing import Optional
from textual.widgets import Input


def _is_ssh() -> bool:
    """Return True if running inside an SSH session."""
    return bool(os.environ.get("SSH_CLIENT") or os.environ.get("SSH_TTY"))


def _read_os_clipboard() -> Optional[str]:
    """Return OS clipboard text, or None if unavailable.

    Uses pyperclip (cross-platform) then subprocess tools as fallback.
    Always returns None rather than raising.
    """
    # pyperclip: works on Windows (win32api), Linux desktop (xclip/xsel/wl-paste), macOS
    try:
        import pyperclip
        text = pyperclip.paste()
        if text:
            return text
    except Exception:
        pass

    # Subprocess fallback for headless/unusual environments
    import subprocess
    for cmd in [
        ["xclip", "-o", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--output"],
        ["wl-paste", "--no-newline"],
        ["pbpaste"],
    ]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            if r.returncode == 0 and r.stdout:
                return r.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue

    return None


class ClipboardInput(Input):
    """Input widget with clipboard paste support.

    - LOCAL session : Ctrl+V reads the OS clipboard via pyperclip.
    - SSH session   : Ctrl+V shows a hint; use right-click or Shift+Insert
                      which send bracketed paste and are handled automatically.
    """

    def action_paste(self) -> None:
        """Ctrl+V handler — OS clipboard for local; hint for SSH."""
        if _is_ssh():
            # Over SSH there is no way to read the user's local clipboard.
            # Bracketed paste (right-click / Shift+Insert) is the correct path.
            self.notify(
                "SSH session detected — Ctrl+V cannot reach your local clipboard.\n"
                "Use  Right-click → Paste  or  Shift+Insert  instead.",
                severity="warning",
                timeout=6,
            )
            return

        # Local session: try OS clipboard via pyperclip
        text = _read_os_clipboard()
        if text is not None:
            self.insert_text_at_cursor(text.rstrip("\n"))
            return

        # Fallback: Textual's internal clipboard (set by cut/copy within the app)
        internal = self.app.clipboard
        if internal:
            self.insert_text_at_cursor(internal)
        else:
            self.notify(
                "Could not read system clipboard.\n"
                "Try: right-click → Paste  or  Shift+Insert",
                severity="warning",
                timeout=5,
            )
