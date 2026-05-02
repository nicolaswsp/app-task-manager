from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.models.task import TaskCreate, TaskOut, TaskStatus, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service() -> TaskService:
    """Dependency to inject TaskService instance."""
    from app.repositories.task_repository import TaskRepository
    from app.services.priority_advisor import PriorityAdvisor

    repository = TaskRepository()
    advisor = PriorityAdvisor()
    return TaskService(repository, advisor)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskOut)
def create_task(payload: TaskCreate, service: TaskService = None) -> TaskOut:
    """Create a new task with optional priority suggestion."""
    if service is None:
        service = get_task_service()
    return service.create_task(payload)


@router.get("", response_model=list[TaskOut])
def list_tasks(
    status_filter: Optional[TaskStatus] = None,
    service: TaskService = None,
) -> list[TaskOut]:
    """List all tasks with optional status filter."""
    if service is None:
        service = get_task_service()
    return service.list_tasks(status_filter)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, service: TaskService = None) -> TaskOut:
    """Get a specific task by ID."""
    if service is None:
        service = get_task_service()
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: TaskService = None,
) -> TaskOut:
    """Update a specific task by ID."""
    if service is None:
        service = get_task_service()
    task = service.update_task(task_id, payload)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, service: TaskService = None) -> None:
    """Delete a specific task by ID."""
    if service is None:
        service = get_task_service()
    if not service.delete_task(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")