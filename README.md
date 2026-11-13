# TinyCloud

A lightweight container management platform built with Python, Flask, Docker, and PostgreSQL.

TinyCloud provides a REST API for managing application records, controlling Docker containers, and synchronizing application state with the underlying container infrastructure.

## Overview

TinyCloud was built as a hands-on infrastructure engineering project to explore how backend APIs, container orchestration, databases, and automated testing work together.

The platform connects application metadata stored in PostgreSQL with real Docker containers, providing a centralized interface for managing application lifecycle operations.

## Features

- REST API for creating, retrieving, updating, and deleting applications.
- Docker container inspection, listing, starting, and stopping.
- Automatic linking of application records to existing Docker containers.
- Synchronization of application status between PostgreSQL and Docker.
- Managed-container permission checks using Docker labels.
- Input validation and structured error responses.
- PostgreSQL persistence using Docker volumes.
- Environment-based configuration and secret management.
- Automated development and testing scripts.
- 48 passing automated tests covering API functionality, Docker operations, database integration, and error handling.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Backend development |
| Flask | REST API framework |
| PostgreSQL 16 | Application database |
| Docker | Container management |
| Docker Compose | Infrastructure configuration |
| Docker SDK for Python | Docker Engine communication |
| psycopg2 | PostgreSQL connectivity |
| pytest | Automated testing |
| Bash | Development and testing automation |

## Architecture

```text
                   Client
                     |
                     v
              Flask REST API
                /         \
               /           \
              v             v
       PostgreSQL       Docker SDK
       Application           |
         Records             v
                       Docker Engine
                             |
                             v
                     Managed Containers
```

Flask serves as the central interface between the database and Docker Engine.

PostgreSQL stores application metadata, including application names, statuses, and associated container IDs. Docker Engine provides the actual container state and lifecycle operations.

TinyCloud restricts container operations to containers labeled:

```text
tinycloud.managed=true
```

## Project Structure

```text
TinyCloud/
├── api/
│   ├── main.py
│   ├── docker_manager.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── test_docker_manager.py
│   └── tests/
│       ├── conftest.py
│       ├── test_apps.py
│       ├── test_health.py
│       ├── test_app_sync.py
│       └── test_container_linking.py
├── docker-compose.yml
├── dev.sh
├── test.sh
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12
- Docker Desktop or Docker Engine
- Docker Compose
- Git

### 1. Configure the Python environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
```

### 2. Configure environment variables

Create a local environment file:

```bash
cp .env.example .env
```

Set the database password in `.env`.

Example configuration:

```env
DB_HOST=localhost
DB_NAME=tinycloud
DB_USER=tinycloud
DB_PASSWORD=your_password_here

FLASK_HOST=127.0.0.1
FLASK_PORT=5001
FLASK_DEBUG=false
```

### 3. Start PostgreSQL

```bash
docker compose up -d db
```

### 4. Start TinyCloud

```bash
chmod +x dev.sh
./dev.sh
```

The API is available at:

```text
http://localhost:5001
```

On first startup, PostgreSQL automatically executes `db/init.sql`, creating the application schema and a separate `tinycloud_test` database for integration testing.

Initialization runs only when the PostgreSQL data volume is empty. Existing database volumes retain their data and are not automatically reinitialized.

## API Reference

### Health Checks

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API health |
| GET | `/health/db` | Check database connectivity |

### Application Management

| Method | Endpoint | Description |
|---|---|---|
| GET | `/apps` | List applications |
| POST | `/apps` | Create an application |
| GET | `/apps/<name>` | Retrieve an application |
| PUT | `/apps/<name>` | Update an application |
| DELETE | `/apps/<name>` | Delete an application |
| PUT | `/apps/<name>/container` | Link a Docker container |

### Container Management

| Method | Endpoint | Description |
|---|---|---|
| GET | `/containers` | List managed containers |
| GET | `/containers/<name>` | Inspect a managed container |
| POST | `/containers/<name>/start` | Start a container |
| POST | `/containers/<name>/stop` | Stop a container |

## Example Workflow

### Create an application

```bash
curl -X POST http://localhost:5001/apps \
  -H "Content-Type: application/json" \
  -d '{"name":"demo-app"}'
```

### Create a managed Docker container

```bash
docker run -d \
  --name tinycloud-demo \
  --label tinycloud.managed=true \
  alpine:latest sleep infinity
```

### Link the container to the application

```bash
curl -X PUT http://localhost:5001/apps/demo-app/container \
  -H "Content-Type: application/json" \
  -d '{"container_id":"tinycloud-demo"}'
```

TinyCloud validates the container and stores its full Docker container ID in PostgreSQL.

### Retrieve the application

```bash
curl http://localhost:5001/apps/demo-app
```

Example response:

```json
{
  "app": {
    "id": 1,
    "name": "demo-app",
    "status": "running",
    "docker_status": "running",
    "container_id": "<docker-container-id>"
  }
}
```

### Stop the container

```bash
curl -X POST \
  http://localhost:5001/containers/tinycloud-demo/stop
```

Retrieve the application again to observe its synchronized status.

## Status Synchronization

TinyCloud compares the stored application status with the live Docker container status.

| Docker Status | Application Status |
|---|---|
| running | running |
| exited | stopped |

If Docker reports a different supported state, TinyCloud updates the application record in PostgreSQL.

If Docker is unavailable or the linked container cannot be found, the existing application status is preserved and the API reports the Docker lookup error.

## Error Handling

| Status Code | Description |
|---|---|
| 200 | Successful request |
| 201 | Application created |
| 400 | Invalid request data |
| 403 | Container is not managed by TinyCloud |
| 404 | Application or container not found |
| 409 | Duplicate application |
| 503 | Docker service unavailable |

## Testing

TinyCloud includes 48 passing automated tests covering:

- Application CRUD operations.
- Database connectivity.
- Docker container inspection and lifecycle management.
- Managed-container permission enforcement.
- Application-to-container linking.
- PostgreSQL and Docker status synchronization.
- Invalid input handling.
- Missing containers and Docker service failures.

Run the complete test suite:

```bash
chmod +x test.sh
./test.sh
```

The test script configures the test environment, starts PostgreSQL, waits for database readiness, and executes pytest.

Integration tests use a separate `tinycloud_test` database to avoid modifying development data.

## Security

TinyCloud includes several safeguards for local development:

- Container operations restricted to explicitly managed containers.
- Database credentials loaded through environment variables.
- Environment files containing secrets excluded from Git.
- PostgreSQL port bound to localhost.
- Flask debug mode disabled by default.

TinyCloud is a local-development MVP and is not intended for production deployment without authentication, authorization, and additional infrastructure security controls.

## Future Improvements

- User authentication and role-based authorization.
- Container creation and provisioning through the API.
- Container logs and resource usage monitoring.
- Background status synchronization.
- Web-based management dashboard.
- CI/CD integration.
- Production-ready deployment configuration.

## Project Status

Core backend functionality is implemented and tested.

TinyCloud is an ongoing personal engineering project focused on backend infrastructure, cloud computing fundamentals, and container lifecycle management.


