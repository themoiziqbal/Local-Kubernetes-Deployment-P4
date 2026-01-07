"""Task repository service with SQLite database integration."""

import json
import os
import sqlite3
from datetime import datetime
from typing import List, Optional

from src.models.task import Task


class TaskRepository:
    """
    Repository for task persistence using SQLite database.

    Provides CRUD operations for tasks and exposes MCP resource interface
    for inter-agent communication.
    """

    def __init__(self, db_path: str = 'data/tasks.db'):
        """
        Initialize TaskRepository with SQLite database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Create database directory and initialize schema if not exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                due_date TEXT,
                priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
                status TEXT CHECK(status IN ('pending', 'in-progress', 'completed')) DEFAULT 'pending',
                tags TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        ''')

        # Create indexes for common queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)')

        # Create trigger to auto-update updated_at timestamp
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_task_timestamp
            AFTER UPDATE ON tasks
            FOR EACH ROW
            BEGIN
                UPDATE tasks SET updated_at = datetime('now') WHERE id = OLD.id;
            END
        ''')

        # Enable WAL mode for concurrent access
        cursor.execute('PRAGMA journal_mode=WAL')

        conn.commit()
        conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    def create(self, task: Task) -> Task:
        """
        Create a new task in the database.

        Args:
            task: Task object to create

        Returns:
            Created task with auto-generated ID

        Raises:
            ValueError: If task validation fails
        """
        is_valid, error_msg = task.validate()
        if not is_valid:
            raise ValueError(error_msg)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO tasks (description, due_date, priority, status, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.description,
            task.due_date.isoformat() if task.due_date else None,
            task.priority,
            task.status,
            json.dumps(task.tags),
            task.created_at.isoformat(),
            task.updated_at.isoformat()
        ))

        task.id = cursor.lastrowid
        conn.commit()
        conn.close()

        return task

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task object if found, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Task.from_dict(dict(row))
        return None

    def get_all(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[Task]:
        """
        Retrieve all tasks with optional filters.

        Args:
            status: Optional status filter (pending, in-progress, completed)
            priority: Optional priority filter (low, medium, high)

        Returns:
            List of Task objects
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        if priority:
            query += ' AND priority = ?'
            params.append(priority)

        query += ' ORDER BY created_at DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [Task.from_dict(dict(row)) for row in rows]

    def update(self, task: Task) -> Task:
        """
        Update an existing task (full replacement).

        Args:
            task: Task object with updated values

        Returns:
            Updated task

        Raises:
            ValueError: If task validation fails or task not found
        """
        is_valid, error_msg = task.validate()
        if not is_valid:
            raise ValueError(error_msg)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE tasks
            SET description = ?, due_date = ?, priority = ?, status = ?, tags = ?
            WHERE id = ?
        ''', (
            task.description,
            task.due_date.isoformat() if task.due_date else None,
            task.priority,
            task.status,
            json.dumps(task.tags),
            task.id
        ))

        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Task with ID {task.id} not found")

        conn.commit()
        conn.close()

        # Refresh task to get updated timestamp
        return self.get_by_id(task.id)

    def patch(self, task_id: int, **fields) -> Task:
        """
        Partially update task fields.

        Args:
            task_id: Task ID to update
            **fields: Fields to update (description, due_date, priority, status, tags)

        Returns:
            Updated task

        Raises:
            ValueError: If task not found or invalid field values
        """
        task = self.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Update only provided fields
        if 'description' in fields:
            task.description = fields['description']
        if 'due_date' in fields:
            task.due_date = fields['due_date']
        if 'priority' in fields:
            task.priority = fields['priority']
        if 'status' in fields:
            task.status = fields['status']
        if 'tags' in fields:
            task.tags = fields['tags']

        # Validate and update
        return self.update(task)

    def delete(self, task_id: int) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: Task ID to delete

        Returns:
            True if task was deleted, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted

    def search(self, keyword: str) -> List[Task]:
        """
        Search tasks by keyword in description or tags.

        Args:
            keyword: Search keyword

        Returns:
            List of matching tasks
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM tasks
            WHERE description LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{keyword}%', f'%{keyword}%'))

        rows = cursor.fetchall()
        conn.close()

        return [Task.from_dict(dict(row)) for row in rows]

    def get_count(self) -> int:
        """Get total number of tasks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tasks')
        count = cursor.fetchone()[0]
        conn.close()
        return count
