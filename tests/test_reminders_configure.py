from http import HTTPStatus

from app.db.users import PREFERRED_NOTIFICATION_METHODS, UserResource


def test_configure_reminders_requires_auth(client):
    response = client.post(
        "/reminders/configure",
        json={"preferred_notification_methods": ["email"]},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_configure_reminders_invalid_role_forbidden(client, invalid_role_headers):
    response = client.post(
        "/reminders/configure",
        headers=invalid_role_headers,
        json={"preferred_notification_methods": ["email"]},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json["message"] == "Current role is not allowed to access this resource"


def test_configure_reminders_invalid_method_returns_not_acceptable(client, member_headers, seeded_member):
    response = client.post(
        "/reminders/configure",
        headers=member_headers,
        json={"preferred_notification_methods": ["sms"]},
    )

    assert response.status_code == HTTPStatus.NOT_ACCEPTABLE
    assert "supported methods" in response.json["message"]


def test_configure_reminders_updates_member_preference(client, app, member_headers, seeded_member):
    response = client.post(
        "/reminders/configure",
        headers=member_headers,
        json={"preferred_notification_methods": ["telegram", "email", "telegram"]},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json["preferred_notification_methods"] == ["telegram", "email"]

    with app.app_context():
        user = UserResource().get_user("test_member")

    assert isinstance(user, dict)
    assert user.get(PREFERRED_NOTIFICATION_METHODS) == ["telegram", "email"]


def test_configure_reminders_updates_trainer_preference(client, app, trainer_headers, seeded_trainer):
    response = client.post(
        "/reminders/configure",
        headers=trainer_headers,
        json={"preferred_notification_methods": ["email"]},
    )

    assert response.status_code == HTTPStatus.OK

    with app.app_context():
        user = UserResource().get_user("test_trainer")

    assert isinstance(user, dict)
    assert user.get(PREFERRED_NOTIFICATION_METHODS) == ["email"]
