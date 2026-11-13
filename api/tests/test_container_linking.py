from unittest.mock import MagicMock, patch
from main import app

def test_link_running_container():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.validate_container") as mock_docker:

        fake_conn = MagicMock()
        mock_db.return_value = fake_conn

        fake_cursor = fake_conn.cursor.return_value.__enter__.return_value

        fake_cursor.fetchone.return_value = {
              "id": 1,
              "name": "test-app",
              "status": "stopped",
              "container_id": None
          }
        
        mock_docker.return_value = (
        {"id": "abc123", "status": "running"},
        200
        )

        fake_cursor.fetchone.side_effect = [
        {
            "id": 1,
            "name": "test-app",
            "status": "stopped",
            "container_id": None
        },
        {
            "id": 1,
            "name": "test-app",
            "status": "running",
            "container_id": "abc123"
        }
    ]

        client = app.test_client()

        response = client.put(
            "/apps/test-app/container",
            json={"container_id": "abc123"}
        )

        assert response.status_code == 200
        assert response.get_json()["app"]["container_id"] == "abc123"
        assert response.get_json()["app"]["status"] == "running"
        mock_docker.assert_called_once_with("abc123")
        fake_conn.commit.assert_called_once()  
        fake_cursor.execute.assert_any_call(
            "UPDATE apps SET container_id = %s, status = %s WHERE id = %s RETURNING *",
            ("abc123", "running", 1)
        )

def test_link_stopped_container():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.validate_container") as mock_docker:

        fake_conn = MagicMock()
        mock_db.return_value = fake_conn

        fake_cursor = fake_conn.cursor.return_value.__enter__.return_value
        
        fake_cursor.fetchone.side_effect = [
        {
            "id": 1,
            "name": "test-app",
            "status": "running",
            "container_id": None
        },
        {
            "id": 1,
            "name": "test-app",
            "status": "stopped",
            "container_id": "abc123"
        }
    ]

        mock_docker.return_value = (
            {"id": "abc123", "status": "exited"},
            200
        )


        client = app.test_client()

        response = client.put(
            "/apps/test-app/container",
            json={"container_id": "abc123"}
        )

        assert response.status_code == 200
        assert response.get_json()["app"]["container_id"] == "abc123"
        assert response.get_json()["app"]["status"] == "stopped"
        mock_docker.assert_called_once_with("abc123")
        fake_conn.commit.assert_called_once()  
        fake_cursor.execute.assert_any_call(
            "UPDATE apps SET container_id = %s, status = %s WHERE id = %s RETURNING *",
            ("abc123", "stopped", 1)
        )

def test_link_container_not_found():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.validate_container") as mock_docker:

        mock_docker.return_value = (
            {"error": "Container not found"},
            404
        )

        client = app.test_client()

        response = client.put(
            "/apps/test-app/container",
            json={"container_id": "fake-container"}
        )

        assert response.status_code == 404
        assert response.get_json()["error"] == "Container not found"
        mock_docker.assert_called_once_with("fake-container")
        mock_db.assert_not_called()
      
def test_link_unmanaged_container():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.validate_container") as mock_docker:

        mock_docker.return_value = (
        {"error": "Container is not managed by TinyCloud"},
        403
        ) 

        client = app.test_client()

        response = client.put(
            "/apps/test-app/container",
            json={"container_id": "tinycloud-db-1"}
        )

        assert response.status_code == 403
        assert response.get_json()["error"] == "Container is not managed by TinyCloud"
        mock_docker.assert_called_once_with("tinycloud-db-1")
        mock_db.assert_not_called()
        
def test_link_docker_unavailable():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.validate_container") as mock_docker:

        mock_docker.return_value = (
        {"error": "Docker service unavailable"},
        503
        ) 

        client = app.test_client()

        response = client.put(
            "/apps/test-app/container",
            json={"container_id": "abc123"}
        )

        assert response.status_code == 503
        assert response.get_json()["error"] == "Docker service unavailable"
        mock_docker.assert_called_once_with("abc123")
        mock_db.assert_not_called()
    
def test_link_app_not_found():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.validate_container") as mock_docker:

        fake_conn = MagicMock()
        mock_db.return_value = fake_conn

        fake_cursor = fake_conn.cursor.return_value.__enter__.return_value

        mock_docker.return_value = (
        {"id": "abc123", "status": "running"},
        200
        )

        fake_cursor.fetchone.return_value = None
        client = app.test_client()

        response = client.put(
            "/apps/fake-app/container",
            json={"container_id": "abc123"}
        )

        assert response.status_code == 404
        assert response.get_json()["error"] == "App not found"
        mock_docker.assert_called_once_with("abc123")
        mock_db.assert_called_once()
        fake_conn.commit.assert_not_called()
        assert fake_cursor.execute.call_count == 1

def test_link_invalid_container_id():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.validate_container") as mock_docker:

        client = app.test_client()

        response = client.put(
            "/apps/test-app/container",
            json={"container_id": 123}
        )
        
        assert response.status_code == 400
        assert response.get_json()["error"] == "Container ID must be a string"
        mock_docker.assert_not_called()
        mock_db.assert_not_called()
      
def test_link_missing_container_id():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.validate_container") as mock_docker:

        client = app.test_client()

        response = client.put(
            "/apps/test-app/container",
            json={}
        )

        assert response.status_code == 400
        assert response.get_json()["error"] == "container id is required"
        mock_docker.assert_not_called()
        mock_db.assert_not_called()

def test_link_empty_container():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.validate_container") as mock_docker:

        client = app.test_client()

        response = client.put(
            "/apps/test-app/container",
            json={"container_id": "  "}
        )

        assert response.status_code == 400
        assert response.get_json()["error"] == "Container ID cannot be empty"
        mock_docker.assert_not_called()
        mock_db.assert_not_called()

def test_link_invalid_json():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.validate_container") as mock_docker:

        client = app.test_client()

        response = client.put(
            "/apps/test-app/container",
            json=["abc123"]
        )

        assert response.status_code == 400
        assert response.get_json()["error"] == "Invalid JSON data"
        mock_docker.assert_not_called()
        mock_db.assert_not_called()