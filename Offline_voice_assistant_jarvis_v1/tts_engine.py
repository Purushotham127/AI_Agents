import os
import tempfile
from pathlib import Path
from gtts import gTTS
import subprocess
import sys


def speak(text: str, lang: str = "en") -> None:
    """
    Convert text to speech and play the audio using the default media player.
    """
    try:
        if not text or not text.strip():
            print("Jarvis: I didn't catch that.")
            text = "I didn't catch that."

        temp_dir = tempfile.gettempdir()
        audio_file = os.path.join(temp_dir, "jarvis_response.mp3")

        print(f"Jarvis: {text}")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(audio_file)

        if sys.platform == "win32":
            os.startfile(audio_file)
        elif sys.platform == "darwin":
            subprocess.run(["open", audio_file], check=False)
        else:
            subprocess.run(["xdg-open", audio_file], check=False)

    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        try:
            print("Falling back to console output.")
        except Exception:
            pass


def speak_with_interrupt(text: str, lang: str = "en") -> None:
    """
    Convert text to speech and play the audio.
    This version is simplified and doesn't require RealtimeTTS or webrtcvad.
    
    Args:
        text (str): The text to convert to speech
        lang (str): Language code (default: "en" for English)
    """
    speak(text, lang)
