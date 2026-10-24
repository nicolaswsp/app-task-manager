import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.task_routes import get_task_service, router
from app.repositories.task_repository import TaskRepository
from app.services.priority_advisor import PriorityAdvisor
from app.services.task_service import TaskService


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Provide a client backed by an isolated SQLite database and local advisor."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    repository = TaskRepository(db_path=str(tmp_path / "integration.db"))
    service = TaskService(repository, PriorityAdvisor())
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_task_service] = lambda: service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_task_suggests_status_and_persists_for_filtered_list(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Corrigir bug urgente",
            "description": "Falha crítica no login",
            "status": "pending",
        },
    )

    assert response.status_code == 201
    created_task = response.json()
    assert created_task["status"] == "in_progress"

    get_response = client.get(f"/tasks/{created_task['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == created_task

    list_response = client.get("/tasks", params={"status_filter": "in_progress"})
    assert list_response.status_code == 200
    assert [task["id"] for task in list_response.json()] == [created_task["id"]]


def test_update_and_delete_task_are_reflected_across_api_and_database(client):
    created_response = client.post(
        "/tasks",
        json={"title": "Preparar relatório", "status": "completed"},
    )
    task_id = created_response.json()["id"]

    update_response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Revisar relatório", "status": "in_progress"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Revisar relatório"
    assert update_response.json()["status"] == "in_progress"

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json() == update_response.json()

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404
    assert client.get("/tasks").json() == []


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "", "status": "pending"},
        {"title": "Tarefa válida", "status": "unknown"},
    ],
)
def test_invalid_task_payload_is_rejected_without_persisting(client, payload):
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    assert client.get("/tasks").json() == []
