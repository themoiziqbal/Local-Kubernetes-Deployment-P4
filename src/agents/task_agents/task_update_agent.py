"""Task Update Agent for full task replacement.

Handles complete task updates (replaces all fields).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models.task import Task
from src.services.task_repository import TaskRepository


class TaskUpdateAgent:
    """
    Agent responsible for full task updates.

    Replaces all task fields with new values.
    """

    def __init__(self, repository: TaskRepository):
        """
        Initialize Task Update Agent.

        Args:
            repository: TaskRepository instance for persistence
        """
        self.repository = repository

    def update_task(
        self,
        task_id: int,
        description: str,
        due_date: Optional[str] = None,
        priority: Optional[str] = None,
        status: str = 'pending',
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update task with new values (full replacement).

        Args:
            task_id: Task ID to update
            description: New description
            due_date: New due date (ISO 8601)
            priority: New priority (low, medium, high)
            status: New status (pending, in-progress, completed)
            tags: New tags list

        Returns:
            Dict with success, task, and user_message fields
        """
        # Check if task exists
        existing_task = self.repository.get_by_id(task_id)
        if not existing_task:
            return {
                "success": False,
                "task": None,
                "user_message": f"I couldn't find task #{task_id} to update."
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
                    "user_message": f"Invalid date format: {due_date}"
                }

        # Create updated task object
        updated_task = Task(
            id=task_id,
            description=description.strip(),
            due_date=parsed_due_date,
            priority=priority,
            status=status,
            tags=tags or [],
            created_at=existing_task.created_at,
            updated_at=datetime.now()
        )

        # Validate
        is_valid, error_msg = updated_task.validate()
        if not is_valid:
            return {
                "success": False,
                "task": None,
                "user_message": f"Invalid task data: {error_msg}"
            }

        # Update in repository
        try:
            result = self.repository.update(updated_task)

            return {
                "success": True,
                "task": result.to_dict(),
                "user_message": f"✓ Task #{task_id} updated: {result.description}"
            }

        except Exception as e:
            return {
                "success": False,
                "task": None,
                "user_message": f"Error updating task: {str(e)}"
            }

    def patch_task(
        self,
        task_id: int,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Partially update task (only specified fields).

        Args:
            task_id: Task ID to update
            description: Optional new description
            due_date: Optional new due date (ISO 8601)
            priority: Optional new priority (low, medium, high)
            status: Optional new status (pending, in-progress, completed)
            tags: Optional new tags list

        Returns:
            Dict with success, task, and user_message fields
        """
        # Check if task exists
        existing_task = self.repository.get_by_id(task_id)
        if not existing_task:
            return {
                "success": False,
                "task": None,
                "user_message": f"I couldn't find task #{task_id} to update."
            }

        # Track which fields are being updated
        updated_fields = []

        # Use existing values for unspecified fields
        new_description = description if description is not None else existing_task.description
        new_priority = priority if priority is not None else existing_task.priority
        new_status = status if status is not None else existing_task.status
        new_tags = tags if tags is not None else existing_task.tags

        # Parse due_date if provided
        if due_date is not None:
            try:
                new_due_date = datetime.fromisoformat(due_date)
                updated_fields.append("due date")
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "task": None,
                    "user_message": f"Invalid date format: {due_date}"
                }
        else:
            new_due_date = existing_task.due_date

        # Track which fields changed
        if description is not None:
            updated_fields.append("description")
        if priority is not None:
            updated_fields.append("priority")
        if status is not None:
            updated_fields.append("status")
        if tags is not None:
            updated_fields.append("tags")

        # Create updated task object
        updated_task = Task(
            id=task_id,
            description=new_description.strip() if isinstance(new_description, str) else new_description,
            due_date=new_due_date,
            priority=new_priority,
            status=new_status,
            tags=new_tags or [],
            created_at=existing_task.created_at,
            updated_at=datetime.now()
        )

        # Validate
        is_valid, error_msg = updated_task.validate()
        if not is_valid:
            return {
                "success": False,
                "task": None,
                "user_message": f"Invalid task data: {error_msg}"
            }

        # Update in repository
        try:
            result = self.repository.update(updated_task)

            # Generate message about what was updated
            if updated_fields:
                fields_str = ", ".join(updated_fields)
                message = f"✓ Task #{task_id} updated ({fields_str}): {result.description}"
            else:
                message = f"✓ Task #{task_id} (no changes made)"

            return {
                "success": True,
                "task": result.to_dict(),
                "user_message": message
            }

        except Exception as e:
            return {
                "success": False,
                "task": None,
                "user_message": f"Error updating task: {str(e)}"
            }
