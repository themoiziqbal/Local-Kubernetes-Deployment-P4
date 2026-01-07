# Implementation Plan: AI-Powered Multilingual Voice-Enabled Todo Chatbot

**Branch**: `001-multimodal-todo-chatbot` | **Date**: 2025-12-13 | **Updated**: 2025-12-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-multimodal-todo-chatbot/spec.md`

**Note**: This plan has been updated to reflect the architectural pivot from console-first to web-first deployment (see ADR-0001). Original plan preserved console-based agent architecture; current implementation uses FastAPI web framework with phased feature rollout.

## Summary

Build a **web-based** AI-powered todo chatbot that accepts natural language commands via browser interface, with planned support for multilingual interaction and voice input. The system uses FastAPI for REST API backend, OpenAI API for AI capabilities (intent classification, language processing), and is deployed as a serverless application on Vercel.

**Technical Approach**: Web-first architecture with modular FastAPI backend. Core functionality includes intent-driven todo management using OpenAI API for natural language understanding, RESTful HTTP/JSON communication, and responsive HTML/CSS/JS frontend. Features are implemented in phases: P0 (MVP) delivers English text-based task management, P1 adds multilingual support, P2 adds voice capabilities.

**Architectural Decision**: See [ADR-0001](../../history/adr/0001-architectural-pivot-from-console-first-to-web-first-deployment.md) for rationale behind pivot from console-first to web-first deployment.

## Technical Context

**Language/Version**: Python 3.11+ (for FastAPI async capabilities and OpenAI API compatibility)

**Primary Dependencies**:
- FastAPI (async REST API framework)
- OpenAI API (GPT-3.5-turbo/GPT-4 for intent classification, language understanding, translation)
- Uvicorn (ASGI server for local development)
- HTML5/CSS3/JavaScript (vanilla - frontend)
- Pydantic (request/response validation)

**Storage**:
- **Current (MVP)**: In-memory Python list (todos: List[dict])
- **Planned (P1)**: SQLite for persistent task storage

**Testing**:
- **Current (MVP)**: Manual testing via web UI and API endpoints
- **Planned (Production)**: pytest (API contract tests, integration tests, user scenario tests)

**Target Platform**: Web browser (cross-platform: Windows, macOS, Linux, mobile)

**Project Type**: Web application (monolithic FastAPI backend + static frontend)

**Performance Goals**:
- Text command response: <2 seconds end-to-end
- Voice command response: <4 seconds (P2 - including transcription)
- Intent classification accuracy: >95%
- Language detection accuracy: >90% (P1)
- API latency: <500ms for CRUD operations

**Constraints**:
- **Current**: Web-only interface (no CLI)
- Single-user application (no authentication/multi-user support in MVP)
- Internet required for OpenAI API calls
- Max 1000 tasks optimized (personal use scale)
- Stateless HTTP API (conversation context in P1+)

**Scale/Scope**:
- Personal productivity tool (single user)
- **Phase 0 (MVP)**: English text-based interaction
- **Phase 1**: 7+ languages supported (English, Spanish, French, Mandarin, Arabic, Hindi, German)
- **Phase 2**: Voice input (Web Speech API or OpenAI Whisper)

## Constitution Check

*GATE: Must pass before implementation. Checked against Constitution v2.0.0.*

**Reference**: Constitution v2.0.0 (amended 2025-12-21) - [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
**Architectural Decision**: [ADR-0001](../../history/adr/0001-architectural-pivot-from-console-first-to-web-first-deployment.md) documents pivot from console-first to web-first

**Principle I - Modular Architecture**: ✅ PASS
- Functionality organized as modular components (routes, services, models)
- Clear separation: API layer (api/index.py), business logic (intent handling), data models (Task entity)
- Components communicate via function calls and shared data models
- Single responsibility: intent classification, todo CRUD operations, AI integration separated

**Principle II - AI-Powered Web Stack**: ✅ PASS
- FastAPI web framework for RESTful APIs
- OpenAI API (GPT-3.5-turbo) for intent classification and conversational AI
- HTML/CSS/JavaScript frontend (vanilla, responsive design)
- RESTful HTTP/JSON communication

**Principle III - Web-First, API-Ready**: ✅ PASS
- Primary interface: Web browser via HTML/CSS/JS frontend
- All functionality exposed through REST API endpoints (`/api/chat`, `/api/todos`)
- API-ready: Can add mobile app or CLI by consuming same REST endpoints
- Responsive design for cross-device compatibility

**Principle IV - Multimodal & Multilingual Intelligence (Phased)**: ⚠️ PARTIAL (Phased Implementation)
- **P0 (MVP - Current)**: ✅ English text input via web forms
- **P1 (Planned)**: ⚠️ Language detection and translation (not yet implemented)
- **P2 (Planned)**: ⚠️ Voice input (Web Speech API) - frontend has UI, backend integration pending
- **Justification**: Phased approach per Constitution v2.0.0 Principle IV - MVP delivers core value, additional modalities added iteratively

**Principle V - Intent-Driven Todo Management**: ✅ PASS (Simple Implementation)
- Natural language parsing using keyword matching + GPT-4 fallback
- Handles CRUD operations: add task, list tasks, complete task, delete task
- Graceful handling: AI fallback (`ask_openai`) when keywords don't match
- User-friendly responses with emojis and confirmations

**Principle VI - RESTful API Communication**: ✅ PASS
- HTTP methods: GET (`/api/todos`), POST (`/api/chat`)
- JSON payloads for request/response data
- Stateless design (no session state in MVP)
- Standard HTTP status codes (200 OK, error handling)

**Principle VII - Polite, Clear, Helpful Behavior**: ✅ PASS
- Natural language responses with emojis (✅ ✓ ○ 🗑️ 📝)
- Confirmation messages for operations ("✅ Task added: ...", "✅ Completed: ...")
- User-friendly messages (no technical error codes exposed)

**Principle VIII - Graceful Error Handling**: ⚠️ PARTIAL
- **Current**: Try/catch blocks in API endpoints, OpenAI API error handling
- **Missing**: Formal offline fallback, detailed error recovery guidance
- **Justification**: MVP prioritizes core functionality; production-grade error handling in next phase

**Principle IX - Test-Driven Development (Phased)**: ⚠️ MVP Phase (Tests Optional)
- **Current**: No automated tests (MVP prototype)
- **Justification**: Constitution v2.0.0 Principle IX allows tests optional for MVP, required for production
- **Planned**: API contract tests, integration tests for critical user flows before production deployment

**GATE STATUS**: ✅ MVP REQUIREMENTS PASS - Proceed with phased implementation
- Core principles satisfied for MVP delivery
- Partial implementations documented with phase plan
- Constitution v2.0.0 explicitly allows phased feature rollout

## Project Structure

### Documentation (this feature)

```text
specs/001-multimodal-todo-chatbot/
├── plan.md              # This file (updated for web-first architecture)
├── spec.md              # Original specification (to be updated for web UI)
├── tasks.md             # Task list (to be updated to reflect web implementation)
└── [ADR-0001]           # ../../history/adr/0001-architectural-pivot-*.md
```

### Source Code (repository root)

```text
# Web Application Structure (Current Implementation)

api/
└── index.py             # FastAPI application with REST endpoints
                         # - /api (health check)
                         # - /api/todos (GET - list tasks)
                         # - /api/chat (POST - natural language commands)
                         # - In-memory storage: todos list
                         # - OpenAI integration: ask_openai(), handle_message()

index.html               # Frontend - main web UI
                         # - Voice input UI (Web Speech API integration)
                         # - Chat interface with message history
                         # - Language selector (6 languages)
                         # - Task display and management

styles.css               # Styling - responsive design with animations

script.js                # Frontend logic
                         # - Chat interaction
                         # - Voice recognition (Web Speech API)
                         # - API communication (fetch)
                         # - Task rendering and actions

vercel.json              # Vercel deployment configuration

requirements.txt         # Python dependencies
requirements.vercel.txt  # Vercel-specific dependencies (no PyAudio)

# Partial Agent Implementation (src/ - for potential future use)

src/
├── agents/
│   ├── master_chat_agent.py       # Orchestrator (partially implemented)
│   ├── intent_classifier_agent.py # GPT-4 intent classification
│   └── task_agents/               # CRUD agents (add, read, update, delete)
│
├── models/
│   ├── task.py                    # Task dataclass
│   ├── conversation_context.py   # Context tracking model
│   └── user_preferences.py        # User settings model
│
├── services/
│   ├── task_repository.py         # SQLite repository (for future persistence)
│   ├── translation_service.py    # Translation API wrapper
│   └── voice_service.py           # Voice processing service
│
└── lib/
    ├── config.py                  # Environment configuration
    └── logging_config.py          # Logging setup

# Configuration & Data

config/
└── .env.example                   # API key template

data/
└── (planned) tasks.db            # SQLite database (not yet used)

# Deployment

.github/workflows/                 # (planned) CI/CD pipelines
vercel.json                        # Vercel serverless configuration
```

**Structure Decision**:
- **Current**: Monolithic FastAPI (`api/index.py`) + static frontend (HTML/CSS/JS) deployed on Vercel serverless
- **Rationale**: Simplest deployment model for MVP; single-file backend easy to iterate
- **Future**: Can migrate to modular structure (`api/routes/`, `api/services/`) or integrate `src/agents/` layer for advanced features

## Complexity Tracking

| Issue | Principle Violated | Justification | Mitigation Plan |
|-------|-------------------|---------------|-----------------|
| In-memory storage | FR-004 (persistence) | MVP prioritizes fast iteration; persistent storage adds deployment complexity | **P1**: Migrate to SQLite (task_repository.py already exists in src/) |
| No delete confirmation | FR-007 (user confirmation) | Current UI directly deletes tasks; acceptable for MVP with small task counts | **P1**: Add confirmation dialog in frontend (modal or inline prompt) |
| No language auto-detect | FR-008 (language detection) | Language selector (manual choice) sufficient for MVP; auto-detect requires backend integration | **P1**: Implement Language Detection Agent or use OpenAI API for detection |
| No translation | FR-009 (multilingual) | UI has language selector but no actual translation; English-only for MVP | **P1**: Integrate Translation Agent or OpenAI API for bidirectional translation |
| Stateless API | FR-014 (conversation context) | HTTP stateless by default; context tracking requires session management | **P1**: Add session middleware or use browser localStorage for context |
| Keyword matching | Principle V (intent-driven) | Current: keyword matching (`if "add" in msg`) with GPT fallback; less sophisticated than dedicated intent classifier | **Acceptable**: Works for MVP; **P1** can upgrade to dedicated Intent Classifier Agent if needed |

**Constitutional Compliance**: All deviations are explicitly allowed under Constitution v2.0.0 phased implementation approach. MVP delivers core value; production features added iteratively.

---

## Implementation Phases

### Phase 0: MVP (Current Status - Deployed on Vercel)

**Delivered:**
- ✅ Web UI with chat interface
- ✅ Basic todo CRUD operations (add, list, complete, delete)
- ✅ Natural language intent understanding (keyword + GPT fallback)
- ✅ OpenAI API integration for conversational AI
- ✅ Responsive frontend with voice UI elements
- ✅ Vercel serverless deployment

**Limitations:**
- In-memory storage (tasks lost on restart)
- No delete confirmation
- English-only (no translation despite language selector)
- No conversation context tracking
- No persistent voice transcription backend

---

### Phase 1: Production-Ready Features (Planned)

**Goals:**
1. **Data Persistence** (FR-004)
   - Migrate from in-memory to SQLite
   - Use existing `task_repository.py` from `src/services/`
   - Update `/api/todos` and `/api/chat` to use repository

2. **Delete Confirmation** (FR-007)
   - Add confirmation modal/dialog in frontend
   - Update delete logic to require user confirmation

3. **Multilingual Support** (FR-008, FR-009)
   - Implement language detection (OpenAI API or dedicated agent)
   - Add translation service (OpenAI API GPT-4 for bidirectional translation)
   - Update `/api/chat` to detect language → translate → process → translate response

4. **Conversation Context** (FR-014)
   - Add session management (server-side sessions or client-side localStorage)
   - Track last 5 exchanges per user
   - Enable implicit references ("delete it" after viewing task)

5. **Testing Infrastructure**
   - API contract tests (pytest)
   - Integration tests for critical user flows
   - Automated testing in CI/CD pipeline

---

### Phase 2: Voice & Advanced Features (Future)

**Goals:**
1. **Voice Input Backend**
   - Integrate OpenAI Whisper API for speech-to-text
   - Connect frontend Web Speech API to backend processing

2. **Voice Output**
   - OpenAI TTS API for text-to-speech responses
   - User preference toggle for voice output

3. **Task Filtering & Search** (FR-017)
   - Filter by priority, status, due date
   - Search by description keywords

4. **Partial Task Updates** (FR-006)
   - PATCH endpoint for field-specific updates
   - Update only specified fields (priority, due date, etc.)

---

## Key Architectural Decisions

**See [ADR-0001](../../history/adr/0001-architectural-pivot-from-console-first-to-web-first-deployment.md) for detailed rationale.**

1. **Web-First Deployment**: Browser-based UI instead of console CLI for universal accessibility
2. **FastAPI Monolith**: Single `api/index.py` file for MVP simplicity vs. agent-based microservices
3. **RESTful HTTP/JSON**: Standard web communication instead of MCP protocol
4. **Phased Implementation**: MVP → Production → Advanced features instead of all-at-once delivery
5. **Vercel Serverless**: Cloud hosting with automatic scaling instead of local executable distribution
6. **In-Memory MVP Storage**: Fast iteration over persistent storage for initial deployment

---

## Success Criteria (Updated for Web Implementation)

**MVP (Phase 0)** - ✅ ACHIEVED:
- Users can add, view, complete, and delete tasks via web browser
- Natural language commands work with reasonable accuracy
- Deployed and accessible via public URL (Vercel)
- Responsive UI works on desktop and mobile browsers

**Production (Phase 1)** - Targets:
- 100% task persistence across app restarts (SQLite)
- 90% language detection accuracy for 7+ languages
- Conversation context enables follow-up commands
- Delete confirmation prevents accidental data loss
- API contract tests cover all critical endpoints

**Advanced (Phase 2)** - Targets:
- 85% voice transcription accuracy (Whisper API)
- Voice input/output fully functional
- Task filtering and search work seamlessly
- <2s response time for text, <4s for voice

---

**COMPLETION STATUS**: Plan updated to reflect web-first architecture per Constitution v2.0.0 and ADR-0001. Phase 0 (MVP) deployed; Phase 1 (production features) ready for implementation.
