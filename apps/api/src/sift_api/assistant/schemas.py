"""Typed grounded-assistant API contracts."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from sift_api.retrieval.schemas import SourceEvidence


class AssistantRequest(BaseModel):
    """A question linked to an optional user-owned conversation."""

    question: str = Field(min_length=1, max_length=4_000)
    conversation_id: UUID | None = None


class Citation(BaseModel):
    """Citation to a source chunk that supports the answer."""

    chunk_id: UUID
    document_id: UUID
    page_number: int | None
    quote: str


class AssistantResponse(BaseModel):
    """A structured answer that distinguishes grounded evidence from uncertainty."""

    conversation_id: UUID
    answer: str
    citations: list[Citation]
    insufficient_evidence: bool
    sources: list[SourceEvidence]
