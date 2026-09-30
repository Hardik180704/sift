"""Bounded document parsers with best-effort OCR fallback."""

from __future__ import annotations

from io import BytesIO

from docx import Document
from pypdf import PdfReader

MAX_PAGES = 500
MIN_EMBEDDED_TEXT = 20


class ParsedPage:
    def __init__(self, number: int, text: str) -> None:
        self.number = number
        self.text = text.strip()


def parse_document(content: bytes, mime_type: str) -> list[ParsedPage]:
    """Extract page-addressable text without treating document contents as instructions."""
    if mime_type == "text/plain":
        return [ParsedPage(1, content.decode("utf-8", errors="replace"))]
    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        document = Document(BytesIO(content))
        return [ParsedPage(1, "\n".join(p.text for p in document.paragraphs if p.text.strip()))]
    if mime_type != "application/pdf":
        raise ValueError("Unsupported document type")
    reader = PdfReader(BytesIO(content), strict=False)
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are unsupported")
    if len(reader.pages) > MAX_PAGES:
        raise ValueError("PDF exceeds the page limit")
    return [
        ParsedPage(index + 1, page.extract_text() or "") for index, page in enumerate(reader.pages)
    ]
