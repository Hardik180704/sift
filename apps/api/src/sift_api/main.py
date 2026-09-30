"""FastAPI application entrypoint."""

import json
import os
from typing import Annotated
from uuid import UUID

import inngest.fast_api
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from sift_api.assistant.schemas import AssistantRequest, AssistantResponse
from sift_api.assistant.service import AssistantService
from sift_api.auth import AuthenticatedUser, get_current_user
from sift_api.config import get_settings
from sift_api.ingestion.schemas import UploadConfirmationResponse, UploadRequest, UploadResponse
from sift_api.ingestion.uploads import UploadService
from sift_api.ingestion.workflows import ingest_document, inngest_client
from sift_api.retrieval.schemas import RetrievalRequest, RetrievalResponse
from sift_api.retrieval.service import RetrievalService


class HealthResponse(BaseModel):
    """Public API liveness response."""

    status: str
    service: str


class CurrentUserResponse(BaseModel):
    """Public representation of the caller's verified identity."""

    user_id: str


def create_app() -> FastAPI:
    """Create the API application without connecting to external services."""
    settings = get_settings()
    app = FastAPI(title="Sift API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.rstrip("/") for origin in settings.cors_origins.split(",")],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    if settings.inngest_signing_key is not None:
        os.environ["INNGEST_SIGNING_KEY"] = settings.inngest_signing_key.get_secret_value()
        inngest.fast_api.serve(app, inngest_client, [ingest_document])

    @app.get("/health", response_model=HealthResponse, tags=["operations"])  # type: ignore[untyped-decorator]
    def health() -> HealthResponse:
        """Return liveness for platform and deployment checks."""
        return HealthResponse(status="ok", service="api")

    @app.get("/v1/auth/me", response_model=CurrentUserResponse, tags=["authentication"])  # type: ignore[untyped-decorator]
    def current_user(
        user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> CurrentUserResponse:
        """Expose the verified caller identity for authentication integration checks."""
        return CurrentUserResponse(user_id=str(user.user_id))

    @app.post("/v1/documents/uploads", response_model=UploadResponse, tags=["documents"])  # type: ignore[untyped-decorator]
    def initiate_upload(
        request: UploadRequest,
        user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> UploadResponse:
        """Create a private, user-scoped signed upload target."""
        return UploadService(settings).initiate(user.user_id, request)

    @app.post(
        "/v1/documents/{document_id}/upload-complete",
        response_model=UploadConfirmationResponse,
        tags=["documents"],
    )  # type: ignore[untyped-decorator]
    def confirm_upload(
        document_id: UUID, user: Annotated[AuthenticatedUser, Depends(get_current_user)]
    ) -> UploadConfirmationResponse:
        try:
            UploadService(settings).confirm(user.user_id, document_id)
        except LookupError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
        return UploadConfirmationResponse(document_id=document_id, state="QUEUED")

    @app.post("/v1/retrieval", response_model=RetrievalResponse, tags=["retrieval"])  # type: ignore[untyped-decorator]
    def retrieve_sources(
        request: RetrievalRequest,
        user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> RetrievalResponse:
        """Return only page-level source evidence owned by the verified caller."""
        return RetrievalResponse(
            sources=RetrievalService(settings).retrieve(user.user_id, request.query, request.limit)
        )

    @app.post("/v1/assistant", response_model=AssistantResponse, tags=["assistant"])  # type: ignore[untyped-decorator]
    def assistant_answer(
        request: AssistantRequest,
        user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> AssistantResponse:
        """Return a persisted, citation-gated grounded assistant response."""
        try:
            return AssistantService(settings).answer(
                user.user_id, request.question, request.conversation_id
            )
        except LookupError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    @app.post("/v1/assistant/stream", tags=["assistant"])  # type: ignore[untyped-decorator]
    def stream_assistant_answer(
        request: AssistantRequest,
        user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> StreamingResponse:
        """Stream a typed result event while keeping persistence inside the assistant service."""
        try:
            result = AssistantService(settings).answer(
                user.user_id, request.question, request.conversation_id
            )
        except LookupError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

        def events() -> object:
            yield f"event: answer\ndata: {json.dumps(result.model_dump(mode='json'))}\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    return app


app = create_app()
