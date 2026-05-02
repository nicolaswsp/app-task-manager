from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status

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


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskOut)
def create_task(payload: TaskCreate, service: TaskServiceDep) -> TaskOut:
    """Create a new task with optional priority suggestion."""
    return service.create_task(payload)


@router.get("", response_model=list[TaskOut])
def list_tasks(
    service: TaskServiceDep,
    status_filter: Optional[TaskStatus] = None,
) -> list[TaskOut]:
    """List all tasks with optional status filter."""
    return service.list_tasks(status_filter)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, service: TaskServiceDep) -> TaskOut:
    """Get a specific task by ID."""
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: TaskServiceDep,
) -> TaskOut:
    """Update a specific task by ID."""
    task = service.update_task(task_id, payload)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, service: TaskServiceDep) -> None:
    """Delete a specific task by ID."""
    if not service.delete_task(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
