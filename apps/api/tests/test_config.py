from pathlib import Path

import pytest
from pydantic import ValidationError

from sift_api.config import Settings


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
