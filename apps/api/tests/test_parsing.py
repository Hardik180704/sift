from unittest.mock import MagicMock, patch

from sift_api.ingestion.parsing import parse_document


def test_plain_text_parsing_preserves_text_as_page_one() -> None:
    pages = parse_document(b"Lease renewal date: 2027-01-15", "text/plain")

    assert [(page.number, page.text) for page in pages] == [(1, "Lease renewal date: 2027-01-15")]


@patch("sift_api.ingestion.parsing.pytesseract.image_to_string")
@patch("sift_api.ingestion.parsing.convert_from_bytes")
@patch("sift_api.ingestion.parsing.PdfReader")
def test_pdf_low_text_page_uses_ocr_fallback(
    reader_factory: MagicMock, convert: MagicMock, ocr: MagicMock
) -> None:
    reader = MagicMock()
    reader.is_encrypted = False
    reader.pages = [MagicMock(extract_text=lambda: "")]
    reader_factory.return_value = reader
    convert.return_value = [MagicMock()]
    ocr.return_value = "Scanned insurance policy"

    pages = parse_document(b"pdf", "application/pdf")

    assert pages[0].text == "Scanned insurance policy"
    convert.assert_called_once()
    ocr.assert_called_once()
