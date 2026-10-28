"""Find duplicate files: group by size, then by a quick partial hash, then by full hash."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path

from docscanner.scanner import FileRecord

CHUNK_SIZE = 1024 * 1024
PARTIAL_SIZE = 64 * 1024

# Called as progress(stage, total) once per stage, then progress(stage, None) per file done.
ProgressFn = Callable[[str, int | None], None]


def hash_file(path: Path, limit: int | None = None) -> str | None:
    """SHA-256 of a file's contents (or its first `limit` bytes), or None if unreadable."""
    h = hashlib.sha256()
    remaining = limit
    try:
        with path.open("rb") as f:
            while remaining is None or remaining > 0:
                size = CHUNK_SIZE if remaining is None else min(CHUNK_SIZE, remaining)
                chunk = f.read(size)
                if not chunk:
                    break
                h.update(chunk)
                if remaining is not None:
                    remaining -= len(chunk)
    except OSError:
        return None
    return h.hexdigest()


def _refine(
    groups: list[list[FileRecord]],
    key: Callable[[FileRecord], str | None],
    stage: str,
    progress: ProgressFn | None,
) -> list[list[FileRecord]]:
    """Split each group by `key`, keeping only sub-groups with 2+ files."""
    if progress:
        progress(stage, sum(len(g) for g in groups))
    refined: list[list[FileRecord]] = []
    for group in groups:
        buckets: dict[str, list[FileRecord]] = defaultdict(list)
        for rec in group:
            if (k := key(rec)) is not None:
                buckets[k].append(rec)
            if progress:
                progress(stage, None)
        refined.extend(b for b in buckets.values() if len(b) > 1)
    return refined


def find_duplicates(
    records: Iterable[FileRecord], progress: ProgressFn | None = None
) -> list[list[FileRecord]]:
    """Return groups of files with identical contents (each group has 2+ files)."""
    by_size: dict[int, list[FileRecord]] = defaultdict(list)
    for rec in records:
        if rec.size > 0:
            by_size[rec.size].append(rec)
    groups = [g for g in by_size.values() if len(g) > 1]

    groups = _refine(groups, lambda r: hash_file(r.path, PARTIAL_SIZE), "Quick check", progress)
    # Files no bigger than the partial read are already fully compared.
    small = [g for g in groups if g[0].size <= PARTIAL_SIZE]
    large = [g for g in groups if g[0].size > PARTIAL_SIZE]
    return small + _refine(large, lambda r: hash_file(r.path), "Full compare", progress)
