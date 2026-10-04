from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest

from sift_api.config import Settings
from sift_api.ingestion.uploads import UploadService

USER_ID = UUID("11111111-1111-1111-1111-111111111111")
DOCUMENT_ID = UUID("22222222-2222-2222-2222-222222222222")


def build_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Settings:
    monkeypatch.chdir(tmp_path)
    return Settings.model_validate(
        {
            "supabase_url": "https://dev.supabase.co",
            "supabase_jwt_audience": "authenticated",
            "supabase_service_role_key": "service-key",
            "inngest_event_key": "event-key",
            "inngest_signing_key": "signing-key",
            "inngest_api_base_url": "http://127.0.0.1:8288",
        }
    )


def test_confirm_queues_document_creates_job_and_emits_event(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    settings = build_settings(monkeypatch, tmp_path)
    client = MagicMock()
    documents = MagicMock()
    jobs = MagicMock()
    client.table.side_effect = [documents, jobs]
    documents.update.return_value = documents
    documents.eq.return_value = documents
    documents.execute.return_value.data = [{"id": str(DOCUMENT_ID)}]
    jobs.insert.return_value = jobs
    jobs.execute.return_value.data = [{"id": "job-id"}]
    response = MagicMock()

    with (
        patch("sift_api.ingestion.uploads.create_client", return_value=client),
        patch("sift_api.ingestion.uploads.httpx.post", return_value=response) as post,
    ):
        UploadService(settings).confirm(USER_ID, DOCUMENT_ID)

    jobs.insert.assert_called_once_with(
        {"document_id": str(DOCUMENT_ID), "user_id": str(USER_ID), "state": "QUEUED"}
    )
    post.assert_called_once_with(
        settings.inngest_event_endpoint,
        json={
            "name": "document.ingest",
            "data": {"document_id": str(DOCUMENT_ID), "user_id": str(USER_ID)},
        },
        timeout=10.0,
    )
    response.raise_for_status.assert_called_once_with()


def test_confirm_re_emits_a_queued_document_without_creating_another_job(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    settings = build_settings(monkeypatch, tmp_path)
    client = MagicMock()
    documents = MagicMock()
    client.table.return_value = documents
    documents.update.return_value = documents
    documents.eq.return_value = documents
    documents.execute.side_effect = [
        MagicMock(data=[]),
        MagicMock(data=[{"id": str(DOCUMENT_ID)}]),
    ]
    response = MagicMock()

    with (
        patch("sift_api.ingestion.uploads.create_client", return_value=client),
        patch("sift_api.ingestion.uploads.httpx.post", return_value=response) as post,
    ):
        UploadService(settings).confirm(USER_ID, DOCUMENT_ID)

    assert client.table.call_args_list == [
        (("documents",),),
        (("documents",),),
    ]
    post.assert_called_once()
    response.raise_for_status.assert_called_once_with()
