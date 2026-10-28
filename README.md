# docscanner

Scan a PC and its connected drives for documents: find duplicates, read content and dates,
then categorise and sort.

## Setup (Windows, PowerShell)

```powershell
git clone <your-repo-url> doc-scanner
cd doc-scanner
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev,extract]"
code .
```

If PowerShell blocks the activate script, run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Accept VS Code's prompt to install the recommended extensions.

## Usage

```powershell
docscanner drives                       # list drives
docscanner scan  "$HOME\Documents"      # count files per category
docscanner dupes "$HOME\Documents" D:\  # find duplicate files
```

## Development

```powershell
pytest          # run tests
ruff check .    # lint
ruff format .   # format
```

## Layout

| Module | Purpose |
| --- | --- |
| `scanner.py` | Walk drives/folders, collect size and dates |
| `duplicates.py` | Group by size, then SHA-256 hash |
| `categorise.py` | Assign a category (extension rules for now) |
| `extractors/` | Pull text from txt/pdf/docx (OCR planned) |
| `cli.py` | `docscanner` command |

## Roadmap

- [ ] SQLite index so rescans are incremental
- [ ] Full-text search over extracted content (SQLite FTS5)
- [ ] Content-based categorisation (invoices, receipts, letters...)
- [ ] OCR for scanned PDFs and images (`pip install -e ".[ocr]"` + Tesseract)
- [ ] Sort/move/copy into an organised folder tree, with dry-run and undo log
