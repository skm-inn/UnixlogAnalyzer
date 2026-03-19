"""Copy matched log files into the lookup/ folder. Never modifies source files."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from app.utils.validators import sanitize_term


def copy_matched_files(
    matches: List[Tuple[str, int, str]],
    log_paths: List[str],
    search_term: str,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> Path:
    """
    Copy unique matched files to lookup/<term>_<YYYYMMDD_HHMMSS>/.
    Mirrors the directory structure relative to each log_path root.
    Source files are opened with shutil.copy2 (read-only semantics).
    Returns the destination Path.
    """
    term_safe = sanitize_term(search_term)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = Path("lookup") / f"{term_safe}_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)

    # Deduplicate by absolute path, preserving order
    unique_files: List[str] = list(dict.fromkeys(m[0] for m in matches))
    total = len(unique_files)

    for idx, filepath in enumerate(unique_files, 1):
        if progress_callback:
            progress_callback(idx, total, filepath)

        target = _resolve_target(filepath, log_paths, dest)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(filepath, target)  # preserves metadata, never modifies source

    return dest


def _resolve_target(filepath: str, log_paths: List[str], dest: Path) -> Path:
    """Compute mirrored destination path preserving relative directory structure."""
    src = Path(filepath)
    for log_path in log_paths:
        if not log_path:
            continue
        try:
            rel = src.relative_to(log_path)
            return dest / rel
        except ValueError:
            continue
    # Fallback: copy to destination root with original filename
    return dest / src.name
