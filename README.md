# AI-Powered Multilingual Voice-Enabled Todo Chatbot

A console-based AI-powered todo chatbot that accepts natural language commands in both text and voice formats, automatically detects and translates between 7+ languages, and uses a modular agent architecture for intent classification, task management, and multimodal interaction.

## Features

- **Text-Based Task Management**: Manage tasks using natural language English commands (add, view, update, delete)
- **Multilingual Support**: Interact in 7+ languages (English, Spanish, French, Mandarin, Arabic, Hindi, German)
- **Voice Input/Output**: Hands-free voice commands with speech-to-text and text-to-speech
- **Conversational Context**: Understand implicit references and follow-up questions
- **Partial Task Updates**: Modify individual task fields without re-specifying entire task

## Quick Start

### Prerequisites

- Python 3.11 or higher
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ChatbotTodoApp
git checkout 001-multimodal-todo-chatbot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp config/.env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Chatbot

```bash
python src/cli/chatbot_cli.py
```

### Basic Usage

```
You: add a task to buy groceries tomorrow
Chatbot: Task added: buy groceries (due December 14, 2025)

You: show my tasks
Chatbot: You have 1 task:
  1. [pending] buy groceries (due: Dec 14, 6:00 PM)

You: mark task 1 as completed
Chatbot: Task 1 marked as completed. Great job!
```

## Architecture

This project features a **dual-backend architecture** designed for flexibility:

### Backend 1: Web API (`api/index.py`)
- **Purpose**: Production web interface with full multilingual support
- **Features**:
  - ✅ Full translation service (English, Urdu, Hindi, Spanish, French, Arabic)
  - ✅ Language auto-detection
  - ✅ Conversation context tracking
  - ✅ RESTful API endpoints
  - ✅ Comprehensive error handling and logging
- **Used by**: Web interface (index.html), Vercel deployments
- **Endpoints**:
  - `GET /` - Serves web UI
  - `GET /api/todos` - Get all tasks
  - `POST /api/chat` - Chat with multilingual support
  - `GET /api/context` - Get conversation context

### Backend 2: CLI Application (`src/cli/chatbot_cli.py`)
- **Purpose**: Console/terminal interface with agent orchestration
- **Features**:
  - ✅ Agent-based architecture (MasterChatAgent, IntentClassifier, TaskAgents)
  - ✅ Voice input/output support
  - ✅ User preferences management
  - ✅ CLI commands and interactive mode
- **Used by**: Terminal/console users, development

### Backend Selection

The `run_server.py` file determines which backend to load:

```python
from api.index import app  # Web-optimized backend (current)
# OR
from src.cli.chatbot_cli import app  # CLI-optimized backend
```

**Current Configuration**: Web API backend is active for full translation support.

## Project Structure

```
ChatbotTodoApp/
├── api/                 # Web API backend (FastAPI)
│   └── index.py         # Main web API with translation support
├── src/
│   ├── agents/          # Agent implementations (IntentClassifier, TaskAgents)
│   ├── models/          # Data models (Task, ConversationContext, UserPreferences)
│   ├── services/        # Services (TaskRepository, Voice, Translation)
│   ├── cli/             # CLI interface and CLI backend
│   └── lib/             # Utilities (config, logging, MCP helpers)
├── tests/               # Integration and unit tests
│   └── test_api_integration.py  # API endpoint tests
├── data/                # Database and preferences (auto-created)
├── config/              # Configuration templates
├── specs/               # Feature specifications and planning docs
├── index.html           # Web interface
├── script.js            # Frontend JavaScript
├── styles.css           # Frontend styling
└── run_server.py        # Server entry point
```

## Development Status

### ✅ Completed Features
- ✅ **Dual-Backend Architecture** - Web API and CLI backends
- ✅ **Multilingual Support** - English, Urdu, Hindi, Spanish, French, Arabic
- ✅ **Language Auto-Detection** - Automatic language identification
- ✅ **Translation Service** - OpenAI-powered translation
- ✅ **Task Management** - Create, read, update, delete tasks
- ✅ **SQLite Database** - Persistent task storage
- ✅ **Voice Input (Web)** - Web Speech API integration
- ✅ **Voice Output (Web)** - Text-to-Speech support
- ✅ **Conversation Context** - Tracks last 5 exchanges
- ✅ **Web Interface** - Modern, responsive UI
- ✅ **Agent Architecture** - MasterChatAgent, IntentClassifier, TaskAgents
- ✅ **Comprehensive Error Logging** - Detailed logging throughout
- ✅ **Integration Tests** - API endpoint test coverage
- ✅ **Environment Configuration** - .env support for all backends

### 🔧 Recent Improvements (2025-12-29)
- ✅ Fixed backend module loading (switched to web-optimized backend)
- ✅ Added comprehensive error logging with Python logging module
- ✅ Created integration test suite for API endpoints
- ✅ Documented dual-backend architecture
- ✅ Fixed Unicode encoding issues in translation errors
- ✅ Added proper .env loading for API key access

## Testing

### Running Tests

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_api_integration.py -v
```

Run tests with coverage:
```bash
pytest tests/ --cov=api --cov=src --cov-report=html
```

### Test Structure

- `tests/test_api_integration.py` - Integration tests for API endpoints
  - Tests for `/api/todos` endpoint
  - Tests for `/api/chat` endpoint with multilingual support
  - Tests for conversation context tracking
  - Tests for error handling

### Test Configuration

Tests are configured in `pytest.ini` with the following settings:
- Test discovery patterns
- Output formatting
- Logging configuration
- Coverage options

## Documentation

For detailed documentation, see:
- [Quickstart Guide](specs/001-multimodal-todo-chatbot/quickstart.md)
- [Technical Plan](specs/001-multimodal-todo-chatbot/plan.md)
- [Data Model](specs/001-multimodal-todo-chatbot/data-model.md)
- [Research](specs/001-multimodal-todo-chatbot/research.md)

## Web Interface

The application now includes a web interface that can be hosted on GitHub Pages, with the backend deployed to Railway.

### Frontend Files
- `index.html` - Main web interface
- `styles.css` - Styling for the interface
- `script.js` - JavaScript functionality

### Deployment

#### Backend (Railway)

1. Create an account on [Railway](https://railway.app)
2. Create a new project and connect your GitHub repository
3. Set the following environment variables:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `DATABASE_PATH` - Path to SQLite database (default: `data/tasks.db`)
4. Set the start command to: `python run_server.py`
5. Deploy the application
6. Note the deployed URL (e.g., `https://your-app-name.up.railway.app`)

#### Frontend (GitHub Pages)

1. Push the frontend files (index.html, styles.css, script.js) to your repository
2. Go to your repository settings
3. In the "Pages" section, select source as the main branch
4. The frontend will be available at `https://your-username.github.io/repository-name`

#### Configuration

After deploying the backend, update the `BACKEND_URL` in `script.js`:

```javascript
const BACKEND_URL = 'https://your-railway-app-url.railway.app'; // Replace with your Railway URL
```

### API Endpoints

- `GET /` - Health check
- `POST /chat` - Process chat message (CLI endpoint)
- `GET /api/todos` - Get all todos
- `POST /api/chat` - Web chat endpoint (returns response + todos)

## Running the Server

To run the backend server locally:

```bash
python run_server.py
```

The server will start on `http://localhost:8000` with API documentation available at `http://localhost:8000/docs`.

## License

[Your License Here]

## Contributing

[Contributing Guidelines]
