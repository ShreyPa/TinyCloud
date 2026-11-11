from unittest.mock import MagicMock, patch
from main import app

def test_sync_exited_to_stopped():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.get_container") as mock_docker:

        fake_conn = MagicMock()
        mock_db.return_value = fake_conn

        fake_cursor = fake_conn.cursor.return_value.__enter__.return_value

        fake_cursor.fetchone.return_value = {
            "id": 1,
            "name": "test-app",
            "status": "running",
            "container_id": "abc123"
        }

        mock_docker.return_value = (
            {"id": "abc123", "status": "exited"},
            200
        )

        client = app.test_client()
        response = client.get("/apps/test-app")

        assert response.status_code == 200
        assert response.get_json()["app"]["status"] == "stopped"
        fake_conn.commit.assert_called_once()
        print(fake_cursor.execute.call_args_list)

        fake_cursor.execute.assert_any_call(
        "UPDATE apps SET status = %s WHERE id = %s",
        ("stopped", 1)
        )

def test_sync_stopped_to_running():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.get_container") as mock_docker:

        fake_conn = MagicMock()
        mock_db.return_value = fake_conn

        fake_cursor = fake_conn.cursor.return_value.__enter__.return_value

        fake_cursor.fetchone.return_value = {
            "id": 1,
            "name": "test-app",
            "status": "stopped",
            "container_id": "abc123"
        }

        mock_docker.return_value = (
            {"id": "abc123", "status": "running"},
            200
        )

        client = app.test_client()
        response = client.get("/apps/test-app")

        assert response.status_code == 200
        assert response.get_json()["app"]["status"] == "running"
        fake_conn.commit.assert_called_once()
        print(fake_cursor.execute.call_args_list)

        fake_cursor.execute.assert_any_call(
        "UPDATE apps SET status = %s WHERE id = %s",
        ("running", 1)
        )
  
def test_sync_status_already_matches():
    with patch("main.get_db_connection") as mock_db, \
         patch("main.get_container") as mock_docker:

        fake_conn = MagicMock()
        mock_db.return_value = fake_conn

        fake_cursor = fake_conn.cursor.return_value.__enter__.return_value

        fake_cursor.fetchone.return_value = {
            "id": 1,
            "name": "test-app",
            "status": "running",
            "container_id": "abc123"
        }

        mock_docker.return_value = (
            {"id": "abc123", "status": "running"},
            200
        )

        client = app.test_client()
        response = client.get("/apps/test-app")

        assert response.status_code == 200
        assert response.get_json()["app"]["status"] == "running"
        fake_conn.commit.assert_not_called()
        assert fake_cursor.execute.call_count == 1

def test_app_without_container():
  with patch("main.get_db_connection") as mock_db, \
        patch("main.get_container") as mock_docker:

      fake_conn = MagicMock()
      mock_db.return_value = fake_conn

      fake_cursor = fake_conn.cursor.return_value.__enter__.return_value

      fake_cursor.fetchone.return_value = {
          "id": 5,
          "name": "netflix",
          "status": "stopped",
          "container_id": None
      }

      client = app.test_client()
      response = client.get("/apps/netflix")

      assert response.status_code == 200
      assert response.get_json()["app"]["name"] == "netflix"
      mock_docker.assert_not_called()
      fake_conn.commit.assert_not_called()  

def test_sync_container_not_found():
  with patch("main.get_db_connection") as mock_db, \
          patch("main.get_container") as mock_docker:

        fake_conn = MagicMock()
        mock_db.return_value = fake_conn

        fake_cursor = fake_conn.cursor.return_value.__enter__.return_value

        fake_cursor.fetchone.return_value = {
            "id": 1,
            "name": "test-app",
            "status": "running",
            "container_id": "abc123"
        }

        mock_docker.return_value = (
            {"error": "Container not found"},
            404
        )

        client = app.test_client()
        response = client.get("/apps/test-app")

        assert response.status_code == 200
        assert response.get_json()["app"]["status"] == "running"
        fake_conn.commit.assert_not_called()  
        mock_docker.assert_called_once_with("abc123")
        assert response.get_json()["app"]["docker_status"] is None
        assert response.get_json()["app"]["docker_error"] == "Container not found"

def test_sync_docker_unavailable():
  with patch("main.get_db_connection") as mock_db, \
            patch("main.get_container") as mock_docker:

          fake_conn = MagicMock()
          mock_db.return_value = fake_conn

          fake_cursor = fake_conn.cursor.return_value.__enter__.return_value

          fake_cursor.fetchone.return_value = {
              "id": 1,
              "name": "test-app",
              "status": "running",
              "container_id": "abc123"
          }

          mock_docker.return_value = (
              {"error": "Docker service unavailable"},
              503
          )

          client = app.test_client()
          response = client.get("/apps/test-app")

          assert response.status_code == 200
          assert response.get_json()["app"]["status"] == "running"
          fake_conn.commit.assert_not_called()  
          mock_docker.assert_called_once_with("abc123")
          assert response.get_json()["app"]["docker_status"] is None
          assert response.get_json()["app"]["docker_error"] == "Docker service unavailable"