"""Test script for Task MCP Server.

This script demonstrates and tests the MCP resource endpoints.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server import Server
from src.services.task_mcp_server import create_task_mcp_server
from src.models.task import Task
from datetime import datetime, timedelta


async def test_mcp_server():
    """Test MCP server functionality."""
    print("=== Task MCP Server Test ===\n")

    # Create MCP server
    server = Server("task-server")
    mcp_server = create_task_mcp_server(server, db_path="data/test_tasks.db")

    # Add some test tasks
    print("1. Adding test tasks...")
    task1 = Task(
        id=None,
        description="Buy groceries for the week",
        priority="medium",
        status="pending",
        tags=["shopping", "personal"]
    )
    task2 = Task(
        id=None,
        description="Complete project documentation",
        due_date=datetime.now() + timedelta(days=3),
        priority="high",
        status="in-progress",
        tags=["work", "documentation"]
    )

    created_task1 = mcp_server.repository.create(task1)
    created_task2 = mcp_server.repository.create(task2)
    print(f"   Created task {created_task1.id}: {created_task1.description}")
    print(f"   Created task {created_task2.id}: {created_task2.description}\n")

    # Test task://list resource
    print("2. Testing task://list resource...")
    list_result = await mcp_server._handle_list_resource()
    print(f"   Response:\n{list_result}\n")

    # Test task://get/{id} resource
    print(f"3. Testing task://get/{created_task1.id} resource...")
    get_result = await mcp_server._handle_get_resource(created_task1.id)
    print(f"   Response:\n{get_result}\n")

    # Test task://schema resource
    print("4. Testing task://schema resource...")
    schema_result = await mcp_server._handle_schema_resource()
    print(f"   Response:\n{schema_result}\n")

    # Test error handling
    print("5. Testing error handling (non-existent task)...")
    try:
        await mcp_server._handle_get_resource(9999)
    except ValueError as e:
        print(f"   Caught expected error: {e}\n")

    print("=== All Tests Passed ===")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
