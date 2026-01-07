"""MCP Server for Task Resource Management.

Exposes TaskRepository via Model Context Protocol (MCP) resources
for inter-agent communication and persistence.
"""

import json
from typing import Optional
from mcp.server import Server
from mcp.types import Resource, TextContent

from src.services.task_repository import TaskRepository


class TaskMCPServer:
    """
    MCP Server wrapper for TaskRepository.

    Exposes task persistence via MCP resources:
    - task://list - List all tasks with optional filters
    - task://get/{id} - Get a specific task by ID
    - task://schema - Get the database schema
    """

    def __init__(self, server: Server, repository: Optional[TaskRepository] = None):
        """
        Initialize MCP server with task repository.

        Args:
            server: FastMCP server instance
            repository: TaskRepository instance (creates default if None)
        """
        self.server = server
        self.repository = repository or TaskRepository()
        self._register_resources()

    def _register_resources(self):
        """Register MCP resource handlers."""

        @self.server.list_resources()
        async def list_resources():
            """List available task resources."""
            return [
                Resource(
                    uri="task://list",
                    name="Task List",
                    description="List all tasks with optional filtering by status and priority",
                    mimeType="application/json"
                ),
                Resource(
                    uri="task://get",
                    name="Get Task",
                    description="Retrieve a specific task by ID (use task://get/{id})",
                    mimeType="application/json"
                ),
                Resource(
                    uri="task://schema",
                    name="Task Schema",
                    description="Get the task database schema definition",
                    mimeType="application/json"
                )
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """
            Read resource handler for task resources.

            Args:
                uri: Resource URI (task://list, task://get/{id}, task://schema)

            Returns:
                JSON string with resource content

            Raises:
                ValueError: If URI is invalid or resource not found
            """
            if uri == "task://list":
                return await self._handle_list_resource()

            elif uri.startswith("task://get/"):
                task_id = uri.split("/")[-1]
                try:
                    task_id_int = int(task_id)
                    return await self._handle_get_resource(task_id_int)
                except ValueError:
                    raise ValueError(f"Invalid task ID: {task_id}")

            elif uri == "task://schema":
                return await self._handle_schema_resource()

            else:
                raise ValueError(f"Unknown resource URI: {uri}")

    async def _handle_list_resource(self) -> str:
        """
        Handle task://list resource request.

        Returns:
            JSON string with array of tasks
        """
        tasks = self.repository.get_all()
        tasks_data = [task.to_dict() for task in tasks]
        return json.dumps({
            "tasks": tasks_data,
            "count": len(tasks_data),
            "uri": "task://list"
        }, indent=2)

    async def _handle_get_resource(self, task_id: int) -> str:
        """
        Handle task://get/{id} resource request.

        Args:
            task_id: Task ID to retrieve

        Returns:
            JSON string with task data

        Raises:
            ValueError: If task not found
        """
        task = self.repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        return json.dumps({
            "task": task.to_dict(),
            "uri": f"task://get/{task_id}"
        }, indent=2)

    async def _handle_schema_resource(self) -> str:
        """
        Handle task://schema resource request.

        Returns:
            JSON string with database schema
        """
        schema = {
            "table_name": "tasks",
            "columns": [
                {
                    "name": "id",
                    "type": "INTEGER",
                    "nullable": False,
                    "primary_key": True,
                    "auto_increment": True
                },
                {
                    "name": "description",
                    "type": "TEXT",
                    "nullable": False
                },
                {
                    "name": "due_date",
                    "type": "TEXT",
                    "nullable": True
                },
                {
                    "name": "priority",
                    "type": "TEXT",
                    "nullable": True,
                    "check": "priority IN ('low', 'medium', 'high')"
                },
                {
                    "name": "status",
                    "type": "TEXT",
                    "nullable": False,
                    "default": "'pending'",
                    "check": "status IN ('pending', 'in-progress', 'completed')"
                },
                {
                    "name": "tags",
                    "type": "TEXT",
                    "nullable": True,
                    "description": "JSON array of tag strings"
                },
                {
                    "name": "created_at",
                    "type": "TEXT",
                    "nullable": False,
                    "default": "datetime('now')"
                },
                {
                    "name": "updated_at",
                    "type": "TEXT",
                    "nullable": False,
                    "default": "datetime('now')"
                }
            ],
            "indexes": [
                {"name": "idx_tasks_status", "columns": ["status"]},
                {"name": "idx_tasks_due_date", "columns": ["due_date"]},
                {"name": "idx_tasks_priority", "columns": ["priority"]}
            ],
            "triggers": [
                {
                    "name": "update_task_timestamp",
                    "event": "AFTER UPDATE",
                    "action": "UPDATE tasks SET updated_at = datetime('now')"
                }
            ]
        }

        return json.dumps({
            "schema": schema,
            "uri": "task://schema"
        }, indent=2)


def create_task_mcp_server(server: Server, db_path: str = 'data/tasks.db') -> TaskMCPServer:
    """
    Factory function to create TaskMCPServer instance.

    Args:
        server: FastMCP server instance
        db_path: Path to SQLite database file

    Returns:
        Initialized TaskMCPServer
    """
    repository = TaskRepository(db_path)
    return TaskMCPServer(server, repository)
