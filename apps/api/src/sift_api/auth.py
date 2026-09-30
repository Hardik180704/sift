"""Supabase JWT verification for FastAPI endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientError
from pydantic import BaseModel

from sift_api.config import Settings, get_settings

bearer_scheme = HTTPBearer(auto_error=False)
supported_algorithms = ("ES256", "RS256")


class AuthenticatedUser(BaseModel):
    """Identity derived exclusively from a verified Supabase JWT subject."""

    user_id: UUID


def unauthorized(detail: str = "Invalid or missing access token") -> HTTPException:
    """Return a standards-compliant bearer-token authentication failure."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_access_token(token: str, settings: Settings) -> AuthenticatedUser:
    """Verify a Supabase access token and construct its trusted subject identity."""
    if settings.supabase_url is None or settings.supabase_jwt_audience is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured",
        )

    try:
        signing_key = PyJWKClient(settings.supabase_jwks_url).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=list(supported_algorithms),
            audience=settings.supabase_jwt_audience,
            issuer=settings.supabase_jwt_issuer,
        )
        return AuthenticatedUser(user_id=claims["sub"])
    except (InvalidTokenError, KeyError, PyJWKClientError, ValueError):
        raise unauthorized() from None


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthenticatedUser:
    """Require a verified bearer token and never accept a client user identifier."""
    if credentials is None:
        raise unauthorized("Missing bearer token")
    return decode_access_token(credentials.credentials, settings)
