"""User preferences entity for storing user settings."""

import json
import os
from dataclasses import dataclass
from typing import Literal, Optional


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
