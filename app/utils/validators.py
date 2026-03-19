"""Input validators for log paths and file patterns."""

import os
import fnmatch
from typing import Tuple


def validate_path(path: str) -> Tuple[bool, str]:
    """Validate a log directory path. Returns (is_valid, message)."""
    if not path or not path.strip():
        return False, "Empty"
    path = path.strip()
    if not os.path.exists(path):
        return False, "Does not exist"
    if not os.path.isdir(path):
        return False, "Not a directory"
    if not os.access(path, os.R_OK):
        return False, "Not readable"
    return True, "OK"


def validate_file_pattern(pattern: str) -> Tuple[bool, str]:
    """Validate an optional file name glob pattern. Returns (is_valid, message)."""
    if not pattern or not pattern.strip():
        return True, "All files"
    try:
        fnmatch.fnmatch("test.log", pattern.strip())
        return True, f"Filter: {pattern.strip()}"
    except Exception as e:
        return False, f"Invalid pattern: {e}"


def sanitize_term(term: str) -> str:
    """Make a search term safe for use in folder names."""
    import re
    safe = re.sub(r"[^\w\-]", "_", term)
    return safe[:30] or "search"
