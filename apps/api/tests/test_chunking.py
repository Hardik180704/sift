from uuid import UUID

from sift_api.ingestion.chunking import chunk_pages
from sift_api.ingestion.parsing import ParsedPage


def test_chunk_ids_are_deterministic_and_page_scoped() -> None:
    version_id = UUID("d03d0a04-020d-44c6-a2bb-47ca9f7d7c41")
    pages = [ParsedPage(2, "First paragraph.\nSecond paragraph.")]

    first = chunk_pages(version_id, pages)
    second = chunk_pages(version_id, pages)

    assert first == second
    assert first[0].page_number == 2
    assert first[0].text == "First paragraph.\nSecond paragraph."
