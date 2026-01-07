from openai import OpenAI
from src.lib.config import config
from src.lib.logging_config import setup_logging

logger = setup_logging()

class TranslationService:
    """
    Handles translation of text using OpenAI.
    """

    def __init__(self):
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model = "gpt-4-turbo-preview"  # Or gpt-3.5-turbo for speed/cost

    def translate(self, text: str, target_lang: str) -> str:
        """
        Translates text to the target language.
        
        Args:
            text: The text to translate.
            target_lang: The target language code (e.g., 'es', 'fr', 'ur').
            
        Returns:
            Translated text.
        """
        if not text or not target_lang or target_lang.lower() == 'en':
            return text

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a helpful translator. Translate the following text to {target_lang}. Return ONLY the translated text, no quotes or explanations."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Fallback to original text
