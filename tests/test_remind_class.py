import pytest
from unittest.mock import patch
from http import HTTPStatus

# pytest automatically gets client and member_headers and trainer_headers from conftest.py
# forom the @pytest.fixtures defined there

MOCK_GET_USER = "app.apis.classes.UserResource.get_user"
MOCK_GET_CLASS_MEMBERS = "app.apis.classes.ClassResource.get_class_members"
MOCK_GET_CLASS_BY_ID = "app.apis.classes.ClassResource.get_class_by_id"
MOCK_SEND_CLASS_REMINDER = "app.apis.classes.EmailService.send_class_reminder"

# for mocking idfferent types of users in Userresource.get_user
def user_side_effect_helper(user_id):
    if user_id == "member_1":
        return {"_id": "m1", "email": "m1@test.com"}
    if user_id == "member_2":
        return {"_id": "m2", "email": "m2@test.com"}
    if user_id == "missing_email_user":
        return {"_id": "m3", "email": " "}
    if user_id == "failing_email_user":
        return {"_id": "m4", "email": "fail@test.com"}
    
    return {"_id": "trainer_id"} # by defaul return trainer id

def test_remind_class_unauthorized_user(client, member_headers):
    # members should not be able to send reminders
    response = client.post("/classes/remind/some_class_id", headers = member_headers)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json["message"] == "Only trainers allowed"
    
@patch(MOCK_GET_USER) # becomes input no2 for following func
@patch(MOCK_GET_CLASS_MEMBERS) # becomes input no1 for following func
def test_remind_class_invalid_id(mock_get_members, mock_get_user, client, trainer_headers):
    #client and trainer_headers from conftest.py
    mock_get_user.return_value = {"_id": "trainer_id"}
    mock_get_members.return_value = "invalid_class_id" # guarantees that we hit the invalid class id code block
    
    response = client.post("/classes/remind/bad_id", headers=trainer_headers)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json["message"] == "Invalid class id"
    
@patch(MOCK_GET_USER)
@patch(MOCK_GET_CLASS_MEMBERS)
def test_remind_class_not_found(mock_get_members, mock_get_user, client, trainer_headers): # testing class not found
    mock_get_user.return_value = {"_id": "trainer_id"} # we need to simulate succeful finding of trainer in database
    mock_get_members.return_value = "class_not_found" # force code into class not found block
    
    response = client.post("/classes/remind/605c3c2f9f1b2c3d4e5f6a7b", headers = trainer_headers)
    assert response.status_code == HTTPStatus.NOT_FOUND
    
@patch(MOCK_GET_USER)
@patch(MOCK_GET_CLASS_MEMBERS)
def test_remind_class_wrong_trainer(mock_get_members, mock_get_user, client, trainer_headers): # testing trainer tries to access another trainer's class
    mock_get_user.return_value = {"_id": "trainer_id"}
    mock_get_members.return_value = "not_your_class"
    
    response = client.post("/classes/remind/605c3c2f9f1b2c3d4e5f6a7b", headers = trainer_headers)
    
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Only the trainer" in response.json["message"]
    
    
@patch(MOCK_SEND_CLASS_REMINDER)
@patch(MOCK_GET_CLASS_BY_ID)
@patch(MOCK_GET_CLASS_MEMBERS)
@patch(MOCK_GET_USER)
def test_remind_class_success(mock_get_user, mock_get_members, mock_get_class_by_id, mock_send_email, client, trainer_headers):
    mock_get_user.side_effect = user_side_effect_helper # access mock object side effect
    
    mock_get_members.return_value = ["member_1", "member_2"] # 2 members in mock class
    mock_get_class_by_id.return_value = {"class_name": "Yoga"}
    mock_send_email.return_value = (True, None) # simulate email sent out successfully
    
    response = client.post("/classes/remind/valid_id_here", headers = trainer_headers)
    
    assert response.status_code == HTTPStatus.OK
    assert response.json["sent"] == 2 # we should have sent out email to 2 people
    
@patch(MOCK_SEND_CLASS_REMINDER)
@patch(MOCK_GET_CLASS_BY_ID)
@patch(MOCK_GET_CLASS_MEMBERS)
@patch(MOCK_GET_USER)
def test_remind_class_missing_user_emails(mock_get_user, mock_get_members, mock_get_class_by_id, mock_send_email, client, trainer_headers):
    mock_get_user.side_effect = user_side_effect_helper
    
    mock_get_members.return_value = ["missing_email_user", "failing_email_user"] # 2 mems in our class
    mock_get_class_by_id.return_value = {"class_name": "Test Class"}
    mock_send_email.return_value = (False, "Simulated SendGrid timeout") # did not send out successfully
    
    response = client.post("/classes/remind/valid_id_here", headers = trainer_headers)
    
    assert response.status_code == HTTPStatus.OK
    assert response.json["failed"] == 2 # 2 failed emails
    
@patch(MOCK_SEND_CLASS_REMINDER)
@patch(MOCK_GET_CLASS_BY_ID)
@patch(MOCK_GET_CLASS_MEMBERS)
@patch(MOCK_GET_USER)
def test_remind_class_does_not_have_name(mock_get_user, mock_get_members, mock_get_class_by_id, mock_send_email, client, trainer_headers):
    # test branch where class does not have a name and falls back
    mock_get_user.return_value = {"_id": "m1", "email": "m1@test.com"} # this is our singular user
    mock_get_members.return_value = ["member_1"] # we simulate class with 1 member
    
    mock_get_class_by_id.return_value = {} # we force an empty dictionary, which means that the class does not have a name
    mock_send_email.return_value = (True, None) # we force email sender to succesfully report sent out email
    
    response = client.post("/classes/remind/valid_id_here", headers = trainer_headers)
    
    assert response.status_code == HTTPStatus.OK
    mock_send_email.assert_called_with("m1@test.com", "your upcoming class") # the fall back class name is "your upcoming class"