# Voice Assistant Setup and Usage Guide

## Overview
This is a complete offline voice assistant pipeline that:
1. **Detects wake word** - Listens for "Hey Jarvis"
2. **Records speech** - Records audio until silence detected
3. **Converts to text** - Uses Whisper to transcribe speech
4. **Gets LLM response** - Queries Ollama for intelligent responses
5. **Converts to audio** - Uses Google TTS to speak the response

## Prerequisites

### 1. Environment Setup
Make sure you're using the `env_v1` virtual environment:
```powershell
..\env_v1\Scripts\Activate
```

### 2. Install Ollama
The assistant requires Ollama running locally with a model. Download from: https://ollama.ai

**Quick Start with Ollama:**
```powershell
# Pull and run a model (in a separate terminal)
ollama run llama3.2:3b-instruct-q4_K_M
# Or use a faster model:
ollama run phi3:mini
```

Ollama will start a server on `http://localhost:11434` (used by the assistant).

### 3. Verify Dependencies
All required packages should be in `env_v1`:
- `faster-whisper` - Speech-to-text
- `pyaudio` - Audio recording
- `requests` - Ollama API communication
- `gtts` - Google Text-to-Speech
- `webrtcvad` - Voice Activity Detection
- `numpy` - Audio processing

Check installation:
```powershell
pip list | findstr "whisper pyaudio requests gtts webrtcvad numpy"
```

## Running the Voice Assistant

### Option 1: Simple Pipeline (Recommended)
```powershell
python run_assistant.py
```

The assistant will:
1. Wait for "Hey Jarvis" (say this to activate)
2. Listen for your speech
3. Stop recording after 1-2 seconds of silence
4. Process and respond

### Option 2: Using Main Script
```powershell
python main.py
```

### Option 3: Test Individual Components

**Test wake word detection:**
```powershell
python -c "from wake_word import wait_for_wake_word; wait_for_wake_word()"
```

**Test speech recording:**
```powershell
python -c "from vad_record import record_speech; audio=record_speech(); print(f'Recorded {len(audio)} bytes')"
```

**Test text-to-audio (generate MP3):**
```powershell
python text_to_audio.py "Hello, I am Jarvis" --output test.mp3
```

**Test speech-to-text:**
```powershell
from stt import speech_to_text
# (requires audio_bytes from recording)
```

## Configuration

### Change LLM Model
Edit `llm.py`:
```python
MODEL = "phi3:mini"  # Faster but less capable
# or
MODEL = "llama3.2:3b-instruct-q4_K_M"  # Better quality
```

### Adjust Recording Silence Threshold
Edit `vad_record.py` - change the silence count (default: 30 chunks = ~1 sec):
```python
if silence > 30:  # Increase for longer silence tolerance
    break
```

### Change Language
Edit `tts_engine.py` - modify the `speak()` function call:
```python
speak(text, lang="es")  # Spanish
speak(text, lang="fr")  # French
```

## Troubleshooting

### "ModuleNotFoundError: webrtcvad"
The package is already in `env_v1`. Ensure you've activated the environment:
```powershell
..\env_v1\Scripts\Activate
```

### "ConnectionError: Failed to establish connection to Ollama"
Ollama server is not running. In a new terminal:
```powershell
ollama run llama3.2:3b-instruct-q4_K_M
```

### Audio issues or no sound
Make sure your default audio device is set correctly in Windows Sound Settings.

### "No module named 'faster_whisper'"
Reinstall the environment package:
```powershell
& ..\env_v1\Scripts\Activate
pip install faster-whisper
```

## Pipeline Components

| Module | Purpose | Requires |
|--------|---------|----------|
| `wake_word.py` | Detects "Hey Jarvis" | faster-whisper, pyaudio |
| `vad_record.py` | Records until silence | webrtcvad, pyaudio |
| `stt.py` | Speech to text | faster-whisper |
| `llm.py` | LLM query | requests, ollama (running) |
| `tts_engine.py` | Text to speech | gtts |
| `run_assistant.py` | Complete pipeline | All of the above |

## Tips for Better Performance

1. **Faster Response**: Use `phi3:mini` model instead of `llama3.2:3b`
2. **Better Quality**: Use GPU acceleration if available
3. **Cleaner Audio**: Reduce background noise
4. **Offline Mode**: All components run locally (except gTTS which needs internet)

## Example Interactions

```
🤖 Jarvis Voice Assistant Initialized
Waiting for wake word: 'Hey Jarvis'

[1/5] Listening for wake word...
Wake word detected

[2/5] Recording your speech...
Listening...

[3/5] Converting speech to text...
You: What is the weather today?

[4/5] Processing with AI...

[5/5] Converting response to speech...
Jarvis: I don't have real-time weather data, but you can check your weather app or ask a weather-enabled assistant.
```

## Support

For issues:
1. Check the error messages in the terminal
2. Verify Ollama is running
3. Test each component individually
4. Check your microphone and speaker settings
