"""Walk drives and folders, yielding file records."""

from __future__ import annotations

import os
import string
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Folders that are never worth scanning and often throw permission errors.
DEFAULT_EXCLUDES = {
    "$Recycle.Bin",
    "System Volume Information",
    "Windows",
    "Program Files",
    "Program Files (x86)",
    "ProgramData",
    "AppData",
    "node_modules",
    ".git",
    "__pycache__",
}


@dataclass(frozen=True)
class FileRecord:
    path: Path
    size: int
    modified: datetime
    created: datetime

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()


def list_drives() -> list[Path]:
    """Return available drive roots (C:\\, D:\\, ... on Windows; / elsewhere)."""
    if sys.platform == "win32":
        return [Path(f"{d}:\\") for d in string.ascii_uppercase if Path(f"{d}:\\").exists()]
    return [Path("/")]


def scan(
    roots: Iterable[Path],
    extensions: set[str] | None = None,
    excludes: set[str] = DEFAULT_EXCLUDES,
) -> Iterator[FileRecord]:
    """Yield a FileRecord for every file under the given roots.

    extensions: optional filter like {".pdf", ".docx"} (lower-case, with dot).
    Unreadable folders and files are skipped silently.
    """
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(Path(root).resolve(), onerror=lambda _e: None):
            # Prune excluded folders in place so os.walk doesn't descend into them.
            dirnames[:] = [d for d in dirnames if d not in excludes]
            for name in filenames:
                path = Path(dirpath, name)
                if extensions and path.suffix.lower() not in extensions:
                    continue
                try:
                    st = path.stat()
                except OSError:
                    continue
                yield FileRecord(
                    path=path,
                    size=st.st_size,
                    modified=datetime.fromtimestamp(st.st_mtime),
                    created=datetime.fromtimestamp(st.st_ctime),
                )
