"""
Integration tests for the Web API (api/index.py)

Tests the /api/chat and /api/todos endpoints with various scenarios.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.index import app, task_repo

client = TestClient(app)


class TestTodosEndpoint:
    """Tests for the /api/todos endpoint"""

    def test_get_todos_returns_list(self):
        """Test that /api/todos returns a list of tasks"""
        response = client.get("/api/todos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_todos_have_correct_structure(self):
        """Test that each todo has the correct structure"""
        response = client.get("/api/todos")
        data = response.json()

        if len(data) > 0:
            todo = data[0]
            assert "id" in todo
            assert "title" in todo
            assert "completed" in todo
            assert isinstance(todo["id"], int)
            assert isinstance(todo["title"], str)
            assert isinstance(todo["completed"], bool)


class TestChatEndpoint:
    """Tests for the /api/chat endpoint"""

    def test_chat_endpoint_exists(self):
        """Test that /api/chat endpoint is accessible"""
        response = client.post(
            "/api/chat",
            json={"message": "hello", "language": "en"}
        )
        assert response.status_code == 200

    def test_chat_response_structure(self):
        """Test that chat response has all required fields"""
        response = client.post(
            "/api/chat",
            json={"message": "show tasks", "language": "en"}
        )
        data = response.json()

        assert "response" in data
        assert "todos" in data
        assert "detected_language" in data
        assert "context_size" in data

        assert isinstance(data["response"], str)
        assert isinstance(data["todos"], list)
        assert isinstance(data["detected_language"], str)
        assert isinstance(data["context_size"], int)

    def test_chat_english_language(self):
        """Test chat with English language"""
        response = client.post(
            "/api/chat",
            json={"message": "show my tasks", "language": "en"}
        )
        data = response.json()

        assert data["detected_language"] == "en"
        assert len(data["response"]) > 0

    def test_chat_add_task_english(self):
        """Test adding a task in English"""
        response = client.post(
            "/api/chat",
            json={"message": "Add task: Integration test task", "language": "en"}
        )
        data = response.json()

        assert response.status_code == 200
        assert "Integration test task" in data["response"] or "added" in data["response"].lower()

        # Verify task was added by checking todos
        assert any("Integration test task" in todo["title"] for todo in data["todos"])

    def test_chat_list_tasks(self):
        """Test listing tasks"""
        response = client.post(
            "/api/chat",
            json={"message": "list tasks", "language": "en"}
        )
        data = response.json()

        assert response.status_code == 200
        assert len(data["todos"]) > 0

    def test_chat_multilingual_support(self):
        """Test that multilingual requests are handled"""
        # Test with Urdu language parameter
        response = client.post(
            "/api/chat",
            json={"message": "show tasks", "language": "ur"}
        )
        data = response.json()

        assert response.status_code == 200
        assert data["detected_language"] == "ur"

    def test_chat_context_tracking(self):
        """Test that conversation context is tracked"""
        # First message
        response1 = client.post(
            "/api/chat",
            json={"message": "hello", "language": "en"}
        )
        context_size_1 = response1.json()["context_size"]

        # Second message
        response2 = client.post(
            "/api/chat",
            json={"message": "how are you", "language": "en"}
        )
        context_size_2 = response2.json()["context_size"]

        # Context should increase
        assert context_size_2 > context_size_1

    def test_chat_error_handling(self):
        """Test that errors are handled gracefully"""
        # Test with empty message
        response = client.post(
            "/api/chat",
            json={"message": "", "language": "en"}
        )

        # Should still return a valid response structure
        data = response.json()
        assert "response" in data
        assert "todos" in data


class TestConversationContext:
    """Tests for conversation context endpoint"""

    def test_get_context_endpoint(self):
        """Test /api/context endpoint"""
        response = client.get("/api/context")
        assert response.status_code == 200

        data = response.json()
        assert "context" in data
        assert "size" in data
        assert "max_size" in data
        assert isinstance(data["context"], list)


class TestFrontendServing:
    """Tests for frontend file serving"""

    def test_root_serves_html(self):
        """Test that root serves the HTML file"""
        response = client.get("/")
        assert response.status_code == 200
        # Check if it returns HTML content
        assert "text/html" in response.headers.get("content-type", "")


if __name__ == "__main__":
    print("Running integration tests...")
    pytest.main([__file__, "-v", "--tb=short"])
