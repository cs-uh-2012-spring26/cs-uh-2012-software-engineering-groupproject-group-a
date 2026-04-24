from unittest.mock import patch
from http import HTTPStatus

def test_register_member_success(client):
    data = {
        "full_name": "John Doe",
        "username": "john_doe",
        "email": "john@example.com",
        "password": "password123"
    }
    response = client.post('/auth/register', json=data)
    assert response.status_code == HTTPStatus.CREATED


def test_register_trainer_success(client):
    data = {
        "full_name": "Jane Trainer",
        "username": "jane_trainer",
        "email": "jane@example.com",
        "password": "password123",
        "trainer_code": "IAMATRAINER"
    }
    response = client.post('/auth/register', json=data)
    assert response.status_code == HTTPStatus.CREATED


def test_register_invalid_input_empty_strings(client):
    data = {
        "full_name": "",
        "username": "",
        "email": "",
        "password": ""
    }
    response = client.post('/auth/register', json=data)
    assert response.status_code == HTTPStatus.NOT_ACCEPTABLE
    
def test_register_duplicate_username(client, seeded_trainer):
    data = {
        "full_name": "New User",
        "username": seeded_trainer["username"],  # Use seeded trainer's username
        "email": "new@example.com",
        "password": "password456"
    }
    response = client.post('/auth/register', json=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    
def test_register_duplicate_email(client, seeded_member):
    data = {
        "full_name": "New User",
        "username": "new_username",
        "email": seeded_member["email"],  # Use seeded member's email
        "password": "password456"
    }
    response = client.post('/auth/register', json=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
   
def test_register_failed(client):
    data = {
        "full_name": "Fail User",
        "username": "fail_user",
        "email": "fail@example.com",
        "password": "password123"
    }
    with patch('app.apis.auth.UserResource.create_user', return_value=(None,None)):
        response = client.post('/auth/register', json=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
      