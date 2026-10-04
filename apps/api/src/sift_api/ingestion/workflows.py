"""Inngest durable document-ingestion workflow registration."""

from __future__ import annotations

import asyncio
import uuid

import inngest

from sift_api.config import Settings, get_settings
from sift_api.ingestion.processor import process_document

_settings = get_settings()


def _build_client(settings: Settings) -> inngest.Inngest:
    """Create the Inngest client; mode follows the declared environment."""
    if settings.inngest_signing_key is None:
        raise RuntimeError("Inngest signing key is required to serve the workflow endpoint")
    return inngest.Inngest(
        app_id="sift-api",
        signing_key=settings.inngest_signing_key.get_secret_value(),
        is_production=settings.environment == "production",
    )


inngest_client = _build_client(_settings)


async def run_processor(user_id: uuid.UUID, document_id: uuid.UUID) -> None:
    """Run blocking managed-service work off the event loop."""
    await asyncio.to_thread(process_document, get_settings(), user_id, document_id)


inngest_client = _build_client(_settings)


@inngest_client.create_function(
    fn_id="document-ingest",
    trigger=inngest.TriggerEvent(event="document.ingest"),
)
async def ingest_document(ctx: inngest.Context) -> dict[str, str]:
    """Durable ingestion entrypoint; event payloads contain identifiers only."""
    document_id = uuid.UUID(str(ctx.event.data["document_id"]))
    user_id = uuid.UUID(str(ctx.event.data["user_id"]))
    await ctx.step.run("process-document", lambda: run_processor(user_id, document_id))
    return {"document_id": str(document_id), "user_id": str(user_id), "state": "READY"}
