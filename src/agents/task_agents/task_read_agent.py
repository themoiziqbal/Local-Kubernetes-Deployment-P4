"""Task Read Agent for retrieving and displaying tasks.

Handles task queries with filtering, searching, and formatting.
"""

from typing import Any, Dict, List, Optional

from src.models.task import Task
from src.services.task_repository import TaskRepository


class TaskReadAgent:
    """
    Agent responsible for reading and displaying tasks.

    Supports filtering by status/priority, searching by keywords,
    and formatting task lists for user display.
    """

    def __init__(self, repository: TaskRepository):
        """
        Initialize Task Read Agent.

        Args:
            repository: TaskRepository instance for data access
        """
        self.repository = repository

    def get_task(self, task_id: int) -> Dict[str, Any]:
        """
        Get a single task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Dict with success, task, and user_message fields
        """
        try:
            task = self.repository.get_by_id(task_id)

            if not task:
                return {
                    "success": False,
                    "task": None,
                    "user_message": f"I couldn't find task #{task_id}."
                }

            return {
                "success": True,
                "task": task.to_dict(),
                "user_message": self._format_task_detail(task)
            }

        except Exception as e:
            return {
                "success": False,
                "task": None,
                "user_message": f"Error retrieving task: {str(e)}"
            }

    def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all tasks with optional filters.

        Args:
            status: Optional status filter (pending, in-progress, completed)
            priority: Optional priority filter (low, medium, high)

        Returns:
            Dict with success, tasks, count, and user_message fields
        """
        try:
            tasks = self.repository.get_all(status=status, priority=priority)

            if not tasks:
                filter_desc = self._build_filter_description(status, priority)
                return {
                    "success": True,
                    "tasks": [],
                    "count": 0,
                    "user_message": f"You have no {filter_desc}tasks."
                }

            return {
                "success": True,
                "tasks": [task.to_dict() for task in tasks],
                "count": len(tasks),
                "user_message": self._format_task_list(tasks, status, priority)
            }

        except Exception as e:
            return {
                "success": False,
                "tasks": [],
                "count": 0,
                "user_message": f"Error listing tasks: {str(e)}"
            }

    def search_tasks(self, keyword: str) -> Dict[str, Any]:
        """
        Search tasks by keyword in description or tags.

        Args:
            keyword: Search keyword

        Returns:
            Dict with success, tasks, count, and user_message fields
        """
        try:
            tasks = self.repository.search(keyword)

            if not tasks:
                return {
                    "success": True,
                    "tasks": [],
                    "count": 0,
                    "user_message": f"No tasks found matching '{keyword}'."
                }

            return {
                "success": True,
                "tasks": [task.to_dict() for task in tasks],
                "count": len(tasks),
                "user_message": self._format_search_results(tasks, keyword)
            }

        except Exception as e:
            return {
                "success": False,
                "tasks": [],
                "count": 0,
                "user_message": f"Error searching tasks: {str(e)}"
            }

    def _format_task_detail(self, task: Task) -> str:
        """
        Format detailed view of a single task.

        Args:
            task: Task object to format

        Returns:
            Formatted task detail string
        """
        lines = [
            f"Task #{task.id}: {task.description}",
            f"  Status: {task.status}"
        ]

        if task.priority:
            lines.append(f"  Priority: {task.priority}")

        if task.due_date:
            due_str = task.due_date.strftime("%B %d, %Y at %I:%M %p")
            lines.append(f"  Due: {due_str}")

        if task.tags:
            tags_str = ", ".join(task.tags)
            lines.append(f"  Tags: {tags_str}")

        created_str = task.created_at.strftime("%B %d, %Y")
        lines.append(f"  Created: {created_str}")

        return "\n".join(lines)

    def _format_task_list(
        self,
        tasks: List[Task],
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> str:
        """
        Format list of tasks for display.

        Args:
            tasks: List of tasks to format
            status: Optional status filter applied
            priority: Optional priority filter applied

        Returns:
            Formatted task list string
        """
        filter_desc = self._build_filter_description(status, priority)
        header = f"You have {len(tasks)} {filter_desc}task{'s' if len(tasks) != 1 else ''}:\n"

        task_lines = []
        for task in tasks:
            # Format: [ID] Description (priority) [status]
            line = f"  [{task.id}] {task.description}"

            if task.priority:
                line += f" (priority: {task.priority})"

            if task.due_date:
                due_str = task.due_date.strftime("%b %d")
                line += f" [due: {due_str}]"

            line += f" - {task.status}"

            task_lines.append(line)

        return header + "\n".join(task_lines)

    def _format_search_results(self, tasks: List[Task], keyword: str) -> str:
        """
        Format search results for display.

        Args:
            tasks: List of matching tasks
            keyword: Search keyword used

        Returns:
            Formatted search results string
        """
        header = f"Found {len(tasks)} task{'s' if len(tasks) != 1 else ''} matching '{keyword}':\n"

        task_lines = []
        for task in tasks:
            line = f"  [{task.id}] {task.description}"
            if task.priority:
                line += f" (priority: {task.priority})"
            line += f" - {task.status}"
            task_lines.append(line)

        return header + "\n".join(task_lines)

    def _build_filter_description(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> str:
        """
        Build description of active filters.

        Args:
            status: Optional status filter
            priority: Optional priority filter

        Returns:
            Filter description string (e.g., "high priority pending ")
        """
        parts = []

        if priority:
            parts.append(f"{priority} priority")

        if status:
            parts.append(status)

        if parts:
            return " ".join(parts) + " "
        return ""
