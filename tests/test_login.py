import pytest


def test_login_success(client, seeded_member):
    response = client.post(
        "/auth/login",
        json={"username": seeded_member["username"], "password": "password123"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Logged in successfully"
    assert isinstance(data.get("access_token"), str)
    assert len(data["access_token"]) > 0


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
