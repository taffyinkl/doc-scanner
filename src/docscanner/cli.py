"""Command-line interface: `docscanner scan`, `docscanner dupes`, `docscanner drives`."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from docscanner.categorise import categorise
from docscanner.duplicates import find_duplicates
from docscanner.scanner import list_drives, scan

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
    counts = Counter(categorise(rec) for rec in scan(roots))
    table = Table("Category", "Files")
    for category, n in counts.most_common():
        table.add_row(category, str(n))
    console.print(table)


@app.command()
def dupes(roots: Roots) -> None:
    """Find files with identical contents."""
    groups = find_duplicates(scan(roots))
    if not groups:
        console.print("No duplicates found.")
        return
    wasted = 0
    for group in groups:
        wasted += group[0].size * (len(group) - 1)
        console.print(f"[bold]{len(group)} copies, {group[0].size:,} bytes each[/bold]")
        for rec in group:
            console.print(f"  {rec.path}")
    console.print(f"\n{len(groups)} duplicate groups, {wasted:,} bytes reclaimable.")


if __name__ == "__main__":
    app()
