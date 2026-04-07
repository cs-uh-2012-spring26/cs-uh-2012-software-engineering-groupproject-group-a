import pytest
from flask_jwt_extended import create_access_token

@pytest.mark.parametrize(
	"class_id,expected_status,expected_message",
	[
		("invalid_id", 422, "Invalid class id"),
		("000000000000000000000000", 404, "Class not found"),
	],
)
def test_book_class_parametrized_failures(
	client,
	class_id,
	expected_status,
	expected_message,
	member_headers,
	seeded_member,
):
	response = client.post(f"/classes/{class_id}/book", headers=member_headers)

	assert response.status_code == expected_status
	assert response.get_json()["message"] == expected_message


def test_member_can_book_class_success(client, member_headers, seeded_class, seeded_member):
	response = client.post(f"/classes/{seeded_class['_id']}/book", headers=member_headers)

	assert response.status_code == 200
	assert response.get_json()["message"] == "Class booked successfully"


def test_user_already_booked_returns_conflict(
	client,
	app,
	member_headers,
	seeded_class,
	seeded_member,
):
	from app.db.classes import ClassResource

	with app.app_context():
		resource = ClassResource()
		resource.book_class(seeded_member["username"], seeded_class["_id"], seeded_member["_id"])

	response = client.post(f"/classes/{seeded_class['_id']}/book", headers=member_headers)

	assert response.status_code == 409
	assert response.get_json()["message"] == "User already booked this class"


def test_trainer_cannot_book_own_class(client, trainer_headers, seeded_class, seeded_trainer):
	response = client.post(f"/classes/{seeded_class['_id']}/book", headers=trainer_headers)

	assert response.status_code == 403
	assert response.get_json()["message"] == "Trainer cannot book their own class"


def test_unauthorized_user_cannot_book_class(client, seeded_class):
	response = client.post(f"/classes/{seeded_class['_id']}/book")

	assert response.status_code == 401
	assert response.get_json()["message"] == "Missing Authorization Header"


def test_forbidden_role_cannot_book_class(client, invalid_role_headers):
	response = client.post("/classes/000000000000000000000000/book", headers=invalid_role_headers)

	assert response.status_code == 403
	assert response.get_json()["message"] == "Only trainers and members allowed"


def test_book_class_user_not_found_returns_404(client, member_headers, seeded_class, monkeypatch):
	from app.apis import classes as classes_api

	def fake_get_user(self, username):
		return None

	monkeypatch.setattr(classes_api.UserResource, "get_user", fake_get_user)

	response = client.post(f"/classes/{seeded_class['_id']}/book", headers=member_headers)

	assert response.status_code == 404
	assert response.get_json()["message"] == "User not found"


def test_book_class_failed_returns_400(client, member_headers, seeded_class, seeded_member, monkeypatch):
	from app.apis import classes as classes_api

	def fake_book_class(self, username, class_id, user_id):
		return "booking_failed"

	monkeypatch.setattr(classes_api.ClassResource, "book_class", fake_book_class)

	response = client.post(f"/classes/{seeded_class['_id']}/book", headers=member_headers)

	assert response.status_code == 400
	assert response.get_json()["message"] == "Failed to book class"


def test_cannot_book_class_when_capacity_is_full(client, app, seeded_class, seeded_member):
	from app.db.users import UserResource
	from app.db.classes import ClassResource
	from bson import ObjectId

	# first member takes the last available spot
	with app.app_context():
		class_resource = ClassResource()
		class_resource.collection.update_one(
			{"_id": ObjectId(seeded_class["_id"])},
			{"$set": {"capacity": 1}},
		)
		class_resource.book_class(seeded_member["username"], seeded_class["_id"], seeded_member["_id"])

		# create a second member and token for the new booking attempt
		user_resource = UserResource()
		user_resource.create_user(
			full_name="Second Member",
			username="second_member",
			email="second_member@example.com",
			password="password123",
		)
		second_headers = {
			"Authorization": f"Bearer {create_access_token(identity='second_member', additional_claims={'role': 'member', 'full_name': 'Second Member'})}"
		}

	response = client.post(f"/classes/{seeded_class['_id']}/book", headers=second_headers)

	assert response.status_code == 403
	assert response.get_json()["message"] == "Class is full"
