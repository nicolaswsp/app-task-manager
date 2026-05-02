import pytest
import tempfile
import os
from typing import Optional

from app.models.task import TaskCreate, TaskStatus, TaskUpdate
from app.repositories.task_repository import TaskRepository
from app.services.priority_advisor import PriorityAdvisor
from app.services.task_service import TaskService


class MockPriorityAdvisor(PriorityAdvisor):
    """Mock advisor that always suggests PENDING."""

    def suggest_priority(self, title: str, description: Optional[str]) -> TaskStatus:
        return TaskStatus.PENDING


@pytest.fixture
def test_db_path():
    """Provide a temporary database path for tests."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name
    yield db_path
    os.unlink(db_path)


@pytest.fixture
def task_service(test_db_path):
    """Provide a TaskService instance with test dependencies."""
    repository = TaskRepository(db_path=test_db_path)
    advisor = MockPriorityAdvisor()
    return TaskService(repository, advisor)


def test_create_task(task_service):
    """Test creating a new task."""
    payload = TaskCreate(title="Test Task", description="A test task", status=TaskStatus.PENDING)
    task = task_service.create_task(payload)
    assert task.title == "Test Task"
    assert task.description == "A test task"
    assert task.status == TaskStatus.PENDING
    assert task.id is not None


def test_list_tasks_empty(task_service):
    """Test listing tasks when none exist."""
    tasks = task_service.list_tasks()
    assert tasks == []


def test_list_tasks_with_filter(task_service):
    """Test listing tasks with status filter."""
    # Create tasks with different statuses
    task1 = task_service.create_task(TaskCreate(title="Task 1", status=TaskStatus.PENDING))
    task2 = task_service.create_task(TaskCreate(title="Task 2", status=TaskStatus.COMPLETED))
    task3 = task_service.create_task(TaskCreate(title="Task 3", status=TaskStatus.IN_PROGRESS))

    # List all
    all_tasks = task_service.list_tasks()
    assert len(all_tasks) == 3

    # Filter by PENDING
    pending_tasks = task_service.list_tasks(TaskStatus.PENDING)
    assert len(pending_tasks) == 1
    assert pending_tasks[0].id == task1.id

    # Filter by COMPLETED
    completed_tasks = task_service.list_tasks(TaskStatus.COMPLETED)
    assert len(completed_tasks) == 1
    assert completed_tasks[0].id == task2.id


def test_get_task_existing(task_service):
    """Test getting an existing task by ID."""
    created = task_service.create_task(TaskCreate(title="Existing Task"))
    retrieved = task_service.get_task(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.title == "Existing Task"


def test_get_task_nonexistent(task_service):
    """Test getting a nonexistent task returns None."""
    retrieved = task_service.get_task(999)
    assert retrieved is None


def test_update_task_existing(task_service):
    """Test updating an existing task."""
    created = task_service.create_task(TaskCreate(title="Original", status=TaskStatus.PENDING))
    update_payload = TaskUpdate(title="Updated", status=TaskStatus.COMPLETED)
    updated = task_service.update_task(created.id, update_payload)
    assert updated is not None
    assert updated.id == created.id
    assert updated.title == "Updated"
    assert updated.status == TaskStatus.COMPLETED


def test_update_task_nonexistent(task_service):
    """Test updating a nonexistent task returns None."""
    update_payload = TaskUpdate(title="Updated")
    updated = task_service.update_task(999, update_payload)
    assert updated is None


def test_delete_task_existing(task_service):
    """Test deleting an existing task."""
    created = task_service.create_task(TaskCreate(title="To Delete"))
    deleted = task_service.delete_task(created.id)
    assert deleted is True
    # Verify it's gone
    retrieved = task_service.get_task(created.id)
    assert retrieved is None


def test_delete_task_nonexistent(task_service):
    """Test deleting a nonexistent task returns False."""
    deleted = task_service.delete_task(999)
    assert deleted is False