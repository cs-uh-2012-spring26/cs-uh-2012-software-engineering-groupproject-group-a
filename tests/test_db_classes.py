from app.db.classes import ClassResource, ClassResult


def test_get_class_by_id_returns_invalid_id_for_bad_object_id(app):
    # give an invalid id format and make sure we get INVALID_ID instead of a crash
    with app.app_context():
        resource = ClassResource()
        result = resource.get_class_by_id("not_a_mongo_object_id")

    assert result == ClassResult.INVALID_ID


def test_get_class_by_id_returns_not_found_for_missing_document(app):
    # valid ObjectId format, but no class exists with this id in the test db
    with app.app_context():
        resource = ClassResource()
        result = resource.get_class_by_id("000000000000000000000000")

    assert result == ClassResult.NOT_FOUND


def test_get_class_by_id_returns_serialized_class_when_present(app, seeded_class):
    # class exists, so we should get back a serialized class dictionary
    with app.app_context():
        resource = ClassResource()
        result = resource.get_class_by_id(seeded_class["_id"])

    assert isinstance(result, dict)
    assert result.get("_id") == seeded_class["_id"]
    assert result.get("class_name") == seeded_class["class_name"]


def test_book_class_returns_fail_when_update_does_not_modify_document(app, seeded_class, seeded_member, monkeypatch):
    # force update_one to report modified_count=0 so we hit the FAIL return path
    class _NoOpUpdateResult:
        modified_count = 0

    def fake_update_one(_filter, _update):
        return _NoOpUpdateResult()

    with app.app_context():
        resource = ClassResource()
        monkeypatch.setattr(resource.collection, "update_one", fake_update_one)
        result = resource.book_class(
            seeded_member["username"],
            seeded_class["_id"],
            seeded_member["_id"],
        )

    assert result == ClassResult.FAIL
