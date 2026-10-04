"""Authenticated document upload creation and confirmation."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import httpx
from supabase import Client, create_client

from sift_api.config import Settings
from sift_api.ingestion.schemas import UploadRequest, UploadResponse


class UploadService:
    """Creates ownership-scoped private upload targets."""

    def __init__(self, settings: Settings) -> None:
        if settings.supabase_url is None:
            raise RuntimeError("Supabase configuration is unavailable")
        self._settings = settings
        self._client: Client = create_client(
            str(settings.supabase_url), settings.require_supabase_service_role_key()
        )

    def initiate(self, user_id: UUID, request: UploadRequest) -> UploadResponse:
        """Persist document metadata before returning a user-scoped upload target."""
        document_id = uuid4()
        storage_key = f"{user_id}/{document_id}/v1/{request.filename}"
        self._client.table("documents").insert(
            {
                "id": str(document_id),
                "user_id": str(user_id),
                "original_filename": request.filename,
                "mime_type": request.mime_type,
                "size_bytes": request.size_bytes,
                "storage_key": storage_key,
                "checksum_sha256": request.checksum_sha256,
                "state": "UPLOADED",
            }
        ).execute()
        self._client.table("document_versions").insert(
            {
                "document_id": str(document_id),
                "user_id": str(user_id),
                "version_number": 1,
                "storage_key": storage_key,
                "checksum_sha256": request.checksum_sha256,
            }
        ).execute()
        signed: Any = self._client.storage.from_("documents").create_signed_upload_url(storage_key)
        signed_url = signed.get("signedUrl") or signed.get("signed_url") or signed.get("signedURL")
        if not signed_url or not signed.get("token"):
            raise RuntimeError("Supabase did not create a signed upload target")
        return UploadResponse(
            document_id=document_id,
            storage_key=storage_key,
            signed_upload_url=str(signed_url),
            signed_upload_token=str(signed["token"]),
        )

    def confirm(self, user_id: UUID, document_id: UUID) -> None:
        """Idempotently ingest: queue uploads and re-deliver queued retries."""
        result = (
            self._client.table("documents")
            .update({"state": "QUEUED"})
            .eq("id", str(document_id))
            .eq("user_id", str(user_id))
            .eq("state", "UPLOADED")
            .execute()
        )
        if not result.data:
            queued = (
                self._client.table("documents")
                .update({"state": "QUEUED", "updated_at": "now()"})
                .eq("id", str(document_id))
                .eq("user_id", str(user_id))
                .eq("state", "QUEUED")
                .execute()
            )
            if not queued.data:
                raise LookupError("Document is not available for ingestion")
        else:
            self._client.table("document_jobs").insert(
                {"document_id": str(document_id), "user_id": str(user_id), "state": "QUEUED"}
            ).execute()
        response = httpx.post(
            self._settings.inngest_event_endpoint,
            json={
                "name": "document.ingest",
                "data": {"document_id": str(document_id), "user_id": str(user_id)},
            },
            timeout=10.0,
        )
        response.raise_for_status()
