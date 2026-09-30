from unittest.mock import MagicMock

from qdrant_client import models

from sift_api.ingestion.indexing import ChunkIndexer


def test_collection_initialization_creates_scoped_payload_indexes() -> None:
    indexer = ChunkIndexer.__new__(ChunkIndexer)
    indexer._collection = "test_chunks"
    indexer._dimensions = 1536
    indexer._qdrant = MagicMock()
    indexer._qdrant.collection_exists.return_value = False

    indexer.ensure_collection()

    indexer._qdrant.create_collection.assert_called_once_with(
        collection_name="test_chunks",
        vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
    )
    assert indexer._qdrant.create_payload_index.call_count == 3


def test_collection_initialization_is_idempotent() -> None:
    indexer = ChunkIndexer.__new__(ChunkIndexer)
    indexer._collection = "test_chunks"
    indexer._dimensions = 1536
    indexer._qdrant = MagicMock()
    indexer._qdrant.collection_exists.return_value = True

    indexer.ensure_collection()

    indexer._qdrant.create_collection.assert_not_called()
    indexer._qdrant.create_payload_index.assert_not_called()
