from uuid import UUID

from sift_api.retrieval.fusion import reciprocal_rank_fusion


def test_fusion_rewards_candidates_appearing_in_both_rankings() -> None:
    first = UUID("10000000-0000-0000-0000-000000000001")
    shared = UUID("10000000-0000-0000-0000-000000000002")
    third = UUID("10000000-0000-0000-0000-000000000003")

    results = reciprocal_rank_fusion(((first, shared), (shared, third)), limit=3)

    assert results[0][0] == shared
    assert [chunk_id for chunk_id, _ in results] == [shared, first, third]


def test_fusion_is_deterministic_for_equal_scores() -> None:
    first = UUID("10000000-0000-0000-0000-000000000001")
    second = UUID("10000000-0000-0000-0000-000000000002")

    assert reciprocal_rank_fusion(((second,), (first,)), limit=2) == [
        (first, 1 / 61),
        (second, 1 / 61),
    ]
