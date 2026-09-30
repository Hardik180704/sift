from uuid import UUID

from fastapi.testclient import TestClient

from sift_api.auth import AuthenticatedUser, get_current_user
from sift_api.main import app


def test_protected_endpoint_rejects_missing_bearer_token() -> None:
    response = TestClient(app).get("/v1/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_protected_endpoint_uses_verified_subject_only() -> None:
    trusted_user_id = UUID("9c1b7dc8-e8b5-4595-a493-b337bcd1c5eb")
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(user_id=trusted_user_id)

    try:
        response = TestClient(app).get("/v1/auth/me?user_id=00000000-0000-0000-0000-000000000000")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"user_id": str(trusted_user_id)}
