def test_health(client):
  response = client.get("/health")

  assert response.status_code == 200
  assert response.get_json() == {"status" : "ok"}

def test_post_invalid_json(client):
  response = client.post(
    "/apps",
    json=[]
  )

  assert response.status_code == 400
  assert response.get_json() == {
    "error" : "Invalid JSON information"
  }

def test_database_health(client):
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}