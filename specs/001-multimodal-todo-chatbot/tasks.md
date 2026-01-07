# Tasks: AI-Powered Multilingual Voice-Enabled Todo Chatbot

**Input**: Design documents from `/specs/001-multimodal-todo-chatbot/`
**Prerequisites**: plan.md (updated for web-first), spec.md (updated for web UI), ADR-0001
**Updated**: 2025-12-21 (Reflects architectural pivot from console to web)

**⚠️ IMPORTANT - ARCHITECTURAL PIVOT**: This task list was originally created for a console-first, agent-based architecture. The implementation pivoted to a web-first FastAPI architecture (see [ADR-0001](../../history/adr/0001-architectural-pivot-from-console-first-to-web-first-deployment.md)). The tasks below are preserved for historical reference, but many have been superseded by the web implementation.

**Current Implementation Status**:
- ✅ **MVP Deployed**: Web-based todo chatbot with basic CRUD operations (see `api/index.py`, `index.html`, `script.js`, `styles.css`)
- ✅ **Phase 0 Complete**: English text-based task management via web browser
- ⚠️ **Phase 1 Pending**: SQLite persistence, delete confirmation, multilingual support, conversation context
- ⚠️ **Phase 2 Pending**: Voice backend integration, advanced features

**Tests**: Tests are OPTIONAL per project guidelines (Constitution v2.0.0 Principle IX - MVP phase). Production deployment will require API contract tests and integration tests.

**Organization**: Tasks below are grouped by original user story plan. See [plan.md](./plan.md) for updated phased implementation approach.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single Python project: `src/`, `tests/` at repository root
- All paths shown use forward slashes (cross-platform compatible)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure (src/agents/, src/models/, src/services/, src/cli/, src/lib/, tests/, data/, config/, docs/)
- [X] T002 Initialize Python 3.11+ virtual environment and install base dependencies (openai-agents, mcp, fastmcp, openai, pytest)
- [X] T003 [P] Create config/.env.example template with OPENAI_API_KEY and configuration variables
- [X] T004 [P] Create .gitignore for Python project (venv/, data/, .env, logs/, __pycache__)
- [X] T005 [P] Create requirements.txt with all dependencies (openai-agents>=0.1.0, mcp>=1.7.0, fastmcp>=0.1.0, openai>=1.50.0, sounddevice>=0.4.6, playsound>=1.3.0, jsonschema>=4.20.0, pytest>=7.4.0, pytest-asyncio>=0.21.0, pytest-mock>=3.12.0, python-dotenv>=1.0.0)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create Task entity model in src/models/task.py with dataclass schema per data-model.md
- [X] T007 Create ConversationContext entity in src/models/conversation_context.py with Exchange dataclass
- [X] T008 Create UserPreferences entity in src/models/user_preferences.py with default values
- [X] T009 Create TaskRepository service in src/services/task_repository.py with SQLite database initialization (tasks table, indexes, triggers)
- [X] T010 Create MCP resource wrapper for SQLite task persistence in src/services/task_mcp_server.py (@server.resource() for task://list, task://get/{id}, task://schema)
- [X] T011 [P] Create MCP helpers utility module in src/lib/mcp_helpers.py for tool registration and resource exposure patterns
- [X] T012 [P] Create logging configuration in src/lib/logging_config.py with internal error tracking setup
- [X] T013 [P] Setup environment configuration loader in src/lib/config.py to read .env file and validate API keys
- [X] T014 Create database initialization script that runs on first startup (creates data/ directory, initializes tasks.db with schema, creates preferences.json)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Text-Based Task Management in English (Priority: P1) 🎯 MVP

**Goal**: Enable users to manage todo tasks via console using natural language English text commands (add, view, update, delete)

**Independent Test**: Launch console app, type "add a task to buy groceries", "show my tasks", "mark task 1 as done", verify tasks are created/displayed/managed without voice or translation features

### Implementation for User Story 1

- [X] T015 [P] [US1] Create Intent Classifier Agent in src/agents/intent_classifier_agent.py using GPT-4 structured output for CRUD classification
- [X] T016 [P] [US1] Create Task Add Agent in src/agents/task_agents/task_add_agent.py with MCP tool @agent.tool() decorator
- [X] T017 [P] [US1] Create Task Read Agent in src/agents/task_agents/task_read_agent.py with filtering/searching capabilities
- [X] T018 [P] [US1] Create Task Update Agent in src/agents/task_agents/task_update_agent.py for full task replacement
- [X] T019 [P] [US1] Create Task Delete Agent in src/agents/task_agents/task_delete_agent.py with confirmation workflow
- [ ] T020 [US1] Create Master Chat Agent in src/agents/master_chat_agent.py with Manager pattern orchestration (coordinates Intent Classifier and Task agents)
- [ ] T021 [US1] Implement conversation context management in Master Chat Agent (add_exchange, track referenced tasks)
- [ ] T022 [US1] Implement ChatKit console interface in src/cli/chatbot_cli.py with simple input/output loop
- [ ] T023 [US1] Add user input parsing and command routing in src/cli/chatbot_cli.py (handle /help, /exit commands)
- [ ] T024 [US1] Implement natural language response formatting for task confirmations in Master Chat Agent
- [ ] T025 [US1] Add clarifying question flow for ambiguous user input in Intent Classifier Agent
- [ ] T026 [US1] Implement error handling with user-friendly messages (wrap exceptions, return natural language errors)
- [ ] T027 [US1] Add task validation (non-empty description, valid priority, valid status) in Task Add Agent and Task Update Agent

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (English text-based todo management working)

---

## Phase 4: User Story 2 - Multilingual Text Support (Priority: P2)

**Goal**: Support natural language interaction in 7+ languages with automatic detection and translation

**Independent Test**: Type commands in Spanish ("añadir tarea comprar leche"), French, or other supported languages and verify system responds in the same language

### Implementation for User Story 2

- [ ] T028 [P] [US2] Create Language Detector Agent in src/agents/language_detector_agent.py using GPT-4 structured output (ISO 639-1 codes, confidence)
- [ ] T029 [P] [US2] Create Translator Agent in src/agents/translator_agent.py with bidirectional translation via GPT-4
- [ ] T030 [P] [US2] Create Translation Service wrapper in src/services/translation_service.py as MCP tool (@server.tool())
- [ ] T031 [US2] Integrate Language Detector into Master Chat Agent workflow (detect language before intent classification)
- [ ] T032 [US2] Add translation flow to Master Chat Agent (user language → English → processing → English → user language)
- [ ] T033 [US2] Update ConversationContext to store detected_language and cache language across exchanges
- [ ] T034 [US2] Implement language fallback handling (if confidence <0.7, ask user to clarify language preference)
- [ ] T035 [US2] Add support for 7 languages in Language Detector (en, es, fr, zh, ar, hi, de) with validation
- [ ] T036 [US2] Update ChatKit console interface to display language detection status (optional debug info)
- [ ] T037 [US2] Implement edge case handling for mixed-language input (clarification questions)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently (multilingual text todo management working)

---

## Phase 5: User Story 3 - Voice Input Mode (Priority: P3)

**Goal**: Enable hands-free voice commands using microphone with speech-to-text conversion

**Independent Test**: Click voice input button or command, speak "add a task to walk the dog", verify speech is transcribed and task operation executes with confirmation

### Implementation for User Story 3

- [ ] T038 [P] [US3] Create Voice Processor Agent in src/agents/voice_processor_agent.py for STT/TTS coordination
- [ ] T039 [P] [US3] Create Whisper Service wrapper in src/services/whisper_service.py as MCP tool for OpenAI Whisper API (STT)
- [ ] T040 [P] [US3] Create TTS Service wrapper in src/services/tts_service.py as MCP tool for OpenAI TTS API
- [ ] T041 [US3] Add microphone audio capture in Voice Processor Agent using sounddevice library
- [ ] T042 [US3] Implement Whisper API integration in Whisper Service (audio file upload, transcription retrieval)
- [ ] T043 [US3] Add voice mode toggle in ChatKit console interface (/voice on, /voice off commands)
- [ ] T044 [US3] Integrate Voice Processor into Master Chat Agent workflow (voice input → STT → text processing)
- [ ] T045 [US3] Implement TTS audio output in TTS Service (GPT-4o-mini-tts, WAV format, playsound playback)
- [ ] T046 [US3] Add voice output preference control in UserPreferences (voice_output_enabled flag)
- [ ] T047 [US3] Implement silence detection for voice input (2 second pause triggers processing)
- [ ] T048 [US3] Add voice input error handling (background noise, low confidence, permission denied)
- [ ] T049 [US3] Integrate voice input with multilingual flow (transcribe → detect language → translate → process)
- [ ] T050 [US3] Add optional voice output after text responses (read responses aloud if voice_output_enabled)
- [ ] T051 [US3] Implement audio format optimization (32 kbps, 12 kHz per research.md recommendations)

**Checkpoint**: All voice features working (can use voice OR text for all operations, responses can be spoken)

---

## Phase 6: User Story 4 - Partial Task Updates (Priority: P4)

**Goal**: Allow fine-grained task field updates without re-specifying entire task

**Independent Test**: Create task with multiple fields, issue "change the due date of task 2 to Friday" or "mark task 1 as high priority", verify only specified field changes

### Implementation for User Story 4

- [ ] T052 [P] [US4] Create Task Patch Agent in src/agents/task_agents/task_patch_agent.py for field-specific updates
- [ ] T053 [US4] Implement partial update intent detection in Intent Classifier Agent (distinguish PATCH from UPDATE)
- [ ] T054 [US4] Add field extraction logic in Task Patch Agent (parse which field(s) to modify)
- [ ] T055 [US4] Implement atomic field updates in TaskRepository (update only specified fields, preserve others)
- [ ] T056 [US4] Add validation for partial updates (e.g., cannot set invalid priority on patch)
- [ ] T057 [US4] Support multiple field patches in single command ("change description and priority of task 2")
- [ ] T058 [US4] Integrate Task Patch Agent into Master Chat Agent orchestration workflow
- [ ] T059 [US4] Add natural language confirmation messages for partial updates ("Task 2 due date updated to Friday")

**Checkpoint**: Partial updates working (can modify individual fields without affecting others)

---

## Phase 7: User Story 5 - Conversational Context Awareness (Priority: P5)

**Goal**: Maintain conversation context to understand implicit references and follow-up questions

**Independent Test**: Have conversation "show task 3", [system displays], "delete it", verify system understands "it" refers to task 3

### Implementation for User Story 5

- [ ] T060 [US5] Enhance ConversationContext to track referenced_tasks list (last 3 tasks mentioned)
- [ ] T061 [US5] Add implicit reference resolution in Master Chat Agent (resolve "it", "that task", "them")
- [ ] T062 [US5] Implement context-aware intent classification (use recent exchanges for disambiguation)
- [ ] T063 [US5] Add pronoun resolution logic in Intent Classifier ("delete it" → "delete task {last_referenced_id}")
- [ ] T064 [US5] Support batch operations from context ("mark them all as done" after listing tasks)
- [ ] T065 [US5] Implement pending_confirmation tracking in ConversationContext (e.g., delete confirmation awaiting response)
- [ ] T066 [US5] Add context timeout/reset logic (clear stale references after 5 exchanges per FR-014)
- [ ] T067 [US5] Handle ambiguous context with clarification questions ("Which task would you like to change?")
- [ ] T068 [US5] Add /clear command to manually reset conversation context
- [ ] T069 [US5] Update all task agents to populate referenced_tasks in context after operations

**Checkpoint**: All conversational context features working (can use implicit references, follow-up questions work naturally)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T070 [P] Create architecture documentation in docs/architecture.md with system flow diagrams
- [ ] T071 [P] Create agent registry documentation in docs/agent-registry.md listing all agents and their MCP contracts
- [ ] T072 [P] Add comprehensive logging for debugging (log all agent calls, API requests, errors)
- [ ] T073 [P] Implement graceful degradation for offline mode (detect internet unavailability, fall back to English text-only)
- [ ] T074 [P] Add /settings command to view and modify UserPreferences from console
- [ ] T075 [P] Add /language command to explicitly set preferred language
- [ ] T076 Add performance monitoring for latency goals (text <2s, voice <4s, log warnings if exceeded)
- [ ] T077 Add input validation across all agents (sanitize user input, prevent injection attacks)
- [ ] T078 Implement rate limiting for OpenAI API calls (prevent excessive costs)
- [ ] T079 Add startup validation (check .env file, API key validity, database initialization)
- [ ] T080 Create comprehensive error messages documentation (all error scenarios documented)
- [ ] T081 Add display format options in UserPreferences (simple, detailed, compact task list views)
- [ ] T082 Implement task filtering by priority, status, due date in Task Read Agent
- [ ] T083 Add task search by description keywords in Task Read Agent
- [ ] T084 Add timestamps to all console output (optional debug mode)
- [ ] T085 Create edge case handling documentation (all edge cases from spec.md tested and documented)
- [ ] T086 Run quickstart.md validation (follow setup instructions, verify all sample commands work)
- [ ] T087 Code cleanup and refactoring (remove TODOs, optimize imports, add docstrings)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 workflow but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1 and US2 workflows
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Adds to US1 update capabilities
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Enhances all previous stories with context awareness

### Within Each User Story

- Models before services
- Services before agents
- Agents before integration into Master Chat Agent
- Core implementation before edge case handling

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005)
- All Foundational tasks marked [P] can run in parallel (T011, T012, T013)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story, all tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- Polish tasks marked [P] can all run in parallel (T070-T075)

---

## Parallel Example: User Story 1

```bash
# Launch all agent creation tasks for User Story 1 together:
Task T015: "Create Intent Classifier Agent in src/agents/intent_classifier_agent.py"
Task T016: "Create Task Add Agent in src/agents/task_agents/task_add_agent.py"
Task T017: "Create Task Read Agent in src/agents/task_agents/task_read_agent.py"
Task T018: "Create Task Update Agent in src/agents/task_agents/task_update_agent.py"
Task T019: "Create Task Delete Agent in src/agents/task_agents/task_delete_agent.py"
# Then proceed to T020 (Master Chat Agent) which depends on these agents existing
```

## Parallel Example: User Story 2

```bash
# Launch all service creation tasks for User Story 2 together:
Task T028: "Create Language Detector Agent in src/agents/language_detector_agent.py"
Task T029: "Create Translator Agent in src/agents/translator_agent.py"
Task T030: "Create Translation Service wrapper in src/services/translation_service.py"
# Then proceed to integration tasks
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T014) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T015-T027)
4. **STOP and VALIDATE**: Test User Story 1 independently (English text-based todo management)
5. Deploy/demo if ready - working console chatbot with basic CRUD operations

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - English text todo chatbot!)
3. Add User Story 2 → Test independently → Deploy/Demo (Multilingual chatbot!)
4. Add User Story 3 → Test independently → Deploy/Demo (Voice-enabled chatbot!)
5. Add User Story 4 → Test independently → Deploy/Demo (Fine-grained updates!)
6. Add User Story 5 → Test independently → Deploy/Demo (Context-aware conversations!)
7. Polish → Final production-ready version

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T014)
2. Once Foundational is done:
   - Developer A: User Story 1 (T015-T027)
   - Developer B: User Story 2 (T028-T037) - starts in parallel
   - Developer C: User Story 3 (T038-T051) - starts in parallel
   - Developer D: User Story 4 (T052-T059) - starts in parallel
   - Developer E: User Story 5 (T060-T069) - starts in parallel
3. Stories complete and integrate independently
4. All developers: Polish phase together (T070-T087)

---

## Task Summary

**Total Tasks**: 87

**Tasks per Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 9 tasks (BLOCKS all user stories)
- Phase 3 (User Story 1 - P1): 13 tasks
- Phase 4 (User Story 2 - P2): 10 tasks
- Phase 5 (User Story 3 - P3): 14 tasks
- Phase 6 (User Story 4 - P4): 8 tasks
- Phase 7 (User Story 5 - P5): 10 tasks
- Phase 8 (Polish): 18 tasks

**Parallel Opportunities Identified**: 23 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Type English text commands for CRUD operations
- US2: Type commands in non-English languages (Spanish, French, etc.)
- US3: Use voice input for commands and receive voice/text output
- US4: Modify individual task fields without full updates
- US5: Use implicit references and follow-up questions

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 27 tasks
This delivers a working English text-based todo chatbot with all basic CRUD operations.

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are NOT included as they were not explicitly requested in feature specification
- All file paths use forward slashes for cross-platform compatibility
- Database (tasks.db) and preferences (preferences.json) auto-created on first run
- API keys required in .env file before running (see quickstart.md)
