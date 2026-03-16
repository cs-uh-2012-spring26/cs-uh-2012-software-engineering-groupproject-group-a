import pytest
from unittest.mock import patch, MagicMock
from app.services.email_service import EmailService

#monkeypatch is used here for temporarily swapping out out env variables

# by client her we mean SendGridAPIClient object
def test_get_sendgrid_client_success(monkeypatch): # testing successful client creation
    monkeypatch.setenv("SENDGRID_API_KEY", "fake_api_key")
    client = EmailService._get_sendgrid_client()
    assert client is not None # has been created successfully
    
def test_get_sendgrid_client_missing_key(monkeypatch):
    monkeypatch.delenv("SENDGRID_API_KEY", raising=False) # hypothetically deletes the key from env
    with pytest.raises(ValueError, match="Missing SendGrid API key"): # check if the following error has been raises when there in fact does not exist a key in .env
        EmailService._get_sendgrid_client()
    
def test_get_sender_email_success(monkeypatch): # email exists in .env
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "test@test.com") # change env var to this test email address
    assert EmailService._get_sender_email() == "test@test.com" # make sure the sender email matches
    
def test_get_sender_email_missing_email(monkeypatch): # no email in .env
    monkeypatch.delenv("SENDGRID_FROM_EMAIL", raising=False) # removes it even if it is not set
    with pytest.raises(ValueError, match="Missing SENDGRID_FROM_EMAIL"):
        EmailService._get_sender_email() # make sure that we get the following error message after trying to retrieve sender email
    
def test_get_sender_email_empty_string(monkeypatch):
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", " ") # email address is empty string
    with pytest.raises(ValueError, match="Missing SENDGRID_FROM_EMAIL"):
        EmailService._get_sender_email()
    
def test_build_reminder_message(monkeypatch):
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "admin@mail.com")
    
    mail_object = EmailService.build_reminder_message("user@test.com", "yoga")
    
    mail_dictionary = mail_object.get() # sendgrid mail object dictionary format
    
    assert mail_dictionary["from"]["email"] == "admin@mail.com"
    assert mail_dictionary["personalizations"][0]["to"][0]["email"] == "user@test.com"    
    assert mail_dictionary["subject"] == "Fitness Class Booking Reminder!"
    assert "yoga" in mail_dictionary["content"][0]["value"]
    
@patch("app.services.email_service.EmailService._get_sendgrid_client")
@patch("app.services.email_service.EmailService.build_reminder_message")
def test_send_class_reminder_success(mock_build_message, mock_get_client):
    mock_client_insance = MagicMock()
    
    mock_response = MagicMock()
    mock_response.status_code = 202 # 202 accepted status code
    mock_client_insance.send.return_value = mock_response # when someone calls send, give 202 response
    mock_get_client.return_value = mock_client_insance
    
    success, error = EmailService.send_class_reminder("test@test.com", "yoga")
    
    assert success == True
    assert error == None
    mock_client_insance.send.assert_called_once()
    
@patch("app.services.email_service.EmailService._get_sendgrid_client")
@patch("app.services.email_service.EmailService.build_reminder_message")
def test_send_class_reminder_sendgrid_error(mock_build_message, mock_get_client):
    mock_client_instance = MagicMock()
    
    mock_response = MagicMock()
    mock_response.status_code = 401 # email content when SendGRid rejects email
    mock_response.body = b"Unauthorized"
    mock_client_instance.send.return_value = mock_response # when this gets called just respond with mock_response
    
    mock_get_client.return_value = mock_client_instance
    
    success, error = EmailService.send_class_reminder("test@test.com", "Yoga")
    assert success is False
    assert error is not None
    assert "SendGrid returned status 401: Unauthorized" in error
    
@patch("app.services.email_service.EmailService._get_sendgrid_client")
def test_send_class_reminder_exception(mock_get_client): #testing unexpected exception during process
    mock_get_client.side_effect = Exception("Network timeout") # forcing a hard creash in getting client
    
    success, error = EmailService.send_class_reminder("test@test.com", "Yoga")
    
    assert success is False
    assert error is not None
    assert "Network timeout" in error