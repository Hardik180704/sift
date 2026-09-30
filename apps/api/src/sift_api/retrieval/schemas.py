"""Explicit API contracts for source-grounded retrieval."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    """A document query owned by the authenticated caller."""

    query: str = Field(min_length=1, max_length=2_000)
    limit: int = Field(default=8, ge=1, le=20)


class SourceEvidence(BaseModel):
    """A page-addressable document chunk suitable for a typed citation."""

    chunk_id: UUID
    document_id: UUID
    page_number: int | None
    section: str | None
    content: str
    score: float


class RetrievalResponse(BaseModel):
    """Fused source evidence, never an unsupported generated answer."""

    sources: list[SourceEvidence]
