"""Task Add Agent for creating new todo tasks.

Handles task creation with validation, generates user-friendly confirmation messages.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models.task import Task
from src.services.task_repository import TaskRepository


class TaskAddAgent:
    """
    Agent responsible for adding new tasks to the repository.

    Validates task data, creates tasks in the database, and generates
    user-friendly confirmation messages.
    """

    def __init__(self, repository: TaskRepository):
        """
        Initialize Task Add Agent.

        Args:
            repository: TaskRepository instance for persistence
        """
        self.repository = repository

    def add_task(
        self,
        description: str,
        due_date: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a new task to the repository.

        Args:
            description: Task description (required, 1-500 chars)
            due_date: Optional due date in ISO 8601 format
            priority: Optional priority (low, medium, high)
            tags: Optional list of tags

        Returns:
            Dict with success, task, error, and user_message fields
        """
        # Validate description
        if not description or len(description.strip()) == 0:
            return {
                "success": False,
                "task": None,
                "error": "Description cannot be empty",
                "user_message": "I couldn't add the task. What task would you like to add?"
            }

        if len(description) > 500:
            return {
                "success": False,
                "task": None,
                "error": "Description cannot exceed 500 characters",
                "user_message": f"That description is too long ({len(description)} characters). Please keep it under 500 characters."
            }

        # Parse due_date
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date)
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "task": None,
                    "error": f"Invalid date format: {due_date}",
                    "user_message": "I couldn't understand that date. Please use a format like 'tomorrow' or 'December 15'."
                }

        # Validate priority
        if priority and priority not in ['low', 'medium', 'high']:
            return {
                "success": False,
                "task": None,
                "error": f"Invalid priority: {priority}",
                "user_message": "Priority must be low, medium, or high."
            }

        # Create task object
        task = Task(
            id=None,  # Will be auto-generated
            description=description.strip(),
            due_date=parsed_due_date,
            priority=priority,
            status='pending',
            tags=tags or []
        )

        # Validate task
        is_valid, error_msg = task.validate()
        if not is_valid:
            return {
                "success": False,
                "task": None,
                "error": error_msg,
                "user_message": f"I couldn't add the task: {error_msg}"
            }

        # Create task in repository
        try:
            created_task = self.repository.create(task)

            # Generate user-friendly message
            user_message = self._format_confirmation(created_task)

            return {
                "success": True,
                "task": created_task.to_dict(),
                "error": None,
                "user_message": user_message
            }

        except Exception as e:
            return {
                "success": False,
                "task": None,
                "error": str(e),
                "user_message": f"Sorry, I couldn't add the task due to an error: {str(e)}"
            }

    def _format_confirmation(self, task: Task) -> str:
        """
        Format user-friendly confirmation message.

        Args:
            task: Created task object

        Returns:
            Confirmation message string
        """
        message = f"✓ Task added: {task.description}"

        # Add due date if present
        if task.due_date:
            due_str = task.due_date.strftime("%B %d at %I:%M %p")
            message += f" (due {due_str}"

            # Add priority if present
            if task.priority:
                message += f", priority: {task.priority}"

            message += ")"
        elif task.priority:
            # Priority without due date
            message += f" (priority: {task.priority})"

        # Add tags if present
        if task.tags:
            tags_str = ", ".join(task.tags)
            message += f" [tags: {tags_str}]"

        message += f" (ID: {task.id})"

        return message

    def validate_input(
        self,
        description: str,
        due_date: Optional[str] = None,
        priority: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate task input parameters before creation.

        Args:
            description: Task description
            due_date: Optional due date string
            priority: Optional priority string

        Returns:
            (is_valid, error_message): Validation result and error message
        """
        # Check description
        if not description or len(description.strip()) == 0:
            return False, "Description cannot be empty"

        if len(description) > 500:
            return False, "Description cannot exceed 500 characters"

        # Check due_date format
        if due_date:
            try:
                datetime.fromisoformat(due_date)
            except (ValueError, TypeError):
                return False, f"Invalid date format: {due_date}"

        # Check priority
        if priority and priority not in ['low', 'medium', 'high']:
            return False, f"Priority must be low, medium, or high (got: {priority})"

        return True, None
