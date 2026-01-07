"""Task entity model for todo items."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional


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
            tags=json.loads(data.get('tags', '[]')) if isinstance(data.get('tags'), str) else data.get('tags', []),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at', datetime.now()),
            updated_at=datetime.fromisoformat(data['updated_at']) if isinstance(data.get('updated_at'), str) else data.get('updated_at', datetime.now())
        )

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate task data.

        Returns:
            (is_valid, error_message): Tuple with validation result and optional error message
        """
        # Validate description
        if not self.description or len(self.description.strip()) == 0:
            return False, "Description cannot be empty"
        if len(self.description) > 500:
            return False, "Description cannot exceed 500 characters"

        # Validate due_date
        if self.due_date and self.due_date < datetime.now():
            return False, "Due date must be in the future"

        # Validate priority
        if self.priority and self.priority not in ['low', 'medium', 'high']:
            return False, "Priority must be low, medium, or high"

        # Validate status
        if self.status not in ['pending', 'in-progress', 'completed']:
            return False, "Status must be pending, in-progress, or completed"

        return True, None
