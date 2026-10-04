from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest

from sift_api.config import Settings
from sift_api.ingestion.documents import DocumentListResponse, DocumentService

USER_ID = UUID("11111111-1111-1111-1111-111111111111")


def build_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Settings:
    monkeypatch.chdir(tmp_path)
    return Settings.model_validate(
        {
            "supabase_url": "https://dev.supabase.co",
            "supabase_jwt_audience": "authenticated",
            "supabase_service_role_key": "service-key",
        }
    )


def test_list_documents_scopes_rows_to_verified_user(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    settings = build_settings(monkeypatch, tmp_path)
    client = MagicMock()
    table = MagicMock()
    client.table.return_value = table
    table.select.return_value = table
    table.eq.return_value = table
    table.order.return_value = table
    table.execute.return_value.data = [
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "original_filename": "lease.pdf",
            "mime_type": "application/pdf",
            "size_bytes": 2048,
            "state": "READY",
            "created_at": "2026-10-04T00:00:00+00:00",
            "updated_at": "2026-10-04T00:00:00+00:00",
        }
    ]

    with patch("sift_api.ingestion.documents.create_client", return_value=client):
        response = DocumentService(settings).list_documents(USER_ID)

    table.eq.assert_called_once_with("user_id", str(USER_ID))
    assert isinstance(response, DocumentListResponse)
    assert response.documents[0].original_filename == "lease.pdf"
    assert response.documents[0].state == "READY"


def test_list_documents_returns_empty_library_without_rows(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    settings = build_settings(monkeypatch, tmp_path)
    client = MagicMock()
    table = MagicMock()
    client.table.return_value = table
    table.select.return_value = table
    table.eq.return_value = table
    table.order.return_value = table
    table.execute.return_value.data = []

    with patch("sift_api.ingestion.documents.create_client", return_value=client):
        response = DocumentService(settings).list_documents(USER_ID)

    assert response.documents == []
