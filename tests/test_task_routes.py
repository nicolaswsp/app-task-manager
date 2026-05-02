import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.task_routes import get_task_service, router
from app.models.task import TaskCreate, TaskStatus, TaskUpdate
from app.repositories.task_repository import TaskRepository
from app.services.priority_advisor import PriorityAdvisor
from app.services.task_service import TaskService


class MockPriorityAdvisor(PriorityAdvisor):
    """Mock advisor that always suggests PENDING."""

    def suggest_priority(self, title: str, description: str | None) -> TaskStatus:
        return TaskStatus.PENDING


@pytest.fixture
def test_db_path():
    """Provide a temporary database path for tests."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name
    yield db_path
    os.unlink(db_path)


@pytest.fixture
def test_service(test_db_path):
    """Provide a TaskService instance for testing."""
    repository = TaskRepository(db_path=test_db_path)
    advisor = MockPriorityAdvisor()
    return TaskService(repository, advisor)


@pytest.fixture
def client(test_service):
    """Provide a TestClient with overridden dependencies."""
    app = FastAPI()
    app.include_router(router)

    def override_get_task_service():
        return test_service

    app.dependency_overrides[get_task_service] = override_get_task_service
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_task(client):
    """Test POST /tasks creates a task with 201."""
    payload = {"title": "Test Task", "description": "A test", "status": "pending"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data


def test_list_tasks(client):
    """Test GET /tasks returns list with 200."""
    # Create a task first
    client.post("/tasks", json={"title": "Task 1", "status": "pending"})
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_task_existing(client):
    """Test GET /tasks/{id} returns task with 200."""
    create_response = client.post("/tasks", json={"title": "Existing", "status": "pending"})
    task_id = create_response.json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id


def test_get_task_not_found(client):
    """Test GET /tasks/{id} for nonexistent task returns 404."""
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task_existing(client):
    """Test PUT /tasks/{id} updates task with 200."""
    create_response = client.post("/tasks", json={"title": "Original", "status": "pending"})
    task_id = create_response.json()["id"]
    update_payload = {"title": "Updated", "status": "completed"}
    response = client.put(f"/tasks/{task_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["status"] == "completed"


def test_update_task_not_found(client):
    """Test PUT /tasks/{id} for nonexistent task returns 404."""
    update_payload = {"title": "Updated"}
    response = client.put("/tasks/999", json=update_payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_task_existing(client):
    """Test DELETE /tasks/{id} deletes task with 204."""
    create_response = client.post("/tasks", json={"title": "To Delete", "status": "pending"})
    task_id = create_response.json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    # Verify it's gone
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_not_found(client):
    """Test DELETE /tasks/{id} for nonexistent task returns 404."""
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
