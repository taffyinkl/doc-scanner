"""Extract text from documents. Each extractor needs the optional `extract` extras."""

from __future__ import annotations

from pathlib import Path


def extract_text(path: Path) -> str | None:
    """Return the text content of a file, or None if unsupported or unreadable."""
    ext = path.suffix.lower()
    try:
        if ext in {".txt", ".md", ".csv"}:
            return path.read_text(encoding="utf-8", errors="replace")
        if ext == ".pdf":
            from pypdf import PdfReader

            return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        if ext == ".docx":
            import docx

            return "\n".join(p.text for p in docx.Document(str(path)).paragraphs)
    except Exception:
        return None
    return None
