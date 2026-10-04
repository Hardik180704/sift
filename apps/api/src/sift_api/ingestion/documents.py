"""User-scoped document listing for the library experience."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from supabase import Client, create_client

from sift_api.config import Settings
from sift_api.ingestion.schemas import UPLOADABLE_MIME_TYPES


class DocumentSummary(BaseModel):
    """A single row of the caller's document library."""

    id: UUID
    original_filename: str
    mime_type: str
    size_bytes: int
    state: str
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    """The caller's documents, newest first."""

    documents: list[DocumentSummary]


class DocumentService:
    """Reads only documents owned by the verified caller."""

    def __init__(self, settings: Settings) -> None:
        if settings.supabase_url is None:
            raise RuntimeError("Supabase configuration is unavailable")
        self._client: Client = create_client(
            str(settings.supabase_url), settings.require_supabase_service_role_key()
        )

    def list_documents(self, user_id: UUID) -> DocumentListResponse:
        """Return the caller's documents ordered newest first."""
        rows = (
            self._client.table("documents")
            .select("id, original_filename, mime_type, size_bytes, state, created_at, updated_at")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .execute()
            .data
        )
        documents = [DocumentSummary.model_validate(row) for row in rows or []]
        return DocumentListResponse(documents=documents)


__all__ = ["UPLOADABLE_MIME_TYPES", "DocumentListResponse", "DocumentService", "DocumentSummary"]
