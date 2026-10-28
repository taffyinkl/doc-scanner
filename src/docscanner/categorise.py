"""Assign files to categories. Starts with extension rules; content rules come later."""

from __future__ import annotations

from docscanner.scanner import FileRecord

CATEGORIES: dict[str, set[str]] = {
    "Documents": {".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md"},
    "Spreadsheets": {".xls", ".xlsx", ".ods", ".csv"},
    "Presentations": {".ppt", ".pptx", ".odp"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".heic", ".webp"},
    "Email": {".eml", ".msg", ".pst"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
}


def categorise(record: FileRecord) -> str:
    for category, exts in CATEGORIES.items():
        if record.extension in exts:
            return category
    return "Other"
