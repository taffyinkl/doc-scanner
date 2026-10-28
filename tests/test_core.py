from pathlib import Path

from docscanner.categorise import categorise
from docscanner.duplicates import find_duplicates
from docscanner.scanner import scan


def test_scan_and_categorise(tmp_path: Path) -> None:
    (tmp_path / "a.pdf").write_bytes(b"pdf")
    (tmp_path / "b.xlsx").write_bytes(b"xlsx")
    records = {r.path.name: r for r in scan([tmp_path])}
    assert categorise(records["a.pdf"]) == "Documents"
    assert categorise(records["b.xlsx"]) == "Spreadsheets"


def test_scan_skips_excluded_folders(tmp_path: Path) -> None:
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "x.txt").write_text("x")
    assert list(scan([tmp_path])) == []


def test_find_duplicates(tmp_path: Path) -> None:
    (tmp_path / "one.txt").write_text("same content")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "two.txt").write_text("same content")
    (tmp_path / "other.txt").write_text("diff content")  # same size, different bytes
    groups = find_duplicates(scan([tmp_path]))
    assert len(groups) == 1
    assert {r.path.name for r in groups[0]} == {"one.txt", "two.txt"}


def test_find_duplicates_large_files_differ_after_partial(tmp_path: Path) -> None:
    head = b"x" * (64 * 1024)
    (tmp_path / "a.bin").write_bytes(head + b"tail-1")
    (tmp_path / "b.bin").write_bytes(head + b"tail-1")
    (tmp_path / "c.bin").write_bytes(head + b"tail-2")  # same size and same first 64 KB
    groups = find_duplicates(scan([tmp_path]))
    assert len(groups) == 1
    assert {r.path.name for r in groups[0]} == {"a.bin", "b.bin"}
