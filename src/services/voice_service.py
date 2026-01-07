import os
import tempfile
import time
import speech_recognition as sr
from gtts import gTTS
from src.lib.logging_config import setup_logging

logger = setup_logging()

class VoiceService:
    """
    Handles Voice Input (STT) and Output (TTS).
    """

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self, lang: str = 'en') -> str:
        """
        Listens to microphone input and converts it to text.
        Args:
            lang: Language code for recognition (default 'en').
        Returns:
            The recognized text, or empty string if failed.
        """
        try:
            with sr.Microphone() as source:
                print("🎤 Listening... (Speak now)")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

            print("⏳ Processing voice...")
            # Use specified language or default to en-US
            # Map simple codes to full codes if necessary, but Google often handles 2-char
            text = self.recognizer.recognize_google(audio, language=lang)
            return text

        except sr.WaitTimeoutError:
            print("❌ No speech detected.")
            return ""
        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
            return ""
        except sr.RequestError as e:
            logger.error(f"Could not request results from Speech Recognition service; {e}")
            print("❌ Voice service error.")
            return ""
        except Exception as e:
            logger.error(f"Voice input error: {e}")
            print(f"❌ Error: {e}")
            return ""

    def speak(self, text: str, lang: str = 'en'):
        """
        Converts text to speech and plays it.
        Args:
            text: The text to speak.
            lang: Language code (default 'en').
        """
        try:
            if not text:
                return

            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_filename = fp.name

            # Generate speech
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_filename)

            # Play audio - using Windows-compatible approach
            if os.name == 'nt':  # Windows
                os.startfile(temp_filename)
            else:
                # Linux/Mac fallback (aplay/afplay)
                os.system(f"afplay {temp_filename}" if os.name == 'posix' else f"aplay {temp_filename}")
                
                # Give it time to play since startfile is async
                # Estimate duration? No, just wait a bit or let it play in bg
                time.sleep(len(text) / 10)  # Rough estimate


        except Exception as e:
            logger.error(f"Voice output error: {e}")
            print(f"❌ Error playing audio: {e}")

        finally:
            # Clean up temp file
            try:
                if 'temp_filename' in locals() and os.path.exists(temp_filename):
                    os.remove(temp_filename)
            except Exception:
                pass
