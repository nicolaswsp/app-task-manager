from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import List, Optional, TypedDict


class TaskRow(TypedDict):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


class TaskRepository:
    """SQLite-backed repository for task persistence."""

    def __init__(self, db_path: str = "tasks.db") -> None:
        self._db_path = db_path
        self._ensure_table()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _row_to_task(self, row: sqlite3.Row) -> TaskRow:
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "created_at": datetime.fromisoformat(row["created_at"]),
            "updated_at": datetime.fromisoformat(row["updated_at"]),
        }

    def create(
        self,
        title: str,
        description: Optional[str],
        status: str,
    ) -> TaskRow:
        created_at = updated_at = self._now()
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks (title, description, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, description, status, created_at, updated_at),
            )
            task_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        assert row is not None
        return self._row_to_task(row)

    def list(self) -> List[TaskRow]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM tasks ORDER BY id")
            return [self._row_to_task(row) for row in cursor.fetchall()]

    def get_by_id(self, task_id: int) -> Optional[TaskRow]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._row_to_task(row) if row else None

    def update(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[TaskRow]:
        updates: List[str] = []
        params: List[object] = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if not updates:
            return self.get_by_id(task_id)

        updates.append("updated_at = ?")
        params.append(self._now())
        params.append(task_id)
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"

        with self._get_connection() as conn:
            conn.execute(query, tuple(params))

        return self.get_by_id(task_id)

    def delete(self, task_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0