import asyncio
from unittest.mock import MagicMock

from src.conf import messages as msg
from src.database.models import User
from src.services.auth import auth_service


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["detail"] == msg.USER_SUCCESSFULLY_CREATED


def test_repeat_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 409, response.text
    payload = response.json()
    assert payload["detail"] == msg.ACCOUNT_ALREADY_EXISTS


def test_login_user_not_confirmed_email(client, user):
    response = client.post("/api/auth/login", data={"username": user.get("email"), "password": user.get("password")})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == msg.EMAIL_NOT_CONFIRMED


def test_login_user(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/api/auth/login", data={"username": user.get("email"), "password": user.get("password")})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["refresh_token"] is not None


def test_login_user_with_wrong_password(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    assert current_user.confirmed is True
    response = client.post("/api/auth/login", data={"username": user.get("email"), "password": "wrong_password"})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == msg.INVALID_PASSWORD


def test_login_user_with_wrong_email(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    assert current_user.confirmed is True
    response = client.post("/api/auth/login", data={"username": "wrong_email", "password": user.get("password")})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == msg.INVALID_EMAIL


def test_refresh_token_true(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    old_refresh_token = current_user.refresh_token
    headers = {"Authorization": f"Bearer {old_refresh_token}"}
    response = client.get("/api/auth/refresh_token", headers=headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["token_type"] == "bearer"


def test_refresh_token_invalid_email(client):
    invalid_token = asyncio.run(auth_service.create_refresh_token(data={"sub": "invalid@email.com"}))
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = client.get('/api/auth/refresh_token', headers=headers)
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == msg.INVALID_USER


def test_refresh_token_invalid_token(client, user):
    invalid_token = asyncio.run(auth_service.create_refresh_token(data={"sub": user.get("email")}, expires_delta=1))
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = client.get('/api/auth/refresh_token', headers=headers)
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == msg.INVALID_REFRESH_TOKEN


def test_forgot_password(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/forgot_password", json={"email": user.get("email")})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["detail"] == msg.PASSWORD_RESET_SEND


def test_forgot_password_invalid_email(client, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/forgot_password", json={"email": "invalid@email.com"})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == msg.INVALID_EMAIL


def test_change_password_get(client, user):
    password_token = auth_service.create_password_token(data={"sub": user.get("email")})
    response = client.get(f"/api/auth/change_password/{password_token}")
    assert response.status_code == 200, response.text
    response.template.name = "password_change.html"


def test_change_password_get_invalid_email(client, user):
    password_token = auth_service.create_password_token(data={"sub": "invalid@email.com"})
    response = client.get(f"/api/auth/change_password/{password_token}")
    assert response.status_code == 400, response.text
    payload = response.json()
    assert payload["detail"] == msg.VERIFICATION_ERROR


def test_change_password_put(client, user, session):
    password_token = auth_service.create_password_token(data={"sub": user.get("email")})
    response = client.put(f"/api/auth/change_password/{password_token}", json={"password": "7654321"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["detail"] == msg.PASSWORD_CHANGED
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    assert auth_service.verify_password("7654321", current_user.password) is True


def test_change_password_put_verification_error(client, user):
    password_token = auth_service.create_password_token(data={"sub": "invalid@email.com"})
    response = client.put(f"/api/auth/change_password/{password_token}", json={"password": "7654321"})
    assert response.status_code == 400, response.text
    payload = response.json()
    assert payload["detail"] == msg.VERIFICATION_ERROR


def test_confirmed_email(client, user):
    email_token = auth_service.create_email_token(data={"sub": user.get("email")})
    response = client.get(f"/api/auth/confirmed_email/{email_token}")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["detail"] == msg.EMAIL_CONFIRMED


def test_confirmed_email_verification_error(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = False
    session.commit()

    email_token = auth_service.create_email_token(data={"sub": "invalid@email.com"})
    response = client.get(f"/api/auth/confirmed_email/{email_token}")
    assert response.status_code == 400, response.text
    payload = response.json()
    assert payload["detail"] == msg.VERIFICATION_ERROR


def test_confirmed_email_verification_error_1(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()

    email_token = auth_service.create_email_token(data={"sub": "invalid@email.com"})
    response = client.get(f"/api/auth/confirmed_email/{email_token}")
    assert response.status_code == 400, response.text
    payload = response.json()
    assert payload["detail"] == msg.VERIFICATION_ERROR
