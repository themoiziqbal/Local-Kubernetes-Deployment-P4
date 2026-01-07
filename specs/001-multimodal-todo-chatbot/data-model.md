# Data Model: AI-Powered Multilingual Voice-Enabled Todo Chatbot

**Date**: 2025-12-13
**Feature Branch**: `001-multimodal-todo-chatbot`
**Phase**: 1 (Design & Contracts)

## Purpose

This document defines the entity schemas for the AI-Powered Multilingual Voice-Enabled Todo Chatbot. All entities are designed to support the feature requirements specified in [spec.md](./spec.md) and align with the architectural decisions in [research.md](./research.md).

---

## Entity 1: Task

**Purpose**: Represents a todo item with description, optional metadata (due date, priority, status, tags), and audit timestamps.

**Storage**: SQLite database (`data/tasks.db`)

**Schema**:

```python
@dataclass
class Task:
    """
    Represents a single todo task with optional metadata.

    Attributes:
        id: Unique identifier (auto-generated)
        description: Human-readable task description (required)
        due_date: Optional deadline in ISO 8601 format (YYYY-MM-DD HH:MM:SS)
        priority: Optional priority level (low, medium, high)
        status: Current task status (pending, in-progress, completed)
        tags: Optional list of string labels for categorization
        created_at: Timestamp when task was created (auto-generated)
        updated_at: Timestamp of last modification (auto-updated)
    """
    id: int
    description: str
    due_date: Optional[datetime] = None
    priority: Optional[Literal['low', 'medium', 'high']] = None
    status: Literal['pending', 'in-progress', 'completed'] = 'pending'
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'status': self.status,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @staticmethod
    def from_dict(data: dict) -> 'Task':
        """Create task from dictionary (e.g., from database row)."""
        return Task(
            id=data['id'],
            description=data['description'],
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            priority=data.get('priority'),
            status=data.get('status', 'pending'),
            tags=json.loads(data.get('tags', '[]')),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )
```

**SQLite Table Schema**:

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    due_date TEXT,  -- ISO 8601: YYYY-MM-DD HH:MM:SS
    priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
    status TEXT CHECK(status IN ('pending', 'in-progress', 'completed')) DEFAULT 'pending',
    tags TEXT,  -- JSON array stored as text: '["work", "urgent"]'
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Index for common queries
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority);

-- Trigger to auto-update updated_at timestamp
CREATE TRIGGER update_task_timestamp
AFTER UPDATE ON tasks
FOR EACH ROW
BEGIN
    UPDATE tasks SET updated_at = datetime('now') WHERE id = OLD.id;
END;
```

**Validation Rules** (from FR-019):
- `description`: Must be non-empty string (1-500 characters)
- `due_date`: Must be valid ISO 8601 datetime if provided; cannot be in the past when creating new task
- `priority`: Must be one of: 'low', 'medium', 'high' (or null)
- `status`: Must be one of: 'pending', 'in-progress', 'completed'
- `tags`: Must be valid JSON array of strings

**State Transitions** (status field):
- `pending` → `in-progress` (user starts working on task)
- `pending` → `completed` (user completes task directly)
- `in-progress` → `completed` (user finishes task)
- `completed` → `pending` (user reopens task)

---

## Entity 2: ConversationContext

**Purpose**: Maintains conversation state across user-system exchanges to enable context-aware interactions (User Story 5: Conversational Context Awareness).

**Storage**: In-memory (ephemeral, not persisted to database)

**Schema**:

```python
@dataclass
class Exchange:
    """Single user-system exchange in conversation."""
    user_input: str
    system_response: str
    timestamp: datetime = field(default_factory=datetime.now)
    language: str = 'en'  # ISO 639-1 language code

@dataclass
class ConversationContext:
    """
    Maintains conversation state for context-aware interactions.

    Attributes:
        exchanges: Recent conversation history (last 5 exchanges max)
        referenced_tasks: Tasks mentioned in recent conversation (by ID)
        detected_language: Current detected language of user input (ISO 639-1)
        voice_mode_enabled: Whether voice input/output is active
        pending_confirmation: Optional pending action awaiting user confirmation
    """
    exchanges: List[Exchange] = field(default_factory=list)
    referenced_tasks: List[int] = field(default_factory=list)
    detected_language: str = 'en'
    voice_mode_enabled: bool = False
    pending_confirmation: Optional[dict] = None  # e.g., {'action': 'delete', 'task_id': 5}

    def add_exchange(self, user_input: str, system_response: str, language: str = 'en'):
        """Add new exchange and maintain rolling window of last 5."""
        self.exchanges.append(Exchange(
            user_input=user_input,
            system_response=system_response,
            language=language
        ))
        # Keep only last 5 exchanges (FR-014)
        if len(self.exchanges) > 5:
            self.exchanges = self.exchanges[-5:]

    def add_referenced_task(self, task_id: int):
        """Track task referenced in conversation for implicit references."""
        if task_id not in self.referenced_tasks:
            self.referenced_tasks.append(task_id)
        # Keep only last 3 referenced tasks
        if len(self.referenced_tasks) > 3:
            self.referenced_tasks = self.referenced_tasks[-3:]

    def get_last_referenced_task(self) -> Optional[int]:
        """Get most recently referenced task ID (for 'it', 'that task', etc.)."""
        return self.referenced_tasks[-1] if self.referenced_tasks else None

    def clear_pending_confirmation(self):
        """Clear pending confirmation after user responds."""
        self.pending_confirmation = None

    def to_dict(self) -> dict:
        """Serialize context for session persistence (optional future feature)."""
        return {
            'exchanges': [
                {
                    'user_input': ex.user_input,
                    'system_response': ex.system_response,
                    'timestamp': ex.timestamp.isoformat(),
                    'language': ex.language
                }
                for ex in self.exchanges
            ],
            'referenced_tasks': self.referenced_tasks,
            'detected_language': self.detected_language,
            'voice_mode_enabled': self.voice_mode_enabled,
            'pending_confirmation': self.pending_confirmation
        }
```

**Constraints**:
- Maximum 5 exchanges retained (FR-014)
- Maximum 3 referenced tasks retained (recency-based)
- Exchanges pruned in FIFO order (oldest removed first)

---

## Entity 3: UserPreferences

**Purpose**: Stores user settings for language, voice input/output, and display format preferences.

**Storage**: SQLite database (`data/tasks.db`) OR JSON file (`data/preferences.json`) - single user, so simple persistence acceptable

**Schema**:

```python
@dataclass
class UserPreferences:
    """
    User configuration settings.

    Attributes:
        preferred_language: Explicit language preference (overrides auto-detection if set)
        voice_input_enabled: Whether microphone input is active
        voice_output_enabled: Whether TTS audio output is active
        display_format: Task list display format (simple, detailed, compact)
        tts_voice: Selected TTS voice (coral, alloy, echo, etc.)
    """
    preferred_language: Optional[str] = None  # ISO 639-1 code or null (auto-detect)
    voice_input_enabled: bool = False
    voice_output_enabled: bool = False
    display_format: Literal['simple', 'detailed', 'compact'] = 'simple'
    tts_voice: str = 'coral'  # OpenAI TTS voice name

    def to_dict(self) -> dict:
        """Serialize preferences for storage."""
        return {
            'preferred_language': self.preferred_language,
            'voice_input_enabled': self.voice_input_enabled,
            'voice_output_enabled': self.voice_output_enabled,
            'display_format': self.display_format,
            'tts_voice': self.tts_voice
        }

    @staticmethod
    def from_dict(data: dict) -> 'UserPreferences':
        """Load preferences from stored dictionary."""
        return UserPreferences(
            preferred_language=data.get('preferred_language'),
            voice_input_enabled=data.get('voice_input_enabled', False),
            voice_output_enabled=data.get('voice_output_enabled', False),
            display_format=data.get('display_format', 'simple'),
            tts_voice=data.get('tts_voice', 'coral')
        )

    @staticmethod
    def load_from_file(filepath: str = 'data/preferences.json') -> 'UserPreferences':
        """Load preferences from JSON file (or return defaults if not exists)."""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return UserPreferences.from_dict(json.load(f))
        return UserPreferences()  # Return defaults

    def save_to_file(self, filepath: str = 'data/preferences.json'):
        """Persist preferences to JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
```

**Storage Decision**: Use JSON file for simplicity (single-user app, infrequent writes). SQLite table alternative:

```sql
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Singleton table (max 1 row)
    preferred_language TEXT,
    voice_input_enabled INTEGER DEFAULT 0,
    voice_output_enabled INTEGER DEFAULT 0,
    display_format TEXT DEFAULT 'simple',
    tts_voice TEXT DEFAULT 'coral'
);

INSERT INTO user_preferences (id) VALUES (1);  -- Initialize with defaults
```

---

## Entity Relationships

```
UserPreferences (1) ─── (influences) ─── ConversationContext (1)
                                               │
                                               │ (references)
                                               │
                                               ▼
                                         Tasks (0..N)
```

**Relationships**:
- **UserPreferences → ConversationContext**: Preferences influence language detection and voice mode
- **ConversationContext → Tasks**: Context tracks recently referenced task IDs for implicit references

**Notes**:
- No foreign key constraints between entities (loose coupling)
- ConversationContext is ephemeral (not persisted across sessions initially)
- UserPreferences persisted to allow settings to survive app restarts

---

## Data Flow Summary

1. **Task Creation Flow**: User input → Intent Classifier → Task Add Agent → Create Task in SQLite → Update ConversationContext with new task ID
2. **Task Read Flow**: User input → Intent Classifier → Task Read Agent → Query SQLite → Format response based on UserPreferences.display_format
3. **Task Update/Patch Flow**: User input → Intent Classifier → Resolve task ID (explicit or from ConversationContext.referenced_tasks) → Task Update/Patch Agent → Update SQLite → Update ConversationContext
4. **Task Delete Flow**: User input → Intent Classifier → Resolve task ID → Set ConversationContext.pending_confirmation → Ask user confirmation → Delete from SQLite
5. **Language Detection Flow**: User input → Language Detector Agent → Update ConversationContext.detected_language → Use for translation

---

## Validation Summary

| Field | Constraint | Error Handling |
|-------|-----------|----------------|
| Task.description | Non-empty, 1-500 chars | Ask "What task would you like to add?" (FR-018) |
| Task.due_date | Valid ISO 8601, not in past | Return "Due date must be in the future" |
| Task.priority | 'low'/'medium'/'high'/null | Return "Priority must be low, medium, or high" |
| Task.status | 'pending'/'in-progress'/'completed' | Internal validation (user-friendly names) |
| Task.tags | Valid JSON array | Parse and validate before save |
| ConversationContext.exchanges | Max 5 | Auto-prune oldest |
| ConversationContext.referenced_tasks | Max 3 | Auto-prune oldest |
| UserPreferences.preferred_language | ISO 639-1 or null | Validate against supported set (en, es, fr, zh, ar, hi, de) |
| UserPreferences.display_format | 'simple'/'detailed'/'compact' | Default to 'simple' if invalid |

---

## Implementation Notes

1. **Database Initialization**: Create tables and indexes on first run (see `src/services/task_repository.py`)
2. **Migrations**: For schema changes, use SQLite `ALTER TABLE` statements (track version in metadata table)
3. **Data Integrity**: Use SQLite CHECK constraints and triggers to enforce validation at database level
4. **Serialization**: All entities provide `to_dict()` and `from_dict()` for JSON serialization (MCP resource protocol)
5. **Timestamps**: Use ISO 8601 format for all datetime fields (timezone-naive, local time assumed)

---

## Next Steps

Proceed to **contracts/** generation: Create MCP tool/resource JSON schemas for all agents based on these entity definitions.
