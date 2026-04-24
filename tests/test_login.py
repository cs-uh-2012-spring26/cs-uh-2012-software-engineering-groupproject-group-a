from http import HTTPStatus
from unittest.mock import patch

import pytest
from app.apis import MSG

MOCK_GET_CHAT = "app.apis.auth.TelegramService.get_user_chat_id"

@patch(MOCK_GET_CHAT)
def test_login_success(mock_get_chat, client, seeded_member):
    mock_get_chat.return_value = None
    
    response = client.post(
        "/auth/login",
        json={
            "username": seeded_member["username"], 
            "password": "password123"
        }
    )

    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert data[MSG] == "Logged in successfully"
    assert "access_token" in data
    assert data["telegram_synced"] is False

@pytest.mark.parametrize(
    "username,password",
    [
        ("unknown_user", "password123"),
        ("test_member", "wrong_password"),
    ],
)
def test_login_bad_credentials(client, seeded_member, username, password):
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "Bad credentials"


@pytest.mark.parametrize(
    "username,password",
    [
        ("", "password123"),
        ("test_member", ""),
    ],
)
def test_login_invalid_values(client, seeded_member, username, password):
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )

    assert response.status_code == 406
    assert response.get_json()["message"] == "Invalid value provided for one of the fields"
