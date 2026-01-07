"""Task Delete Agent for removing tasks.

Handles task deletion with confirmation workflow.
"""

from typing import Any, Dict

from src.services.task_repository import TaskRepository


class TaskDeleteAgent:
    """
    Agent responsible for deleting tasks.

    Provides confirmation workflow and handles task removal.
    """

    def __init__(self, repository: TaskRepository):
        """
        Initialize Task Delete Agent.

        Args:
            repository: TaskRepository instance for persistence
        """
        self.repository = repository
        self.pending_deletions = {}  # Maps user_id -> task_id for confirmation

    def delete_task(
        self,
        task_id: int,
        confirmed: bool = False,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Delete a task (with optional confirmation workflow).

        Args:
            task_id: Task ID to delete
            confirmed: Whether deletion is confirmed
            user_id: User identifier for confirmation tracking

        Returns:
            Dict with success, needs_confirmation, task_description, and user_message fields
        """
        # Check if task exists
        task = self.repository.get_by_id(task_id)
        if not task:
            return {
                "success": False,
                "needs_confirmation": False,
                "task_description": None,
                "user_message": f"I couldn't find task #{task_id} to delete."
            }

        # If not confirmed, ask for confirmation
        if not confirmed:
            self.pending_deletions[user_id] = task_id
            return {
                "success": False,
                "needs_confirmation": True,
                "task_description": task.description,
                "user_message": f"Are you sure you want to delete task #{task_id}: '{task.description}'? (yes/no)"
            }

        # Perform deletion
        try:
            deleted = self.repository.delete(task_id)

            if deleted:
                # Clear pending confirmation
                self.pending_deletions.pop(user_id, None)

                return {
                    "success": True,
                    "needs_confirmation": False,
                    "task_description": task.description,
                    "user_message": f"✓ Task #{task_id} deleted: {task.description}"
                }
            else:
                return {
                    "success": False,
                    "needs_confirmation": False,
                    "task_description": None,
                    "user_message": f"Failed to delete task #{task_id}."
                }

        except Exception as e:
            return {
                "success": False,
                "needs_confirmation": False,
                "task_description": None,
                "user_message": f"Error deleting task: {str(e)}"
            }

    def confirm_deletion(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Confirm pending deletion for user.

        Args:
            user_id: User identifier

        Returns:
            Result of delete_task with confirmed=True
        """
        task_id = self.pending_deletions.get(user_id)
        if not task_id:
            return {
                "success": False,
                "needs_confirmation": False,
                "task_description": None,
                "user_message": "No pending deletion to confirm."
            }

        return self.delete_task(task_id, confirmed=True, user_id=user_id)

    def cancel_deletion(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Cancel pending deletion for user.

        Args:
            user_id: User identifier

        Returns:
            Cancellation result
        """
        task_id = self.pending_deletions.pop(user_id, None)
        if task_id:
            return {
                "success": True,
                "needs_confirmation": False,
                "task_description": None,
                "user_message": f"Deletion of task #{task_id} cancelled."
            }
        else:
            return {
                "success": False,
                "needs_confirmation": False,
                "task_description": None,
                "user_message": "No pending deletion to cancel."
            }
