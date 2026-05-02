from __future__ import annotations

from typing import List, Optional, Protocol

from app.models.task import TaskCreate, TaskOut, TaskStatus, TaskUpdate
from app.repositories.task_repository import TaskRepository, TaskRow


class TaskService:
    """Business layer for task operations and priority advice."""

    def __init__(self, repository: TaskRepository, priority_advisor: PriorityAdvisor) -> None:
        self._repository = repository
        self._priority_advisor = priority_advisor

    def _to_out(self, row: TaskRow) -> TaskOut:
        return TaskOut(**row)

    def create_task(self, payload: TaskCreate) -> TaskOut:
        status = payload.status
        if status == TaskStatus.PENDING:
            status = self._priority_advisor.suggest_priority(payload.title, payload.description)

        row = self._repository.create(
            title=payload.title,
            description=payload.description,
            status=status.value,
        )
        return self._to_out(row)

    def list_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[TaskOut]:
        rows = self._repository.list()
        if status_filter:
            rows = [row for row in rows if row["status"] == status_filter.value]
        return [self._to_out(row) for row in rows]

    def get_task(self, task_id: int) -> Optional[TaskOut]:
        row = self._repository.get_by_id(task_id)
        return self._to_out(row) if row else None

    def update_task(self, task_id: int, payload: TaskUpdate) -> Optional[TaskOut]:
        status = payload.status.value if payload.status else None
        row = self._repository.update(
            task_id=task_id,
            title=payload.title,
            description=payload.description,
            status=status,
        )
        return self._to_out(row) if row else None

    def delete_task(self, task_id: int) -> bool:
        return self._repository.delete(task_id)