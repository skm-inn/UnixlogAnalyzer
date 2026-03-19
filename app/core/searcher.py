"""Core log file search engine. Opens files read-only. Never modifies the server."""

import os
import fnmatch
from typing import Generator, List, Optional, Set, Tuple


def is_binary(filepath: str, sample_size: int = 8192) -> bool:
    """Return True if the file appears to be binary (contains null bytes)."""
    try:
        with open(filepath, "rb") as f:
            return b"\x00" in f.read(sample_size)
    except (OSError, PermissionError):
        return True


def _walk_safe(
    log_path: str,
    seen_inodes: Set[Tuple[int, int]],
) -> Generator[Tuple[str, List[str], List[str]], None, None]:
    """os.walk with circular-symlink detection."""
    for root, dirs, files in os.walk(log_path, followlinks=True):
        try:
            stat = os.stat(root)
            key = (stat.st_dev, stat.st_ino)
            if key in seen_inodes:
                dirs.clear()
                continue
            seen_inodes.add(key)
        except OSError:
            dirs.clear()
            continue
        yield root, dirs, files


def count_files(
    log_paths: List[str],
    file_pattern: Optional[str] = None,
) -> int:
    """Count total searchable files across all paths (for progress bar)."""
    count = 0
    seen: Set[Tuple[int, int]] = set()
    for log_path in log_paths:
        if not log_path or not os.path.isdir(log_path):
            continue
        for _, _, files in _walk_safe(log_path, seen):
            for filename in files:
                if file_pattern and not fnmatch.fnmatch(filename, file_pattern):
                    continue
                count += 1
    return count


def search_logs(
    log_paths: List[str],
    search_term: str,
    file_pattern: Optional[str] = None,
    progress_callback: Optional[callable] = None,
) -> Generator[Tuple[str, int, str], None, None]:
    """
    Search log files for search_term (case-insensitive substring).
    Yields (absolute_filepath, line_number, line_text).
    Files are opened read-only. Binary files are skipped.
    progress_callback(filepath) is called for each file scanned.
    """
    term_lower = search_term.lower()
    seen: Set[Tuple[int, int]] = set()

    for log_path in log_paths:
        if not log_path or not os.path.isdir(log_path):
            continue
        for root, _, files in _walk_safe(log_path, seen):
            for filename in sorted(files):
                if file_pattern and not fnmatch.fnmatch(filename, file_pattern):
                    continue
                filepath = os.path.join(root, filename)
                if is_binary(filepath):
                    continue
                if progress_callback:
                    progress_callback(filepath)
                try:
                    with open(filepath, "r", errors="replace") as fh:
                        for lineno, line in enumerate(fh, 1):
                            if term_lower in line.lower():
                                yield (filepath, lineno, line.rstrip())
                except (OSError, PermissionError):
                    continue
