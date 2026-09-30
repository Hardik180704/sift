"""Explicit contracts for document ingestion endpoints and workflows."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    """Metadata required before the browser uploads a private object."""

    filename: str = Field(min_length=1, max_length=512)
    mime_type: str = Field(
        pattern=r"^(application/pdf|application/vnd\.openxmlformats-officedocument\.wordprocessingml\.document|text/plain)$"
    )
    size_bytes: int = Field(gt=0, le=52_428_800)
    checksum_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")


class UploadResponse(BaseModel):
    """A single-use private-object upload target for the authenticated caller."""

    document_id: UUID
    storage_key: str
    signed_upload_url: str
    signed_upload_token: str


class UploadConfirmationResponse(BaseModel):
    """Accepted confirmation after the browser has uploaded its object."""

    document_id: UUID
    state: str
