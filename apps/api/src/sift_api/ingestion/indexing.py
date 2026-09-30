"""Embedding and Qdrant indexing adapters for private document chunks."""

from __future__ import annotations

from uuid import UUID

from openai import OpenAI
from qdrant_client import QdrantClient, models

from sift_api.config import Settings
from sift_api.ingestion.chunking import Chunk


class ChunkIndexer:
    """Indexes deterministic chunks without sending text to Qdrant payloads."""

    def __init__(self, settings: Settings) -> None:
        if (
            settings.qdrant_url is None
            or settings.qdrant_api_key is None
            or settings.openai_api_key is None
        ):
            raise RuntimeError("Qdrant and OpenAI configuration are required for indexing")
        self._collection = settings.qdrant_collection
        self._dimensions = settings.embedding_dimensions
        self._embeddings = OpenAI(api_key=settings.openai_api_key.get_secret_value())
        self._qdrant = QdrantClient(
            url=str(settings.qdrant_url), api_key=settings.qdrant_api_key.get_secret_value()
        )
        self._model = settings.embedding_model

    def index(
        self, user_id: UUID, document_id: UUID, version_id: UUID, chunks: list[Chunk]
    ) -> None:
        """Delete the exact prior version then synchronously upsert deterministic points."""
        self._qdrant.delete(
            collection_name=self._collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id", match=models.MatchValue(value=str(user_id))
                        ),
                        models.FieldCondition(
                            key="document_version_id",
                            match=models.MatchValue(value=str(version_id)),
                        ),
                    ]
                )
            ),
            wait=True,
        )
        if not chunks:
            return
        vectors = self._embeddings.embeddings.create(
            model=self._model, dimensions=self._dimensions, input=[chunk.text for chunk in chunks]
        ).data
        self._qdrant.upsert(
            collection_name=self._collection,
            points=[
                models.PointStruct(
                    id=str(chunk.id),
                    vector=vector.embedding,
                    payload={
                        "user_id": str(user_id),
                        "document_id": str(document_id),
                        "document_version_id": str(version_id),
                        "chunk_id": str(chunk.id),
                        "page": chunk.page_number,
                    },
                )
                for chunk, vector in zip(chunks, vectors, strict=True)
            ],
            wait=True,
        )
