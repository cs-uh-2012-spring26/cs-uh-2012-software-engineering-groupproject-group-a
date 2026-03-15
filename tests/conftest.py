import os

import pytest
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token


@pytest.fixture(scope="session", autouse=True)
def app():
    os.environ["MOCK_DB"] = "true"
    from app import create_app      # we import here so it sets the mock_db env before import
    app = create_app()
    from app.db import DB           # We import after "os.environ["MOCK_DB"]='true'" so it doesnt not set mock_db to false 
    assert "mongomock" in type(DB._get().client).__module__ # checks if were using mock
    yield app


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def clear_db(app):
    from app.db import DB

    # drop all test collection before each test so tests are fully isolated
    # runs automatically for every test
    with app.app_context():
        db = DB._get()
        for name in db.list_collection_names():
            db.drop_collection(name)
    yield

# auth header helper
def _make_auth_headers(app, username: str, role: str, full_name: str = "Test User") -> dict:
    """Return an Authorization header dict with a valid JWT for the given user."""
    with app.app_context():
        token = create_access_token(
            identity=username,
            additional_claims={"role": role, "full_name": full_name},
        )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def trainer_headers(app):
    # auth header for a trainer user
    return _make_auth_headers(app, username="test_trainer", role="trainer", full_name="Test Trainer")


@pytest.fixture()
def member_headers(app):
    return _make_auth_headers(app, username="test_member", role="member", full_name="Test Member")


@pytest.fixture()
def invalid_role_headers(app):
    return _make_auth_headers(app, username="test_guest", role="guest", full_name="Test Guest")

# trainer for testing
@pytest.fixture()
def seeded_trainer(app):
    from app.db.users import UserResource
    with app.app_context():
        resource = UserResource()
        resource.create_user(
            full_name="Test Trainer",
            username="test_trainer",
            email="test_trainer@example.com",
            password="password123",
            trainer_code="IAMATRAINER",
        )
        return resource.get_user("test_trainer")

# member for testing
@pytest.fixture()
def seeded_member(app):
    from app.db.users import UserResource
    with app.app_context():
        resource = UserResource()
        resource.create_user(
            full_name="Test Member",
            username="test_member",
            email="test_member@example.com",
            password="password123",
        )
        return resource.get_user("test_member")

# class for testing
@pytest.fixture()
def seeded_class(app, seeded_trainer):
    from app.db.classes import ClassResource
    with app.app_context():
        resource = ClassResource()
        created = resource.create_class(
            class_name="Morning Yoga",
            start_date="2026-03-01T09:00:00Z",
            end_date="2026-03-01T10:00:00Z",
            location="Studio A",
            capacity=20,
            trainer_id=seeded_trainer["_id"],
        )
        return created
