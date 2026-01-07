"""Conversation context management for maintaining state across exchanges."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


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

    def reset(self):
        """Reset conversation context (clear history and references)."""
        self.exchanges = []
        self.referenced_tasks = []
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
