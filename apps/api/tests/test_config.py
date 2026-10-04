from pathlib import Path

import pytest
from pydantic import ValidationError

from sift_api.config import Settings
from sift_api.ingestion.workflows import _load_workflow_registration


def test_rejects_partial_supabase_configuration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValidationError, match="SIFT_SUPABASE_URL"):
        Settings.model_validate({"supabase_url": "https://example.supabase.co"})


def test_rejects_partial_inngest_configuration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValidationError, match="SIFT_INNGEST_EVENT_KEY"):
        Settings.model_validate({"inngest_event_key": "event-key"})


def test_requires_supabase_in_production(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValidationError, match="required in production"):
        Settings(environment="production")


def test_does_not_register_ingest_workflow_without_signing_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    settings = Settings()

    client, function = _load_workflow_registration(settings)

    assert client is None
    assert function is None
