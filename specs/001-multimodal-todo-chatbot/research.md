# Research: AI-Powered Multilingual Voice-Enabled Todo Chatbot

**Date**: 2025-12-13
**Feature Branch**: `001-multimodal-todo-chatbot`
**Phase**: 0 (Research & Unknown Resolution)

## Purpose

This document resolves all "NEEDS CLARIFICATION" items from the Technical Context section of plan.md and provides architectural decisions with rationale for all technology choices.

---

## 1. OpenAI Agents SDK Integration

### Decision: Use Manager Pattern with OpenAI Agents SDK

**Rationale**: The [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) provides two orchestration patterns: Manager (agents as tools) and Handoffs. For our chatbot, the Manager pattern is optimal because:
- Single thread of control maintains conversation context
- Master Chat Agent retains full awareness of workflow state
- Sub-agents (Intent Classifier, Language Detector, etc.) serve as specialized tools
- Deterministic orchestration improves reliability

**Alternatives Considered**:
- **Handoffs Pattern**: Rejected because handing off control between peer agents would fragment conversation context and make state management complex
- **Custom orchestration**: Rejected because OpenAI Agents SDK provides built-in session management, tracing, and debugging

**Implementation Approach**:
- Master Chat Agent coordinates all workflow steps via code-based orchestration
- Sub-agents registered as tools using `@agent.tool()` decorator
- Use structured outputs for deterministic classification (intent, language detection)
- Built-in tracing for debugging multi-agent flows

**References**:
- [Orchestrating multiple agents - OpenAI Agents SDK](https://openai.github.io/openai-agents-python/multi_agent/)
- [Multi-Agent Portfolio Collaboration with OpenAI Agents SDK](https://cookbook.openai.com/examples/agents_sdk/multi-agent-portfolio-collaboration/multi_agent_portfolio_collaboration)

---

## 2. MCP SDK Implementation

### Decision: Use Decorator-Based Tool Registration with FastMCP

**Rationale**: The [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) provides tool registration patterns, with [FastMCP](https://github.com/jlowin/fastmcp) offering the simplest high-level interface:
- Decorator-based registration: `@server.tool()` handles schema generation automatically
- Supports structured outputs (JSON Schema 2020-12)
- Asyncio-native for high concurrency
- Latest spec compliance (2025-11-25) includes tool name validation and sampling with tools

**Alternatives Considered**:
- **Low-Level Server API**: Rejected because manually defining `types.Tool` objects adds boilerplate without benefit for our use case
- **Direct OpenAI API calls**: Rejected because violates Constitution Principle VI (MCP-Based Communication)

**Implementation Approach**:
- Wrap Whisper API, TTS API, and translation service as MCP tools
- Expose SQLite database as MCP resource (read/write tasks)
- Use async functions for all I/O-bound operations
- Return structured data (dictionaries) for tool outputs

**References**:
- [GitHub - modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- [Model context protocol (MCP) - OpenAI Agents SDK](https://openai.github.io/openai-agents-python/mcp/)
- [GitHub - jlowin/fastmcp: Fast, Pythonic way to build MCP servers](https://github.com/jlowin/fastmcp)

---

## 3. OpenAI ChatKit Console UI

### Decision: Use ChatKit Python SDK with FastAPI Backend

**Rationale**: [ChatKit Python SDK](https://openai.github.io/chatkit-python/) enables console-based conversational UI with:
- Automatic message threading and response streaming
- Built-in handling of complex chat development (UI state management)
- Integration with OpenAI Agents SDK for backend
- "Thinking" indicators and chain-of-thought visualizations

**Implementation Note**: ChatKit is primarily designed for web-based chat interfaces. For pure console interaction, we'll use the Python SDK's backend capabilities with a simple terminal wrapper for input/output.

**Alternatives Considered**:
- **Raw OpenAI API + Custom Console Loop**: Rejected because reinvents streaming, message history, and session management
- **Third-party CLI frameworks (Rich, Prompt Toolkit)**: Could supplement ChatKit for better terminal formatting

**Implementation Approach**:
- Use ChatKit Python SDK for session management and agent integration
- Wrap ChatKit backend with simple console I/O loop (`input()` for text, voice toggle command)
- Leverage response streaming for real-time feedback
- Use FastAPI backend pattern from [ChatKit advanced samples](https://github.com/openai/openai-chatkit-advanced-samples)

**References**:
- [ChatKit | OpenAI API](https://platform.openai.com/docs/guides/chatkit)
- [Chatkit Python SDK](https://openai.github.io/chatkit-python/)
- [GitHub - openai/chatkit-python](https://github.com/openai/chatkit-python)

---

## 4. Voice Processing Best Practices

### Decision: Use OpenAI Whisper API (turbo model) for STT, OpenAI TTS API (gpt-4o-mini-tts) for TTS

**STT Rationale**:
- **Whisper API turbo model**: Optimized version of large-v3 with faster transcription and minimal accuracy loss
- **Audio format optimization**: Use 32 kbps, 12 kHz to reduce file size by 50% without quality loss
- **Latency**: Cloud API provides ~1-2s latency (acceptable for non-realtime console use)
- [Faster-whisper](https://github.com/SYSTRAN/faster-whisper) (local): 4x faster than OpenAI's implementation, but adds deployment complexity

**TTS Rationale**:
- **gpt-4o-mini-tts model**: Newest, most reliable model for intelligent realtime applications
- **Streaming support**: Chunk transfer encoding allows audio playback before full file generation
- **Audio format**: Use WAV for low-latency console playback via `playsound` library
- **Voice selection**: Offer multiple voices (coral, alloy, echo, etc.) via user preferences

**Alternatives Considered**:
- **Local Whisper (faster-whisper)**: Higher performance but requires GPU/CPU setup, complicates deployment
- **WhisperLive**: Real-time streaming variant (380-520ms latency) - overkill for turn-based console chatbot
- **Alternative TTS**: ElevenLabs, Azure - rejected to maintain OpenAI technology stack consistency (Constitution Principle II)

**Implementation Approach**:
- **Microphone input**: Use `sounddevice` library to capture audio chunks
- **STT processing**: Send audio to Whisper API, receive transcribed text
- **TTS playback**: Stream TTS response to WAV file, play via `playsound` library
- **Console integration**: Add voice mode toggle command (e.g., `/voice on`)

**References**:
- [Optimise OpenAI Whisper API](https://dev.to/mxro/optimise-openai-whisper-api-audio-format-sampling-rate-and-quality-29fj)
- [GitHub - SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [Text to speech | OpenAI API](https://platform.openai.com/docs/guides/text-to-speech)
- [How to use the OpenAI Text-to-Speech API](https://www.datacamp.com/tutorial/how-to-use-the-openai-text-to-speech-api)

---

## 5. Language Detection & Translation

### Decision: Use GPT-4 with Structured Outputs for Language Detection and Translation

**Language Detection Rationale**:
- Use GPT-4 with structured output (JSON Schema) to return `{language_code: str, confidence: float}`
- Supported languages: English (en), Spanish (es), French (fr), Mandarin (zh), Arabic (ar), Hindi (hi), German (de)
- Prompt engineering: "Detect the language of the following text. Return ISO 639-1 code and confidence 0-1."
- Fallback: If confidence <0.7, ask user to clarify language preference

**Translation Rationale**:
- Bidirectional translation: User language → English (for internal processing) → User language (for responses)
- GPT-4 provides high-quality translation across all 7 target languages
- Consistency check: For critical operations (delete, update), optionally translate response back to English to verify intent preservation

**Alternatives Considered**:
- **Dedicated translation APIs** (Google Translate, DeepL): Rejected to maintain OpenAI stack consistency
- **Langdetect library**: Fast but less accurate for short phrases; GPT-4 better handles conversational context

**Implementation Approach**:
- Language Detection Agent: GPT-4 call with structured output schema
- Translation Agent: GPT-4 with prompt template "Translate the following text from {source_lang} to {target_lang}: {text}"
- Caching: Store detected language in ConversationContext to avoid re-detection each turn
- Edge case: Mixed-language input triggers clarification question

**References**:
- [Building AI Agents with OpenAI SDK](https://medium.com/data-science-collective/building-ai-agents-with-openai-sdk-5e48a90dccb2)

---

## 6. SQLite as MCP Resource

### Decision: Use mcp-server-sqlite Pattern with FastMCP for CRUD Operations

**Rationale**:
- [mcp-server-sqlite](https://pypi.org/project/mcp-server-sqlite/) demonstrates exposing SQLite as MCP resource
- FastMCP simplifies resource registration with `@server.resource()` decorator
- WAL (Write-Ahead Logging) mode enables concurrent read access for multi-agent scenarios
- Parameterized queries prevent SQL injection

**Schema Design**:
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    due_date TEXT,  -- ISO 8601 format (YYYY-MM-DD HH:MM:SS)
    priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
    status TEXT CHECK(status IN ('pending', 'in-progress', 'completed')) DEFAULT 'pending',
    tags TEXT,  -- JSON array stored as text
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

**Alternatives Considered**:
- **File-based JSON storage**: Rejected due to lack of query capabilities (filtering by priority, date)
- **PostgreSQL/MySQL**: Overkill for single-user local application; violates simplicity principle
- **Read-only MCP resource**: Rejected; full CRUD required for todo operations

**Implementation Approach**:
- TaskRepository service wraps SQLite with MCP resource protocol
- Expose resources: `task://list`, `task://get/{id}`, `task://schema`
- Provide MCP tools: `create_task`, `update_task`, `patch_task`, `delete_task`
- Use absolute paths for database file (`data/tasks.db`)
- Enable WAL mode: `PRAGMA journal_mode=WAL;`

**References**:
- [mcp-server-sqlite · PyPI](https://pypi.org/project/mcp-server-sqlite/)
- [Breaking Isolation: A Practical Guide to Building an MCP Server with SQLite](https://felix-pappe.medium.com/breaking-isolation-a-practical-guide-to-building-an-mcp-server-with-sqlite-68c800a25d42)
- [A Deep Dive into MCP Server for SQLite](https://skywork.ai/skypage/en/A-Deep-Dive-into-MCP-Server-for-SQLite-The-Ultimate-Guide-for-AI-Engineers/1971012059378610176)

---

## 7. Testing Strategy for AI Agents

### Decision: Three-Layer Testing with Pytest, JSON Schema Validation, and Mocking

**Contract Testing**:
- Use `jsonschema` library to validate all MCP tool/resource schemas against JSON Schema 2020-12
- Verify agent input/output schemas match MCP contracts
- Test: Every MCP tool must have valid JSON Schema with required fields

**Integration Testing**:
- Test multi-agent workflows end-to-end (e.g., voice input → STT → language detection → translation → intent classification → task add → response)
- Use pytest fixtures to set up test database and conversation context
- Mock OpenAI API calls with `pytest-mock` or `responses` library to avoid costs
- Test all user scenarios from spec.md (P1-P5) with Given/When/Then format

**Unit Testing**:
- Test individual agent logic (intent classification prompt templates, language detection confidence thresholds)
- Mock MCP tool calls to isolate agent behavior
- Test edge cases: empty input, unsupported language, ambiguous intent

**Mocking Strategy**:
- Use `unittest.mock` to mock OpenAI API responses (Whisper, TTS, GPT-4 completions)
- Create fixtures with realistic sample responses (transcriptions, translations, classifications)
- Test error paths: API timeout, service unavailable, invalid response format

**Implementation Approach**:
- Directory structure: `tests/contract/`, `tests/integration/`, `tests/unit/`
- Use pytest markers: `@pytest.mark.contract`, `@pytest.mark.integration`, `@pytest.mark.unit`
- CI/CD: Run contract and unit tests on every commit, integration tests on PR
- Coverage target: >80% code coverage (excluding OpenAI SDK internals)

**References**:
- [MCP Server in Python — Everything I Wish I'd Known on Day One](https://www.digitalocean.com/community/tutorials/mcp-server-python)

---

## Technology Stack Summary (Finalized)

| Component | Technology | Version/Model | Rationale |
|-----------|-----------|---------------|-----------|
| **Agent Framework** | OpenAI Agents SDK | Latest (Python) | Manager pattern orchestration, built-in tracing |
| **MCP SDK** | FastMCP + MCP Python SDK | Latest | Decorator-based tool/resource registration |
| **Conversational UI** | ChatKit Python SDK | Latest | Session management, response streaming |
| **Speech-to-Text** | OpenAI Whisper API | turbo model | Low latency, high accuracy |
| **Text-to-Speech** | OpenAI TTS API | gpt-4o-mini-tts | Newest model, realtime-optimized |
| **Language Detection** | GPT-4 (structured output) | gpt-4-turbo | High accuracy for short conversational text |
| **Translation** | GPT-4 | gpt-4-turbo | Multi-language support, context-aware |
| **Intent Classification** | GPT-4 (structured output) | gpt-4-turbo | CRUD intent extraction with confidence |
| **Database** | SQLite 3 | Built-in Python | Local storage, MCP resource exposure |
| **Audio I/O** | sounddevice + playsound | Latest | Microphone capture and audio playback |
| **Testing** | pytest + jsonschema + pytest-mock | Latest | Contract, integration, unit testing |
| **Python Version** | 3.11+ | 3.11.x | Required for OpenAI Agents SDK compatibility |

---

## Unknowns Resolved

All "NEEDS CLARIFICATION" items from plan.md Technical Context have been resolved:

✅ **Language/Version**: Python 3.11+ confirmed
✅ **Primary Dependencies**: OpenAI Agents SDK, FastMCP, ChatKit Python SDK confirmed
✅ **Storage**: SQLite with MCP resource exposure confirmed
✅ **Testing**: pytest with contract/integration/unit layers confirmed
✅ **Target Platform**: Cross-platform console confirmed
✅ **Performance Goals**: Validated against Whisper API and TTS API latencies
✅ **Constraints**: Internet required for services, graceful degradation strategy defined
✅ **Scale/Scope**: 7 languages confirmed feasible with GPT-4

---

## Next Steps

Phase 0 research complete. Proceed to **Phase 1: Design & Contracts** to generate:
1. `data-model.md` - Entity schemas (Task, ConversationContext, UserPreferences)
2. `contracts/` - MCP tool/resource JSON schemas for all agents
3. `quickstart.md` - Setup and run instructions
4. Update agent context with technologies from this research

---

**Sources**:
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Orchestrating multiple agents - OpenAI Agents SDK](https://openai.github.io/openai-agents-python/multi_agent/)
- [GitHub - modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- [GitHub - jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- [ChatKit | OpenAI API](https://platform.openai.com/docs/guides/chatkit)
- [Chatkit Python SDK](https://openai.github.io/chatkit-python/)
- [5 Ways to Speed Up Whisper Transcription](https://modal.com/blog/faster-transcription)
- [GitHub - SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [Text to speech | OpenAI API](https://platform.openai.com/docs/guides/text-to-speech)
- [mcp-server-sqlite · PyPI](https://pypi.org/project/mcp-server-sqlite/)
- [Breaking Isolation: A Practical Guide to Building an MCP Server with SQLite](https://felix-pappe.medium.com/breaking-isolation-a-practical-guide-to-building-an-mcp-server-with-sqlite-68c800a25d42)
