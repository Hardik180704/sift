"""Constrained OpenAI generation for grounded document answers."""

from __future__ import annotations

from collections.abc import Callable

from openai import OpenAI

from sift_api.config import Settings
from sift_api.retrieval.schemas import SourceEvidence

AnswerGenerator = Callable[[str, list[SourceEvidence]], str]

SYSTEM_PROMPT = """You are Sift, a precise document assistant.
Answer only from the supplied document excerpts. Do not add facts, assumptions,
or legal advice. For a simple factual question, respond in one or two concise
sentences and no more than 60 words. Expand only when the user explicitly asks
for detail, a summary, or a list. If the excerpts cannot support the answer,
say so plainly. Do not include citation syntax; the application adds citations."""


def build_openai_answer_generator(settings: Settings) -> AnswerGenerator:
    """Return a bounded answer generator using the configured chat model."""
    if settings.openai_api_key is None:
        raise RuntimeError("OpenAI configuration is required for grounded answers")
    client = OpenAI(api_key=settings.openai_api_key.get_secret_value())

    def generate(question: str, sources: list[SourceEvidence]) -> str:
        excerpts = "\n\n".join(
            (f"Source {index} (page {source.page_number or 'unknown'}):\n{source.content}")
            for index, source in enumerate(sources[:5], start=1)
        )
        completion = client.chat.completions.create(
            model=settings.chat_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nDocument excerpts:\n{excerpts}",
                },
            ],
            max_completion_tokens=180,
            temperature=0.2,
        )
        answer = completion.choices[0].message.content
        if not answer or not answer.strip():
            raise RuntimeError("The chat model returned an empty answer")
        return answer.strip()

    return generate
