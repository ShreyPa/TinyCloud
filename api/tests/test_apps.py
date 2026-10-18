def test_get_all_apps(client):

    response = client.get("/apps")

    assert response.status_code == 200

    data = response.get_json()

    assert "apps" in data
    assert isinstance(data["apps"], list)

def test_create_app(client):

    response = client.post("/apps", json={
        "name": "spotify",
        "status": "running"
    })

    assert response.status_code == 201