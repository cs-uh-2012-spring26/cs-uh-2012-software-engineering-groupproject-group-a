import pytest


@pytest.mark.parametrize(
    "class_name,start_date,end_date,location,capacity,expected_status",
    [
        ("", "2026-02-20T09:00:00Z", "2026-02-20T10:00:00Z", "Studio ZA", 20, 406),
        ("Yoga Strength", "", "2026-02-20T10:00:00Z", "Studio ZA", 20, 406),
        ("Yoga Strength", "2026-02-20T09:00:00Z", "", "Studio ZA", 20, 406),
        ("Yoga Strength", "2026-02-20T09:00:00Z", "2026-02-20T10:00:00Z", "", 20, 406),
        ("Yoga Strength", "2026-02-20T09:00:00Z", "2026-02-20T10:00:00Z", "Studio ZA", 0, 406),
        ("Yoga Strength", "2026-02-20T09:00:00Z", "2026-02-20T10:00:00Z", "Studio ZA", -1, 406),
        ("Yoga Strength", "2026-02-20T09:00:00Z", "2026-02-20T10:00:00Z", "Studio ZA", "0", 500),
        ("Yoga Strength", "2026-02-20T09:00:00Z", "2026-02-20T10:00:00Z", "Studio ZA", 20, 201),
    ],
)
def test_trainer_create_class_not_acceptable(client,trainer_headers,class_name,start_date,end_date,location,capacity,expected_status,):
    response = client.post(
        "/classes/create-class",
        headers=trainer_headers,
        json={
            "class_name": class_name,
            "start_date": start_date,
            "end_date": end_date,
            "location": location,
            "capacity": capacity,
        },
    )

    assert response.status_code == expected_status


def test_member_create_class_forbidden(client, member_headers):
    response = client.post(
        "/classes/create-class",
        headers=member_headers,
        json={
            "class_name": "Yoga Strength",
            "start_date": "2026-02-20T09:00:00Z",
            "end_date": "2026-02-20T10:00:00Z",
            "location": "Studio ZA",
            "capacity": 20,
        },
    )

    assert response.status_code == 403


def test_create_class_failed_create_returns_400(client, trainer_headers, monkeypatch):
    from app.apis import classes as classes_api

    # this function will replace create_class of ClassResource for this test
    def fake_create_class(self, **kwargs):
        return None
    # replace here
    monkeypatch.setattr(classes_api.ClassResource, "create_class", fake_create_class)
    # try to create class, runs into fake_create_class which returns none 
    response = client.post(
        "/classes/create-class",
        headers=trainer_headers,
        json={
            "class_name": "Yoga Strength",
            "start_date": "2026-02-20T09:00:00Z",
            "end_date": "2026-02-20T10:00:00Z",
            "location": "Studio ZA",
            "capacity": 20,
        },
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Failed to create class"
