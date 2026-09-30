from uuid import UUID

from sift_api.assistant.graph import build_graph
from sift_api.retrieval.schemas import SourceEvidence


def test_document_question_without_evidence_is_explicitly_insufficient() -> None:
    state = build_graph().invoke({"question": "When does my lease renew?", "sources": []})

    assert state["insufficient_evidence"] is True
    assert (
        state["answer"]
        == "I do not have enough evidence in your uploaded documents to answer that."
    )


def test_document_question_carries_retrieved_evidence_into_cited_answer() -> None:
    source = SourceEvidence(
        chunk_id=UUID("10000000-0000-0000-0000-000000000001"),
        document_id=UUID("20000000-0000-0000-0000-000000000001"),
        page_number=3,
        section="Renewal",
        content="The lease renews on 2027-01-15.",
        score=0.1,
    )

    state = build_graph().invoke({"question": "When does my lease renew?", "sources": [source]})

    assert state["insufficient_evidence"] is False
    assert state["answer"] == "The lease renews on 2027-01-15."


def test_non_document_chat_does_not_make_document_claims() -> None:
    state = build_graph().invoke({"question": "Hello", "sources": []})

    assert state["insufficient_evidence"] is False
    assert state["answer"] == "I can help you understand documents you have uploaded to Sift."
