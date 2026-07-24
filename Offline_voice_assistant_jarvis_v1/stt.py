import os
import tempfile
import wave

from faster_whisper import WhisperModel

# Use CUDA for faster inference if available
model = WhisperModel("base", device="cuda", compute_type="float16")


def speech_to_text(audio_bytes):
    if not audio_bytes:
        return ""

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        temp_path = tmp_file.name

    try:
        with wave.open(temp_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_bytes)

        segments, _ = model.transcribe(temp_path, vad_filter=False)
        text = " ".join([seg.text for seg in segments]).strip()
        return text if text else ""
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
