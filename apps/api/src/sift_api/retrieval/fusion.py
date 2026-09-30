"""Deterministic reciprocal-rank fusion for retrieval candidates."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

RRF_K = 60


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[UUID]], limit: int
) -> list[tuple[UUID, float]]:
    """Combine independent ranked candidate lists without comparing raw scores."""
    scores: dict[UUID, float] = {}
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], str(item[0])))[:limit]
