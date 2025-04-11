from unittest.mock import Mock

import pytest
from sqlalchemy import select
from starlette.status import HTTP_400_BAD_REQUEST

from src.database.models import User
from src.services.auth import create_email_token
from tests.conftest import TestingSessionLocal

user_data = {"username": "agent007", "email": "agent007@gmail.com", "password": "12345678"}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "A user with this email already exists"


def test_not_confirmed_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email address not verified"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect username or password"


def test_wrong_username_login(client):
    response = client.post("api/auth/login",
                           data={"username": "username", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect username or password"


def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_confirm_email(client, monkeypatch):
    token = create_email_token({"sub": user_data["email"]})

    async def fake_confirmed_email(email):
        pass

    monkeypatch.setattr("src.services.users.UserService.confirmed_email", fake_confirmed_email)

    response = client.get(f"/api/auth/confirmed_email/{token}")
    assert response.status_code == 200
    assert response.json()["message"] in ["Email Verified", "Your email is already confirmed"]


def test_confirm_email_invalid_token(client):
    response = client.get("/api/auth/confirmed_email/invalidtoken")
    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid token for email verification"


# === Request Email ===

def test_request_email_unconfirmed(client, monkeypatch):
    monkeypatch.setattr("src.api.auth.send_email", Mock())
    response = client.post("/api/auth/request_email", json={"email": user_data.get("email")})
    assert response.status_code == 200
    assert "message" in response.json()


def test_request_email_user_not_exist(client):
    response = client.post("/api/auth/request_email", json={"email": "nonexist@example.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User with this email does not exist"


def test_reset_password_form(client):
    token = create_email_token({"sub": user_data["email"]})
    response = client.get(f"/api/auth/reset-password?token={token}")
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type")


@pytest.mark.asyncio
async def test_reset_password_expired_token(client):
    response = client.post("/api/auth/reset-password", data={"token": "expiredtoken", "new_password": "pass"})
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid or expired token"
