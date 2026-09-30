"""Inngest durable document-ingestion workflow registration."""

from __future__ import annotations

from uuid import UUID

import inngest

from sift_api.config import get_settings
from sift_api.ingestion.processor import process_document

inngest_client = inngest.Inngest(app_id="sift-api")


async def run_processor(user_id: UUID, document_id: UUID) -> None:
    """Adapt synchronous managed-service adapters to Inngest's async step API."""
    process_document(get_settings(), user_id, document_id)


@inngest_client.create_function(
    fn_id="document-ingest",
    trigger=inngest.TriggerEvent(event="document.ingest"),
)
async def ingest_document(ctx: inngest.Context) -> dict[str, str]:
    """Durable ingestion entrypoint; event payloads contain identifiers only."""
    document_id = UUID(str(ctx.event.data["document_id"]))
    user_id = UUID(str(ctx.event.data["user_id"]))
    await ctx.step.run("process-document", lambda: run_processor(user_id, document_id))
    return {"document_id": str(document_id), "user_id": str(user_id), "state": "READY"}
