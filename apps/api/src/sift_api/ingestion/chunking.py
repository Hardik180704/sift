"""Deterministic, page-aware document chunking."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid5

from sift_api.ingestion.parsing import ParsedPage

CHUNK_NAMESPACE = UUID("a1ff78b8-b4e4-4aa5-9b50-fc2d98175a3d")
MAX_CHUNK_CHARS = 2_000


@dataclass(frozen=True)
class Chunk:
    id: UUID
    index: int
    page_number: int
    text: str


def chunk_pages(document_version_id: UUID, pages: list[ParsedPage]) -> list[Chunk]:
    """Split pages on paragraph boundaries with deterministic retry-safe IDs."""
    chunks: list[Chunk] = []
    for page in pages:
        paragraphs = [part.strip() for part in page.text.split("\n") if part.strip()]
        buffer = ""
        for paragraph in paragraphs:
            candidate = f"{buffer}\n{paragraph}".strip()
            if buffer and len(candidate) > MAX_CHUNK_CHARS:
                index = len(chunks)
                chunks.append(
                    Chunk(
                        uuid5(CHUNK_NAMESPACE, f"{document_version_id}:{index}"),
                        index,
                        page.number,
                        buffer,
                    )
                )
                buffer = paragraph
            else:
                buffer = candidate
        if buffer:
            index = len(chunks)
            chunks.append(
                Chunk(
                    uuid5(CHUNK_NAMESPACE, f"{document_version_id}:{index}"),
                    index,
                    page.number,
                    buffer,
                )
            )
    return chunks
