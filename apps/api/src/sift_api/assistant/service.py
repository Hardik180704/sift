"""Authenticated orchestration, persistence, and citation construction."""

from __future__ import annotations

from typing import Any, cast
from uuid import UUID, uuid4

from supabase import create_client

from sift_api.assistant.graph import build_graph
from sift_api.assistant.schemas import AssistantResponse, Citation
from sift_api.config import Settings
from sift_api.retrieval.service import RetrievalService


class AssistantService:
    """Runs traceable grounded responses for exactly one verified user."""

    def __init__(self, settings: Settings) -> None:
        if settings.supabase_url is None:
            raise RuntimeError("Supabase configuration is unavailable")
        self._settings = settings
        self._supabase = create_client(
            str(settings.supabase_url), settings.require_supabase_service_role_key()
        )

    def answer(
        self, user_id: UUID, question: str, conversation_id: UUID | None
    ) -> AssistantResponse:
        """Retrieve evidence, execute the bounded graph, and persist cited messages."""
        conversation = conversation_id or uuid4()
        if conversation_id is None:
            self._supabase.table("conversations").insert(
                {"id": str(conversation), "user_id": str(user_id)}
            ).execute()
        else:
            existing = (
                self._supabase.table("conversations")
                .select("id")
                .eq("id", str(conversation))
                .eq("user_id", str(user_id))
                .execute()
                .data
            )
            if not existing:
                raise LookupError("Conversation was not found")
        sources = RetrievalService(self._settings).retrieve(user_id, question, 8)
        graph = build_graph()
        state = cast(
            dict[str, Any], graph.invoke({"question": question, "sources": sources, "retries": 0})
        )
        citations = (
            [
                Citation(
                    chunk_id=source.chunk_id,
                    document_id=source.document_id,
                    page_number=source.page_number,
                    quote=source.content[:500],
                )
                for source in sources
            ]
            if not state["insufficient_evidence"]
            else []
        )
        self._persist(user_id, conversation, question, state["answer"], citations)
        return AssistantResponse(
            conversation_id=conversation,
            answer=state["answer"],
            citations=citations,
            insufficient_evidence=state["insufficient_evidence"],
            sources=sources,
        )

    def _persist(
        self,
        user_id: UUID,
        conversation_id: UUID,
        question: str,
        answer: str,
        citations: list[Citation],
    ) -> None:
        self._supabase.table("messages").insert(
            {
                "user_id": str(user_id),
                "conversation_id": str(conversation_id),
                "role": "USER",
                "content": question,
            }
        ).execute()
        response = (
            self._supabase.table("messages")
            .insert(
                {
                    "user_id": str(user_id),
                    "conversation_id": str(conversation_id),
                    "role": "ASSISTANT",
                    "content": answer,
                }
            )
            .execute()
        )
        message = cast(dict[str, Any], response.data[0])
        if citations:
            self._supabase.table("message_citations").insert(
                [
                    {
                        "message_id": message["id"],
                        "chunk_id": str(citation.chunk_id),
                        "user_id": str(user_id),
                        "citation_order": index,
                        "quote": citation.quote,
                    }
                    for index, citation in enumerate(citations)
                ]
            ).execute()
