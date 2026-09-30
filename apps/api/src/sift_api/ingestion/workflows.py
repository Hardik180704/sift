"""Inngest durable document-ingestion workflow registration."""

from __future__ import annotations

import inngest

inngest_client = inngest.Inngest(app_id="sift-api")


@inngest_client.create_function(
    fn_id="document-ingest",
    trigger=inngest.TriggerEvent(event="document.ingest"),
)
async def ingest_document(ctx: inngest.Context) -> dict[str, str]:
    """Durable ingestion entrypoint; event payloads contain identifiers only."""
    document_id = str(ctx.event.data["document_id"])
    user_id = str(ctx.event.data["user_id"])
    return {"document_id": document_id, "user_id": user_id, "state": "QUEUED"}
