from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest

from sift_api.assistant.generation import SYSTEM_PROMPT, build_openai_answer_generator
from sift_api.config import Settings
from sift_api.retrieval.schemas import SourceEvidence


def test_openai_generator_uses_short_grounded_answer_contract(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    settings = Settings.model_validate({"openai_api_key": "openai-key", "chat_model": "test-model"})
    client = MagicMock()
    client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="Your lease renews on January 15, 2027."))
    ]
    source = SourceEvidence(
        chunk_id=UUID("10000000-0000-0000-0000-000000000001"),
        document_id=UUID("20000000-0000-0000-0000-000000000001"),
        page_number=3,
        section="Renewal",
        content="The lease renews on 2027-01-15.",
        score=0.1,
    )

    with patch("sift_api.assistant.generation.OpenAI", return_value=client):
        answer = build_openai_answer_generator(settings)("When does my lease renew?", [source])

    assert answer == "Your lease renews on January 15, 2027."
    client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Question: When does my lease renew?\n\nDocument excerpts:\n"
                    "Source 1 (page 3):\nThe lease renews on 2027-01-15."
                ),
            },
        ],
        max_completion_tokens=180,
        temperature=0.2,
    )
