"""Application configuration loaded from the environment."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime configuration for the API boundary."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="SIFT_", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    cors_origins: str = "http://localhost:3000"
    supabase_url: AnyHttpUrl | None = None
    supabase_jwt_audience: str | None = None
    supabase_service_role_key: SecretStr | None = None
    qdrant_url: AnyHttpUrl | None = None
    qdrant_api_key: SecretStr | None = None
    qdrant_collection: str = "sift_chunks"
    openai_api_key: SecretStr | None = None
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    chat_model: str = "gpt-4.1-mini"
    inngest_event_key: SecretStr | None = None
    inngest_signing_key: SecretStr | None = None
    inngest_api_base_url: str = "https://inn.gs"

    @model_validator(mode="after")
    def validate_service_groups(self) -> Settings:
        """Reject partially configured services before requests can reach them."""
        if (self.supabase_url is None) != (self.supabase_jwt_audience is None):
            raise ValueError(
                "SIFT_SUPABASE_URL and SIFT_SUPABASE_JWT_AUDIENCE must be configured together"
            )

        if (self.inngest_event_key is None) != (self.inngest_signing_key is None):
            raise ValueError(
                "SIFT_INNGEST_EVENT_KEY and SIFT_INNGEST_SIGNING_KEY must be configured together"
            )

        if self.environment == "production" and self.supabase_url is None:
            raise ValueError("Supabase configuration is required in production")

        return self

    @property
    def supabase_jwt_issuer(self) -> str:
        """Return the expected issuer for Supabase access tokens."""
        if self.supabase_url is None:
            raise RuntimeError("Supabase configuration is unavailable")
        return f"{str(self.supabase_url).rstrip('/')}/auth/v1"

    @property
    def supabase_jwks_url(self) -> str:
        """Return the Supabase JWKS endpoint for signature verification."""
        return f"{self.supabase_jwt_issuer}/.well-known/jwks.json"

    def require_supabase_service_role_key(self) -> str:
        """Return the server-only key for narrow, scoped workflow operations."""
        if self.supabase_url is None or self.supabase_service_role_key is None:
            raise RuntimeError("Supabase service-role configuration is unavailable")
        return self.supabase_service_role_key.get_secret_value()

    @property
    def inngest_event_endpoint(self) -> str:
        """Return the events endpoint for the active Inngest environment."""
        if self.inngest_event_key is None:
            raise RuntimeError("Inngest event configuration is unavailable")
        return (
            f"{self.inngest_api_base_url.rstrip('/')}/e/{self.inngest_event_key.get_secret_value()}"
        )


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide validated settings instance."""
    return Settings()
