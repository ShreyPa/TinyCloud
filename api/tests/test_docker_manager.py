from unittest.mock import MagicMock, patch
from docker_manager import start_container, stop_container, get_container, get_containers, validate_container
import docker 

def test_start_already_running():
    container = MagicMock()

    container.name = "tinycloud-test"
    container.status = "running"
    container.labels = {"tinycloud.managed": "true"}

    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.return_value = container

        response, status = start_container("tinycloud-test")

        assert status == 200
        assert response["message"] == "tinycloud-test is already running"

        container.start.assert_not_called()

def test_start_stopped_container():
    container = MagicMock()

    container.name = "tinycloud-test"
    container.status = "exited"
    container.labels = {"tinycloud.managed": "true"}

    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.return_value = container

        response, status = start_container("tinycloud-test")

        assert status == 200
        assert response["message"] == "tinycloud-test has started"
        container.start.assert_called_once()

def test_start_unmanaged_container():
    container = MagicMock()

    container.name = "random-container"
    container.status = "exited"
    container.labels = {}

    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.return_value = container

        response, status = start_container("random-container")

        assert status == 403
        assert response["error"] == "Container is not managed by TinyCloud"
        container.start.assert_not_called()
  
def test_start_nonexistent_container():
    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.side_effect = docker.errors.NotFound(
            "Not found"
        )

        response, status = start_container("fake-container")

        assert status == 404
        assert response["error"] == "Container not found"

def test_stop_running_container():
    container = MagicMock()

    container.name = "tinycloud-test"
    container.status = "running"
    container.labels = {"tinycloud.managed": "true"}

    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.return_value = container

        response, status = stop_container("tinycloud-test")

        # Your assertions here
        assert status == 200
        assert response["message"] == "tinycloud-test has been stopped"
        container.stop.assert_called_once()

def test_stop_already_stopped():
    container = MagicMock()

    container.name = "tinycloud-test"
    container.status = "exited"
    container.labels = {"tinycloud.managed": "true"}

    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.return_value = container

        response, status = stop_container("tinycloud-test")

        assert status == 200
        assert response["message"] == "tinycloud-test has already been stopped"
        container.stop.assert_not_called()
      
def test_stop_unmanaged_container():
    container = MagicMock()

    container.name = "random-container"
    container.status = "running"
    container.labels = {}

    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.return_value = container

        response, status = stop_container("random-container")

        assert status == 403
        assert response["error"] == "Container is not managed by TinyCloud"
        container.stop.assert_not_called()

def test_stop_nonexistent_container():
    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.side_effect = docker.errors.NotFound(
            "Not found"
        )

        response, status = stop_container("fake-container")

        assert status == 404
        assert response["error"] == "Container not found"
        mock_client.containers.get.assert_called_once()

def test_get_container():
    container = MagicMock()

    container.name = "tinycloud-test"
    container.id = "abc123"
    container.status = "running"
    container.labels = {"tinycloud.managed": "true"}

    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.return_value = container

        response, status = get_container("tinycloud-test")

        # Your assertions here
        assert status == 200
        assert response["name"] == "tinycloud-test"
        assert response["id"] == "abc123"
        assert response["status"] == "running"

def test_get_nonexistent_container():
    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.side_effect = docker.errors.NotFound(
            "Not found"
        )

        response, status = get_container("fake-container")

        # Your assertions here
        assert status == 404
        assert response["error"] == "Container not found"
        mock_client.containers.get.assert_called_once()

def test_get_containers():
    managed = MagicMock()
    managed.name = "tinycloud-test"
    managed.id = "abc123"
    managed.status = "running"
    managed.labels = {"tinycloud.managed": "true"}

    unmanaged = MagicMock()
    unmanaged.name = "random-container"
    unmanaged.id = "xyz789"
    unmanaged.status = "exited"
    unmanaged.labels = {}

    with patch("docker_manager.client") as mock_client:
        mock_client.containers.list.return_value = [managed, unmanaged]

        response, status = get_containers()

        assert status == 200
        assert len(response["containers"]) == 1
        assert response["containers"][0]["name"] == "tinycloud-test"
        mock_client.containers.list.assert_called_once_with(all=True)

        # Your assertions here

def test_get_containers_empty():
    with patch("docker_manager.client") as mock_client:
        mock_client.containers.list.return_value = []

        response, status = get_containers()

        # Your assertions here
        assert status == 200
        assert response["containers"] == []
        mock_client.containers.list.assert_called_once_with(all=True)

def test_get_container_docker_error():
    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.side_effect = docker.errors.DockerException(
            "Docker unavailable"
        )

        response, status = get_container("tinycloud-test")

        assert status == 503
        assert response["error"] == "Docker service unavailable"
        # Your assertions here

def test_start_container_docker_error():
    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.side_effect = docker.errors.DockerException(
            "Docker unavailable"
        )

        response, status = start_container("tinycloud-test")

    assert status == 503
    assert response["error"] == "Docker service unavailable"

def test_stop_container_docker_error():
    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.side_effect = docker.errors.DockerException(
            "Docker unavailable"
        )

        response, status = stop_container("tinycloud-test")

        assert status == 503
        assert response["error"] == "Docker service unavailable"

def test_get_containers_docker_error():
    with patch("docker_manager.client") as mock_client:
        mock_client.containers.list.side_effect = docker.errors.DockerException(
            "Docker unavailable"
        )

        response, status = get_containers()

        # Your assertions here
        assert status == 503
        assert response["error"] == "Docker service unavailable"


def test_get_container_success():
    with patch("docker_manager.client") as mock_client:

        mock_container = MagicMock()

        mock_container.name = "test-container"
        mock_container.id = "abc123"
        mock_container.status = "running"
        mock_container.labels = {"tinycloud.managed": "true"}

        mock_client.containers.get.return_value = mock_container

        result, status_code = get_container("test-container")

        assert status_code == 200
        assert result["name"] == "test-container"
        assert result["status"] == "running"

def test_validate_managed_container():
    with patch("docker_manager.client") as mock_client:

        mock_container = MagicMock()
        mock_container.id = "abc123"
        mock_container.status = "running"
        mock_container.labels = {"tinycloud.managed": "true"}

        mock_client.containers.get.return_value = mock_container

        result, status_code = validate_container("test-container")

        assert status_code == 200
        assert result["id"] == "abc123"
        assert result["status"] == "running"

        mock_client.containers.get.assert_called_once_with(
            "test-container"
        )

def test_validate_unmanaged_container():
    with patch("docker_manager.client") as mock_client:
        mock_container = MagicMock()

        mock_container.labels = {
            "tinycloud.managed": "false"
        }

        mock_client.containers.get.return_value = mock_container
        result, status_code = validate_container("test-container")

        assert status_code == 403
        assert result["error"] == "Container is not managed by TinyCloud"
        mock_client.containers.get.assert_called_once_with("test-container")

def test_validate_container_not_found():
    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.side_effect = docker.errors.NotFound(
        "Container not found"
        )

        result, status_code = validate_container("fake-container")

        assert status_code == 404
        assert result["error"] == "Container not found"
        mock_client.containers.get.assert_called_once_with("fake-container")

def test_validate_docker_unavailable():
    with patch("docker_manager.client") as mock_client:
        mock_client.containers.get.side_effect = docker.errors.DockerException(
        "Docker service unavailable"
        )

        result, status_code = validate_container("test-container")

        assert status_code == 503
        assert result["error"] == "Docker service unavailable"
        mock_client.containers.get.assert_called_once_with("test-container")