"""Command-line interface: `docscanner scan`, `docscanner dupes`, `docscanner drives`."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from docscanner.categorise import categorise
from docscanner.duplicates import find_duplicates
from docscanner.scanner import FileRecord, list_drives, scan

app = typer.Typer(help="Scan drives for documents, duplicates and categories.")
console = Console()

Roots = Annotated[list[Path], typer.Argument(help="Folders or drives to scan")]


@app.command()
def drives() -> None:
    """List the drives that can be scanned."""
    for d in list_drives():
        console.print(str(d))


@app.command("scan")
def scan_cmd(roots: Roots) -> None:
    """Count files per category under the given folders."""
    counts = Counter(categorise(rec) for rec in _listing_with_progress(roots))
    table = Table("Category", "Files")
    for category, n in counts.most_common():
        table.add_row(category, str(n))
    console.print(table)


def _listing_with_progress(roots: list[Path]) -> list[FileRecord]:
    """Walk the folders, showing a live count of files found and the current folder."""
    records: list[FileRecord] = []
    with Progress(
        SpinnerColumn(),
        TextColumn("Listing files: [bold]{task.completed:,}[/bold]"),
        TimeElapsedColumn(),
        TextColumn("[dim]{task.fields[folder]}"),
        console=console,
        transient=True,
    ) as bar:
        task = bar.add_task("list", folder="")
        for rec in scan(roots):
            records.append(rec)
            if len(records) % 200 == 0:
                bar.update(task, completed=len(records), folder=_shorten(rec.path.parent))
    console.print(f"Found {len(records):,} files.")
    return records


def _shorten(path: Path, width: int = 60) -> str:
    text = str(path)
    return text if len(text) <= width else "..." + text[-(width - 3) :]


@app.command()
def dupes(
    roots: Roots,
    output: Annotated[Path, typer.Option("--output", "-o", help="CSV file to write")] = Path(
        "dupes.csv"
    ),
) -> None:
    """Find files with identical contents and write them to a CSV file."""
    records = _listing_with_progress(roots)

    with Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TextColumn("left"),
        TimeRemainingColumn(),
        console=console,
    ) as bar:
        tasks: dict[str, TaskID] = {}

        def progress(stage: str, total: int | None) -> None:
            if total is not None:
                tasks[stage] = bar.add_task(stage, total=total)
            else:
                bar.advance(tasks[stage])

        groups = find_duplicates(records, progress)

    if not groups:
        console.print("No duplicates found.")
        return

    # Biggest wasted space first.
    groups.sort(key=lambda g: g[0].size * (len(g) - 1), reverse=True)
    output = output.resolve()
    with output.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["group", "copies", "size_bytes", "modified", "path"])
        for i, group in enumerate(groups, 1):
            for rec in group:
                writer.writerow(
                    [i, len(group), rec.size, rec.modified.isoformat(" ", "seconds"), rec.path]
                )

    wasted = sum(g[0].size * (len(g) - 1) for g in groups)
    console.print(
        f"{len(groups):,} duplicate groups, {wasted / 1e9:,.2f} GB reclaimable.\n"
        f"Results written to [bold]{output}[/bold]"
    )


if __name__ == "__main__":
    app()
