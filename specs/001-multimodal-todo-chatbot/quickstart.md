# Quickstart Guide: AI-Powered Multilingual Voice-Enabled Todo Chatbot

**Feature Branch**: `001-multimodal-todo-chatbot`
**Date**: 2025-12-13

## Overview

This guide will help you set up, run, and test the AI-Powered Multilingual Voice-Enabled Todo Chatbot. Follow these steps to get the chatbot running on your local machine.

---

## Prerequisites

### Required Software

- **Python**: 3.11 or higher ([Download](https://www.python.org/downloads/))
- **Git**: For version control ([Download](https://git-scm.com/downloads))
- **OpenAI API Key**: Sign up at [OpenAI Platform](https://platform.openai.com/)

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **RAM**: 2 GB minimum (4 GB recommended)
- **Disk Space**: 500 MB for dependencies and database
- **Internet Connection**: Required for OpenAI API calls (Whisper, TTS, GPT-4)
- **Microphone**: Optional (for voice input mode)
- **Audio Output**: Optional (for voice output mode)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd ChatbotTodoApp
git checkout 001-multimodal-todo-chatbot
```

### Step 2: Create Virtual Environment

**macOS/Linux**:
```bash
python3.11 -m venv venv
source venv/bin/activate
```

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected dependencies** (will be in `requirements.txt`):
- `openai-agents>=0.1.0` - OpenAI Agents SDK
- `mcp>=1.7.0` - Model Context Protocol SDK
- `fastmcp>=0.1.0` - FastMCP for simplified MCP tool registration
- `openai>=1.50.0` - OpenAI Python client
- `sounddevice>=0.4.6` - Microphone input capture
- `playsound>=1.3.0` - Audio playback for TTS
- `jsonschema>=4.20.0` - JSON Schema validation
- `pytest>=7.4.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-mock>=3.12.0` - Mocking for tests

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp config/.env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here

# Optional: Model Configuration
OPENAI_MODEL=gpt-4-turbo
WHISPER_MODEL=whisper-1
TTS_MODEL=gpt-4o-mini-tts
TTS_VOICE=coral

# Optional: Database Configuration
DATABASE_PATH=data/tasks.db
PREFERENCES_PATH=data/preferences.json

# Optional: Logging
LOG_LEVEL=INFO
LOG_FILE=logs/chatbot.log
```

**Security Note**: Never commit `.env` file to version control. It's already in `.gitignore`.

---

## Running the Chatbot

### First Run (Database Initialization)

On first run, the chatbot will automatically:
1. Create `data/` directory
2. Initialize `tasks.db` SQLite database with schema
3. Create `preferences.json` with default settings

```bash
python src/cli/chatbot_cli.py
```

You should see:

```
🤖 AI Todo Chatbot v1.0
Database initialized at data/tasks.db
Type your command or '/help' for assistance.

You:
```

### Basic Usage

**Text Commands** (default mode):
```
You: add a task to buy groceries tomorrow
Chatbot: Task added: buy groceries (due December 14, 2025)

You: show my tasks
Chatbot: You have 1 task:
  1. [pending] buy groceries (due: Dec 14, 6:00 PM)

You: mark task 1 as completed
Chatbot: Task 1 marked as completed. Great job!

You: delete task 1
Chatbot: Are you sure you want to delete "buy groceries"? (yes/no)
You: yes
Chatbot: Task deleted.
```

**Voice Mode** (toggle with `/voice`):
```
You: /voice on
Chatbot: Voice input enabled. Speak your command after the beep.
[Speak]: "Add a task to call mom"
Chatbot: [Audio + Text] Task added: call mom
```

**Multilingual Example** (Spanish):
```
You: añadir tarea comprar leche
Chatbot: Tarea añadida: comprar leche
```

### Special Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/voice on` | Enable voice input/output |
| `/voice off` | Disable voice mode |
| `/language <code>` | Set preferred language (e.g., `/language es` for Spanish) |
| `/clear` | Clear conversation context |
| `/settings` | View/modify user preferences |
| `/exit` | Quit the chatbot |

---

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Suites

**Contract Tests** (validate MCP schemas):
```bash
pytest tests/contract/ -v
```

**Integration Tests** (end-to-end workflows):
```bash
pytest tests/integration/ -v
```

**Unit Tests** (individual agent logic):
```bash
pytest tests/unit/ -v
```

### Run Tests with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Expected Test Output

```
tests/contract/test_mcp_schemas.py::test_all_schemas_valid PASSED
tests/integration/test_text_workflow.py::test_add_and_list_tasks PASSED
tests/integration/test_multilingual_workflow.py::test_spanish_input PASSED
tests/unit/test_intent_classifier.py::test_classify_create_intent PASSED

======================== 45 passed in 12.3s ========================
```

---

## Sample Workflows

### Workflow 1: Basic Task Management (P1 - English Text)

```
You: add a task to prepare quarterly report
Chatbot: Task added: prepare quarterly report

You: show my tasks
Chatbot: You have 1 task:
  1. [pending] prepare quarterly report

You: update task 1 to say prepare Q4 2025 report
Chatbot: Task 1 updated: prepare Q4 2025 report

You: set the priority of task 1 to high
Chatbot: Task 1 priority set to high

You: mark task 1 as in-progress
Chatbot: Task 1 status changed to in-progress

You: show tasks with high priority
Chatbot: High priority tasks:
  1. [in-progress] prepare Q4 2025 report (priority: high)
```

### Workflow 2: Multilingual Interaction (P2 - Spanish)

```
You: añadir tarea: reunión con el equipo mañana
Chatbot: Tarea añadida: reunión con el equipo (fecha límite: 14 de diciembre)

You: mostrar mis tareas
Chatbot: Tienes 1 tarea:
  1. [pendiente] reunión con el equipo (fecha límite: 14 dic, 9:00 AM)
```

### Workflow 3: Voice Input (P3)

```
You: /voice on
Chatbot: Voice input enabled. Press ENTER and speak your command.
You: [Press ENTER]
[Beep]
[Speak]: "Add a task to water the plants"
Chatbot: [Audio + Text] Task added: water the plants
```

### Workflow 4: Conversational Context (P5)

```
You: show task 5
Chatbot: Task 5: [pending] buy organic milk (priority: medium)

You: delete it
Chatbot: Are you sure you want to delete "buy organic milk"? (yes/no)

You: yes
Chatbot: Task deleted.
```

---

## Troubleshooting

### Issue: "OpenAI API key not found"

**Solution**: Ensure `.env` file exists with `OPENAI_API_KEY=sk-...`

```bash
cat .env  # macOS/Linux
type .env  # Windows
```

### Issue: "Permission denied" for microphone

**Solution**: Grant microphone access to terminal/Python in system settings

- **macOS**: System Preferences → Security & Privacy → Privacy → Microphone
- **Windows**: Settings → Privacy → Microphone
- **Linux**: Check PulseAudio/ALSA permissions

### Issue: "Module 'mcp' not found"

**Solution**: Reinstall dependencies in virtual environment

```bash
pip install --upgrade -r requirements.txt
```

### Issue: Database locked error

**Solution**: Ensure no other chatbot instance is running

```bash
# macOS/Linux
rm data/tasks.db-wal data/tasks.db-shm

# Windows
del data\tasks.db-wal data\tasks.db-shm
```

### Issue: Voice input not working

**Solution**: Test audio input device

```python
import sounddevice as sd
print(sd.query_devices())  # List available devices
sd.default.device = 0  # Set default microphone index
```

---

## Project Structure (Quick Reference)

```
ChatbotTodoApp/
├── src/
│   ├── agents/          # Agent implementations (Master Chat, Intent Classifier, etc.)
│   ├── models/          # Data models (Task, ConversationContext, UserPreferences)
│   ├── services/        # MCP wrappers (TaskRepository, Whisper, TTS, Translation)
│   ├── cli/             # ChatKit console interface entry point
│   └── lib/             # Utilities (MCP helpers, logging)
├── tests/               # Contract, integration, unit tests
├── data/                # SQLite database and preferences (auto-created)
├── config/              # .env.example template
├── specs/               # Feature specs and planning docs
└── docs/                # Architecture and agent registry
```

---

## Next Steps

1. **Explore**: Try different commands and languages
2. **Customize**: Modify `UserPreferences` in `data/preferences.json`
3. **Extend**: Add new agents or intents (see `docs/architecture.md`)
4. **Test**: Run full test suite to validate setup

---

## Support

- **Documentation**: See `docs/` directory for architecture and agent registry
- **Issues**: Report bugs via GitHub Issues
- **Contributing**: See `CONTRIBUTING.md` (if available)

---

**Happy task managing! 🚀**
