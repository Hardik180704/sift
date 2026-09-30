"""Bounded document parsers with best-effort OCR fallback."""

from __future__ import annotations

from io import BytesIO

import pytesseract
from docx import Document
from pdf2image import convert_from_bytes
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
    pages: list[ParsedPage] = []
    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if len(text.strip()) < MIN_EMBEDDED_TEXT:
            image = convert_from_bytes(
                content, dpi=200, first_page=index + 1, last_page=index + 1, timeout=30
            )[0]
            text = pytesseract.image_to_string(image, lang="eng", timeout=30)
        pages.append(ParsedPage(index + 1, text))
    return pages
