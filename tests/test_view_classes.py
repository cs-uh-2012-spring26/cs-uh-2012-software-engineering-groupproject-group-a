def test_get_all_classes_empty(client):
    response = client.get('/classes')
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"classes": []}

def test_get_all_classes(client, seeded_class):
    response = client.get('/classes')
    assert response.status_code == 200
    data = response.get_json()
    assert "classes" in data
    assert len(data["classes"]) == 1
    assert data["classes"][0]["class_name"] == "Morning Yoga"
    assert data["classes"][0]["location"] == "Studio A"
    assert data["classes"][0]["capacity"] == 20
