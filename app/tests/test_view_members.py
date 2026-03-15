# Viesturs

# input explained
# client - makes POST, GET, etc http request to API
# trainer_headers - adds authentication to requests so API knows this is trainer
# member_header - adds authentication to request so API knows this is member not just any client

def test_trainer_can_view_class_members(client, trainer_headers, seeded_trainer, seeded_class):
    response = client.get(f"/classes/{seeded_class['_id']}/members", headers = trainer_headers)
    assert response.status_code == 200 # should get 200 OK http code
    data = response.get_json()
    assert "members" in data
    assert isinstance(data["members"], list) # verifies that data["members"] is indeed a list
    
def test_member_cannot_view_their_class_members(client, app, seeded_class, seeded_member, member_headers):
    # first we must add a member to a class
    from app.db.classes import ClassResource
    with app.app_context():
        resource = ClassResource() # make dummy class and enroll our dummy member into it
        resource.book_class(seeded_member["username"], seeded_class["_id"], seeded_member["_id"])

    response = client.get(f"/classes/{seeded_class['_id']}/members", headers=member_headers)
    assert response.status_code == 403 # 403 forbidden error: only trainers should be able toview member list
    
def test_unauthorized_user_cannot_view_members(client, seeded_class):
    response = client.get(f"/classes/{seeded_class['_id']}/members")
    assert response.status_code == 401 # should receive 401 ... unauthorized status code
    
def test_view_nonexistent_class_members(client, trainer_headers):
    response = client.get("/classes/000000000000000000000000/members", headers = trainer_headers)
    assert response.status_code == 404 # this should return 404 as class does not exist
    
def test_view_class_members_invalid_class_id_returns_422(client, trainer_headers):
    response = client.get("/classes/invalid_id/members", headers = trainer_headers)
    assert response.status_code == 422
    assert response.get_json()["message"] == "Invalid class id"
    
def test_trainer_cannot_view_another_trainers_class_members(client, app, seeded_class):
    from app.db.users import UserResource
    from flask_jwt_extended import create_access_token
    
    with app.app_context(): # create another trainer user
        users = UserResource()
        users.create_user(
            full_name = "Other Trainer",
            username = "other_trainer",
            email = "other_trainer@example.com",
            password = "password123",
            trainer_code = "IAMTRAINER")
        token = create_access_token(
            identity="other_trainer",
            additional_claims = {"role": "trainer", "full_name": "Other Trainer"},
        )
    
    other_trainer_headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(
        f"/classes/{seeded_class['_id']}/members",
        headers = other_trainer_headers,
    )
    assert response.status_code == 403
    assert response.get_json()["message"] == "Only the trainer of this class can view its members"