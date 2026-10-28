"""Find duplicate files: group by size first, then by content hash."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from docscanner.scanner import FileRecord

CHUNK_SIZE = 1024 * 1024


def hash_file(path: Path) -> str | None:
    """SHA-256 of a file's contents, or None if it can't be read."""
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def find_duplicates(records: Iterable[FileRecord]) -> list[list[FileRecord]]:
    """Return groups of files with identical contents (each group has 2+ files)."""
    by_size: dict[int, list[FileRecord]] = defaultdict(list)
    for rec in records:
        if rec.size > 0:
            by_size[rec.size].append(rec)

    groups: list[list[FileRecord]] = []
    for same_size in by_size.values():
        if len(same_size) < 2:
            continue
        by_hash: dict[str, list[FileRecord]] = defaultdict(list)
        for rec in same_size:
            if digest := hash_file(rec.path):
                by_hash[digest].append(rec)
        groups.extend(g for g in by_hash.values() if len(g) > 1)
    return groups
