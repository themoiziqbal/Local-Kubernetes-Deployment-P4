# ChatbotTodoApp Architecture Documentation

## Overview

This document explains the architectural decisions, code organization, and dual-backend design of the ChatbotTodoApp.

## Dual-Backend Architecture

### Why Two Backends?

The project uses a **dual-backend architecture** to support two different use cases:

1. **Web API Backend** (`api/index.py`)
   - Optimized for web interface
   - Full multilingual translation support
   - Lightweight and stateless
   - Direct database access
   - RESTful API design

2. **CLI Backend** (`src/cli/chatbot_cli.py`)
   - Optimized for terminal/console use
   - Agent-based architecture for complex workflows
   - Voice input/output support
   - User preference management
   - Rich interactive command interface

### When to Use Each Backend

**Use Web API Backend When:**
- Deploying to Vercel, Railway, or other web platforms
- Building web/mobile frontends
- Need multilingual translation
- Want RESTful API access
- Require scalability and stateless design

**Use CLI Backend When:**
- Running in terminal/console
- Need voice input/output
- Want agent-based orchestration
- Require rich interactive CLI
- Local development and testing

### Backend Selection

Edit `run_server.py` to switch backends:

```python
# For Web API (recommended for production)
from api.index import app

# For CLI Backend (for terminal use)
# from src.cli.chatbot_cli import app
```

## Code Organization

### Directory Structure

```
ChatbotTodoApp/
├── api/                    # Web API Backend
│   └── index.py           # Main FastAPI app with translation
│
├── src/                    # Core Application Code
│   ├── agents/            # Agent-based Architecture
│   │   ├── master_chat_agent.py       # Orchestrates all agents
│   │   ├── intent_classifier_agent.py # Classifies user intent
│   │   └── task_agents/              # Task-specific agents
│   │       ├── task_add_agent.py
│   │       ├── task_read_agent.py
│   │       ├── task_update_agent.py
│   │       └── task_delete_agent.py
│   │
│   ├── models/            # Data Models
│   │   ├── task.py                   # Task entity
│   │   ├── conversation_context.py   # Context tracking
│   │   └── user_preferences.py       # User settings
│   │
│   ├── services/          # Business Logic Services
│   │   ├── task_repository.py        # Database operations
│   │   ├── translation_service.py    # Translation
│   │   └── voice_service.py          # Voice I/O
│   │
│   ├── cli/               # CLI Interface
│   │   └── chatbot_cli.py            # CLI backend + interface
│   │
│   └── lib/               # Utilities
│       ├── config.py                 # Configuration
│       ├── logging_config.py         # Logging setup
│       └── mcp_helpers.py            # MCP integration
│
├── tests/                 # Test Suite
│   ├── __init__.py
│   └── test_api_integration.py       # API tests
│
├── data/                  # Runtime Data (auto-created)
│   ├── tasks.db                      # SQLite database
│   └── preferences.json              # User preferences
│
├── Frontend Files
│   ├── index.html         # Web UI
│   ├── script.js          # Frontend logic
│   └── styles.css         # Styling
│
└── Configuration Files
    ├── run_server.py      # Server entry point
    ├── requirements.txt   # Production dependencies
    ├── requirements-dev.txt  # Development dependencies
    ├── pytest.ini         # Test configuration
    └── .env               # Environment variables
```

## Key Design Patterns

### 1. Repository Pattern
**File**: `src/services/task_repository.py`

Abstracts database access behind a clean interface:
```python
task_repo.create(task)    # Create
task_repo.get_by_id(id)   # Read
task_repo.update(task)    # Update
task_repo.delete(id)      # Delete
task_repo.get_all()       # List
```

### 2. Agent Pattern
**Files**: `src/agents/`

Each agent has a specific responsibility:
- **MasterChatAgent**: Orchestrates the overall flow
- **IntentClassifierAgent**: Determines user intent
- **TaskAgents**: Specialized for CRUD operations

### 3. Service Layer
**Files**: `src/services/`

Business logic separated from presentation:
- **TranslationService**: Handles multilingual translation
- **VoiceService**: Manages speech-to-text and text-to-speech
- **TaskRepository**: Database operations

### 4. Dependency Injection
Services are injected into agents:
```python
master_agent = MasterChatAgent(
    api_key=config.openai_api_key,
    repository=task_repo
)
```

## Error Handling Strategy

### Logging Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for unexpected but handled situations
- **ERROR**: Error messages for failures

### Error Handling Pattern

```python
try:
    # Operation
    result = perform_operation()
    logger.info("Operation successful")
    return result
except SpecificException as e:
    logger.error(f"Specific error: {e}", exc_info=True)
    return fallback_value
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

## API Design

### Web API Endpoints (`api/index.py`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Serve web UI |
| GET | `/api/todos` | Get all tasks |
| POST | `/api/chat` | Process chat message |
| GET | `/api/context` | Get conversation context |

### Request/Response Format

**Request**:
```json
{
  "message": "Add task: Buy groceries",
  "language": "en"
}
```

**Response**:
```json
{
  "response": "✅ Task added: Buy groceries",
  "todos": [...],
  "detected_language": "en",
  "context_size": 1
}
```

## Database Schema

### Tasks Table

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    due_date TEXT,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
    status TEXT CHECK(status IN ('pending', 'in-progress', 'completed')),
    tags TEXT,  -- JSON array
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
```

## Translation Pipeline

1. **Language Detection**
   - User sends message
   - OpenAI detects language (if not specified)

2. **Translation to English**
   - If message is not in English
   - Translate to English for processing

3. **Processing**
   - Handle message in English
   - Execute task operations

4. **Translation to Target Language**
   - Translate response back to user's language
   - Return translated response

## Future Improvements

### Potential Enhancements
- [ ] Add Redis caching for translations
- [ ] Implement rate limiting
- [ ] Add user authentication
- [ ] Support for recurring tasks
- [ ] Task categories and projects
- [ ] Export/import functionality
- [ ] Collaborative task management
- [ ] Mobile app support

### Code Quality
- [ ] Add more unit tests
- [ ] Increase test coverage to 80%+
- [ ] Add type hints throughout
- [ ] Set up CI/CD pipeline
- [ ] Add code linting (black, flake8)

## Contributing Guidelines

When contributing to this project:

1. **Follow the architecture patterns** described in this document
2. **Add tests** for new features
3. **Update documentation** when adding new endpoints or features
4. **Use proper logging** instead of print statements
5. **Handle errors gracefully** with try-except blocks
6. **Keep backends separate** - don't mix web and CLI logic

## Maintenance Notes

### Deprecated/Legacy Files

- `test_backend.py` - Old test file for CLI backend (kept for reference)
- `test_functionality.py` - Old functionality tests (superseded by pytest tests)

### File Naming Conventions

- `*_agent.py` - Agent implementations
- `*_service.py` - Service layer implementations
- `test_*.py` - Test files (pytest convention)
- `*_config.py` - Configuration files

## Contact & Support

For questions about the architecture or contributions:
- Check existing documentation
- Review code comments
- Open an issue on GitHub
- Refer to this ARCHITECTURE.md file

---

**Last Updated**: 2025-12-29
**Version**: 2.1.0
**Maintainer**: ChatbotTodoApp Team
