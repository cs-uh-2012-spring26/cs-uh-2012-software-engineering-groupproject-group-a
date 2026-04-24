import pytest
import requests
from unittest.mock import patch, MagicMock
from app.services.telegram_service import TelegramService

@patch("requests.get")
def test_get_user_chat_id_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ok": True,
        "result": [
            {
                "message": {
                    "text": "/start secret_token",
                    "chat": {"id": 12345}
                }
            }
        ]
    }
    mock_get.return_value = mock_response

    result = TelegramService.get_user_chat_id("secret_token")
    assert result == "12345"

@patch("requests.get")
def test_get_user_chat_id_not_ok(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"ok": False}
    mock_get.return_value = mock_response

    result = TelegramService.get_user_chat_id("any_token")
    assert result is None

@patch("requests.get")
def test_get_user_chat_id_no_match(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ok": True,
        "result": [
            {"message": {"text": "/start wrong_token", "chat": {"id": 111}}},
            {"message": {"text": "hello", "chat": {"id": 222}}},
            {"message": {}}
        ]
    }
    mock_get.return_value = mock_response

    result = TelegramService.get_user_chat_id("secret_token")
    assert result is None

@patch("requests.post")
def test_send_telegram_message_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}
    mock_post.return_value = mock_response

    success, error = TelegramService.send_telegram_message("123", "Hello")
    assert success is True
    assert error is None

@patch("requests.post")
def test_send_telegram_message_api_error(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": False, "description": "Unknown error"}
    mock_post.return_value = mock_response

    success, error = TelegramService.send_telegram_message("123", "Hello")
    assert success is False
    assert "Telegram API error: Unknown error" in error

@patch("requests.post")
def test_send_telegram_message_exception(mock_post):
    mock_post.side_effect = Exception("Connection Timed Out")

    success, error = TelegramService.send_telegram_message("123", "Hello")
    assert success is False
    assert "Connection Timed Out" in error