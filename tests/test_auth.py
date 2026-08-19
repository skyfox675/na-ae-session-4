import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
import app


def setup_function():
    app.sessions.clear()
    app.practice_leads = {
        "lead": {"password_hash": app.hash_password("secret"), "role": "practice_lead"},
        "consultant": {
            "password_hash": app.hash_password("secret"),
            "role": "consultant",
            "email": "consultant@slalom.com",
        },
    }


def test_registration_requires_authentication():
    client = TestClient(app.app)
    response = client.post("/capabilities/Cloud Architecture/register", params={"email": "new@slalom.com"})
    assert response.status_code == 401


def test_practice_lead_can_unregister_after_login():
    client = TestClient(app.app)
    login = client.post("/auth/login", json={"username": "lead", "password": "secret"})
    assert login.status_code == 200
    response = client.delete(
        "/capabilities/Cloud Architecture/unregister",
        params={"email": "alice.smith@slalom.com"},
    )
    assert response.status_code == 200


def test_consultant_cannot_unregister():
    client = TestClient(app.app)
    login = client.post("/auth/login", json={"username": "consultant", "password": "secret"})
    assert login.status_code == 200
    response = client.delete(
        "/capabilities/Cloud Architecture/unregister",
        params={"email": "bob.johnson@slalom.com"},
    )
    assert response.status_code == 403


def test_consultant_can_only_register_themselves():
    client = TestClient(app.app)
    login = client.post("/auth/login", json={"username": "consultant", "password": "secret"})
    assert login.status_code == 200
    response = client.post(
        "/capabilities/Cloud Architecture/register",
        params={"email": "someone-else@slalom.com"},
    )
    assert response.status_code == 403