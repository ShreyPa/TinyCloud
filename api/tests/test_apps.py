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

def test_duplicate_app(client):
    app_data = {
        "name": "spotify",
        "status": "running"
    }

    response1 = client.post("/apps", json=app_data)
    response2 = client.post("/apps", json=app_data)

    assert response1.status_code == 201
    assert response2.status_code == 409
    assert response2.get_json() == { "error": "nah twin ts cant work like that"}

def test_updating_app(client):

  response1 = client.post("/apps", json = {
    "name" : "netflix",
    "status" : "stopped"
  })

  response2 = client.put("/apps/netflix", json = {"status" : "running"})
  response3 = client.get("/apps/netflix")
  
  assert response1.status_code == 201
  assert response2.status_code == 200
  assert response2.get_json()["app"]["status"] == "running"
  assert response3.status_code == 200
  assert response3.get_json()["app"]["status"] == "running"

def test_deleting_app(client):
  response1 = client.post("/apps", json = {
    "name" : "spotify",
    "status" : "running"
  })

  response2 = client.delete("/apps/spotify")
  response3 = client.get("/apps/spotify")
  
  assert response1.status_code == 201
  assert response2.status_code == 200
  assert response3.status_code == 404
  assert response3.get_json() == {"error" : "app not found"}

def test_missing_application(client):
  response = client.post(
    "/apps",
    json={"status":"running"}
  )

  assert response.status_code == 400
  assert response.get_json() == {
    "error" : "name is required"
  }

def test_invalid_status(client):
  response = client.post(
    "/apps",
    json={
      "name" : "netflix",
      "status":"running"}
  )

  response1 = client.put(
      "/apps/netflix",
      json={
        "status" : "flying"
      }
    )

  response2 = client.get("/apps/netflix")

  assert response.status_code == 201
  assert response1.status_code == 400
  assert response2.status_code == 200
  assert response2.get_json()["app"]["status"] == "running"

def test_nonexistent_app(client):
    response = client.get("/apps/doesnotexist")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "app not found"
    }