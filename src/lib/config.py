"""Configuration loader for environment variables."""

import os
from dotenv import load_dotenv


class Config:
    """Configuration settings loaded from environment variables."""

    def __init__(self):
        """Load configuration from .env file."""
        load_dotenv()

        # OpenAI API Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')
        self.whisper_model = os.getenv('WHISPER_MODEL', 'whisper-1')
        self.tts_model = os.getenv('TTS_MODEL', 'gpt-4o-mini-tts')
        self.tts_voice = os.getenv('TTS_VOICE', 'coral')

        # Database Configuration
        self.database_path = os.getenv('DATABASE_PATH', 'data/tasks.db')
        self.preferences_path = os.getenv('PREFERENCES_PATH', 'data/preferences.json')

        # Logging Configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/chatbot.log')

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate required configuration settings.

        Returns:
            (is_valid, errors): Tuple with validation result and list of error messages
        """
        errors = []

        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required in .env file")

        if not self.openai_api_key.startswith('sk-'):
            errors.append("OPENAI_API_KEY must start with 'sk-'")

        return len(errors) == 0, errors


# Global configuration instance
config = Config()
