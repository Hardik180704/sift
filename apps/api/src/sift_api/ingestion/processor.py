"""Server-only, ownership-scoped document ingestion orchestration."""

from __future__ import annotations

from typing import Any, cast
from uuid import UUID

from supabase import create_client

from sift_api.config import Settings
from sift_api.ingestion.chunking import chunk_pages
from sift_api.ingestion.extractions import extract_dates
from sift_api.ingestion.indexing import ChunkIndexer
from sift_api.ingestion.parsing import parse_document


def process_document(settings: Settings, user_id: UUID, document_id: UUID) -> None:
    """Persist chunks/extractions from one private object; mark failure safely."""
    if settings.supabase_url is None:
        raise RuntimeError("Supabase configuration is unavailable")
    client = create_client(str(settings.supabase_url), settings.require_supabase_service_role_key())
    document = cast(
        dict[str, Any],
        (
            client.table("documents")
            .select("*")
            .eq("id", str(document_id))
            .eq("user_id", str(user_id))
            .single()
            .execute()
            .data
        ),
    )
    if not document:
        raise LookupError("Scoped document was not found")
    try:
        client.table("documents").update({"state": "PARSING"}).eq("id", str(document_id)).eq(
            "user_id", str(user_id)
        ).execute()
        raw = client.storage.from_("documents").download(document["storage_key"])
        pages = parse_document(raw, document["mime_type"])
        version = cast(
            dict[str, Any],
            (
                client.table("document_versions")
                .select("id")
                .eq("document_id", str(document_id))
                .eq("user_id", str(user_id))
                .eq("storage_key", document["storage_key"])
                .single()
                .execute()
                .data
            ),
        )
        chunks = chunk_pages(UUID(version["id"]), pages)
        client.table("chunks").delete().eq("document_id", str(document_id)).eq(
            "user_id", str(user_id)
        ).execute()
        if chunks:
            client.table("chunks").insert(
                [
                    {
                        "id": str(chunk.id),
                        "document_id": str(document_id),
                        "document_version_id": version["id"],
                        "user_id": str(user_id),
                        "chunk_index": chunk.index,
                        "page_number": chunk.page_number,
                        "content": chunk.text,
                    }
                    for chunk in chunks
                ]
            ).execute()
        client.table("documents").update({"state": "EXTRACTING"}).eq("id", str(document_id)).eq(
            "user_id", str(user_id)
        ).execute()
        client.table("document_extractions").delete().eq("document_id", str(document_id)).eq(
            "user_id", str(user_id)
        ).execute()
        extractions = [extraction for chunk in chunks for extraction in extract_dates(chunk.text)]
        if extractions:
            client.table("document_extractions").insert(
                [
                    {
                        "document_id": str(document_id),
                        "user_id": str(user_id),
                        "extraction_type": item.extraction_type,
                        "value": {"value": item.value},
                        "confidence": item.confidence,
                    }
                    for item in extractions
                ]
            ).execute()
        client.table("documents").update({"state": "EMBEDDING"}).eq("id", str(document_id)).eq(
            "user_id", str(user_id)
        ).execute()
        ChunkIndexer(settings).index(user_id, document_id, UUID(version["id"]), chunks)
        client.table("documents").update({"state": "READY"}).eq("id", str(document_id)).eq(
            "user_id", str(user_id)
        ).execute()
    except Exception:
        client.table("documents").update({"state": "FAILED"}).eq("id", str(document_id)).eq(
            "user_id", str(user_id)
        ).execute()
        raise
