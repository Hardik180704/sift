"""Hybrid Qdrant and Supabase FTS retrieval with mandatory ownership filters."""

from __future__ import annotations

from typing import Any, cast
from uuid import UUID

from openai import OpenAI
from qdrant_client import QdrantClient, models
from supabase import create_client

from sift_api.config import Settings
from sift_api.retrieval.fusion import reciprocal_rank_fusion
from sift_api.retrieval.schemas import SourceEvidence


class RetrievalService:
    """Retrieves evidence only from documents belonging to the verified caller."""

    def __init__(self, settings: Settings) -> None:
        if settings.supabase_url is None or settings.qdrant_url is None:
            raise RuntimeError("Supabase and Qdrant configuration are required for retrieval")
        if settings.qdrant_api_key is None or settings.openai_api_key is None:
            raise RuntimeError("Qdrant and OpenAI credentials are required for retrieval")
        self._supabase = create_client(
            str(settings.supabase_url), settings.require_supabase_service_role_key()
        )
        self._qdrant = QdrantClient(
            url=str(settings.qdrant_url), api_key=settings.qdrant_api_key.get_secret_value()
        )
        self._embeddings = OpenAI(api_key=settings.openai_api_key.get_secret_value())
        self._settings = settings

    def retrieve(self, user_id: UUID, query: str, limit: int) -> list[SourceEvidence]:
        """Fuse user-filtered semantic and keyword candidates into page-level evidence."""
        semantic_ids = self._semantic_candidates(user_id, query, limit)
        keyword_ids = self._keyword_candidates(user_id, query, limit)
        fused = reciprocal_rank_fusion((semantic_ids, keyword_ids), limit)
        if not fused:
            return []
        chunk_ids = [str(chunk_id) for chunk_id, _ in fused]
        rows = cast(
            list[dict[str, Any]],
            self._supabase.table("chunks")
            .select("id, document_id, page_number, section, content")
            .eq("user_id", str(user_id))
            .in_("id", chunk_ids)
            .execute()
            .data,
        )
        rows_by_id = {UUID(row["id"]): row for row in rows}
        return [
            SourceEvidence(
                chunk_id=chunk_id,
                document_id=UUID(rows_by_id[chunk_id]["document_id"]),
                page_number=rows_by_id[chunk_id]["page_number"],
                section=rows_by_id[chunk_id]["section"],
                content=rows_by_id[chunk_id]["content"],
                score=score,
            )
            for chunk_id, score in fused
            if chunk_id in rows_by_id
        ]

    def _semantic_candidates(self, user_id: UUID, query: str, limit: int) -> list[UUID]:
        vector = (
            self._embeddings.embeddings.create(
                model=self._settings.embedding_model,
                dimensions=self._settings.embedding_dimensions,
                input=query,
            )
            .data[0]
            .embedding
        )
        results = self._qdrant.query_points(
            collection_name=self._settings.qdrant_collection,
            query=vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id", match=models.MatchValue(value=str(user_id))
                    )
                ]
            ),
            limit=limit,
        ).points
        return [
            UUID(str(point.payload["chunk_id"])) for point in results if point.payload is not None
        ]

    def _keyword_candidates(self, user_id: UUID, query: str, limit: int) -> list[UUID]:
        rows = cast(
            list[dict[str, Any]],
            self._supabase.table("chunks")
            .select("id")
            .eq("user_id", str(user_id))
            .text_search("search_vector", query, options={"type": "websearch"})
            .execute()
            .data,
        )
        return [UUID(row["id"]) for row in rows[:limit]]
