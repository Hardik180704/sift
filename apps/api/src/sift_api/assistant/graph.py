"""Explicit bounded graph for citation-gated document answers."""

from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from sift_api.assistant.generation import AnswerGenerator
from sift_api.retrieval.schemas import SourceEvidence


class AssistantState(TypedDict, total=False):
    question: str
    intent: str
    sources: list[SourceEvidence]
    answer: str
    retries: int
    insufficient_evidence: bool


def route_intent(state: AssistantState) -> AssistantState:
    """Keep off-topic conversation separate from document-derived factual claims."""
    question = state["question"].lower()
    if any(token in question for token in ("hello", "thanks", "who are you")):
        return {"intent": "non_document"}
    return {"intent": "document"}


def generate_grounded_answer(
    state: AssistantState, answer_generator: AnswerGenerator | None = None
) -> AssistantState:
    """Generate only from retrieved evidence; lack of evidence remains explicit."""
    if state["intent"] == "non_document":
        return {
            "answer": "I can help you understand documents you have uploaded to Sift.",
            "insufficient_evidence": False,
        }
    sources = state.get("sources", [])
    if not sources:
        return {
            "answer": "I do not have enough evidence in your uploaded documents to answer that.",
            "insufficient_evidence": True,
        }
    if answer_generator is None:
        return {"answer": sources[0].content, "insufficient_evidence": False}
    return {
        "answer": answer_generator(state["question"], sources),
        "insufficient_evidence": False,
    }


def reflect_citations(state: AssistantState) -> AssistantState:
    """Reject document answers that somehow lost their evidence."""
    if (
        state["intent"] == "document"
        and not state.get("insufficient_evidence")
        and not state.get("sources")
    ):
        return {"retries": state.get("retries", 0) + 1}
    return {}


def next_after_reflection(state: AssistantState) -> str:
    """Allow at most one retrieval retry before returning insufficient evidence."""
    if state.get("retries", 0) == 1:
        return "retrieve"
    return END


def build_graph(answer_generator: AnswerGenerator | None = None) -> Any:
    """Build the bounded routing, generation, reflection graph."""
    graph = StateGraph(AssistantState)
    graph.add_node("route", route_intent)
    graph.add_node("generate", lambda state: generate_grounded_answer(state, answer_generator))
    graph.add_node("reflect", reflect_citations)
    graph.add_edge(START, "route")
    graph.add_edge("route", "generate")
    graph.add_edge("generate", "reflect")
    graph.add_conditional_edges(
        "reflect", next_after_reflection, {"retrieve": "generate", END: END}
    )
    return graph.compile()
