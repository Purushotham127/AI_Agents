# Voice Assistant - Complete Pipeline Implementation

## Summary of Changes

This document outlines all modifications made to enable a complete offline voice assistant with the following pipeline:

```
[Wake Word Detection] → [Speech Recording] → [Speech-to-Text] → [LLM Processing] → [Text-to-Speech] → [Audio Output]
```

---

## Files Modified

### 1. **tts_engine.py** (Major Refactor)
**Before:** Used RealtimeTTS with webrtcvad interrupt detection
**After:** Simplified to use gTTS (Google Text-to-Speech) directly

**Changes:**
- Removed dependency on `RealtimeTTS` and `webrtcvad` threading
- Uses `gtts` library for speech synthesis
- Outputs MP3 files and plays via system default player
- Removed complex interrupt listening mechanism

**Key Functions:**
- `speak(text, lang="en")` - Generates and plays speech
- `speak_with_interrupt(text, lang="en")` - Alias for speak() with simplified interface

---

### 2. **llm.py** (Bug Fix)
**Before:** `MODEL = "ollama run llama3.2:3b-instruct-q4_K_M"`
**After:** `MODEL = "llama3.2:3b-instruct-q4_K_M"`

**Reason:** Removed incorrect "ollama run" prefix from model name

---

## Files Created

### 3. **run_assistant.py** (New)
Complete voice assistant pipeline with step-by-step execution:
1. Listens for wake word ("Hey Jarvis")
2. Records speech until silence detected
3. Converts speech to text
4. Queries Ollama LLM for response
5. Converts response back to audio
6. Plays the audio response

**Usage:**
```powershell
python run_assistant.py
```

---

### 4. **text_to_audio.py** (New - Utility Script)
Standalone script for converting text to audio files.

**Usage:**
```powershell
python text_to_audio.py "Hello world" --output greeting.mp3
python text_to_audio.py "Hola mundo" --output saludo.mp3 --lang es
```

**Features:**
- Supports multiple languages
- Outputs MP3 files
- No ffmpeg required (unlike original SystemEngine approach)

---

### 5. **VOICE_ASSISTANT_README.md** (New - Documentation)
Comprehensive guide including:
- Overview of the pipeline
- Prerequisites and setup instructions
- How to run the assistant (3 different ways)
- Configuration options
- Troubleshooting guide
- Pipeline component reference
- Performance optimization tips

---

### 6. **diagnose.py** (New - Diagnostic Tool)
Pre-flight check utility that verifies:
- ✅ All Python imports are available
- ✅ Local module files exist
- ✅ Audio devices are accessible
- ✅ Ollama server is running with models
- ✅ Quick functional tests (gTTS, Whisper, PyAudio)

**Usage:**
```powershell
python diagnose.py
```

---

## Unchanged Files (Already Functional)

These files remain unchanged as they already work with the env_v1 environment:

### **wake_word.py**
- Detects "Hey Jarvis" wake phrase
- Uses Faster Whisper (tiny model)
- Requires webrtcvad (already in env_v1)

### **vad_record.py**
- Records audio until silence detected
- Uses webrtcvad for Voice Activity Detection
- Records at 16kHz with 480-byte chunks

### **stt.py**
- Converts audio bytes to text
- Uses Faster Whisper (base model)
- No changes needed

### **main.py**
- Original complete pipeline script
- Works without modification
- Alternative to run_assistant.py

---

## Dependencies & Installation

### Required Packages (Already in env_v1)
```
numpy
pyaudio
faster-whisper
requests
webrtcvad
```

### New Package Added
```
gtts  # Google Text-to-Speech (installed for tts_engine.py)
```

### Install if missing:
```powershell
& ..\env_v1\Scripts\Activate
pip install gtts pyttsx3  # pyttsx3 was installed for earlier attempts but not used
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Voice Assistant Pipeline                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  wake_word.py           Record         stt.py              │
│  (Faster-Whisper)  →   (webrtcvad)  →  (Faster-Whisper)   │
│  Detect "Hey Jarvis"    Until Silence   Convert to Text     │
│         ↓                  ↓                 ↓              │
│  ┌──────────────────────────────────────────┐             │
│  │         run_assistant.py (Orchestrator)  │             │
│  └──────────────────────────────────────────┘             │
│         ↓                  ↓                 ↓              │
│  llm.py          tts_engine.py         System Player      │
│  (Ollama)        (Google TTS)          (MP3 Output)        │
│  Query LLM   →   Text → Audio      →  Play Response       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration Options

### Change LLM Model
Edit `llm.py`:
```python
MODEL = "phi3:mini"              # Fastest (3B)
MODEL = "llama3.2:3b"            # Balanced
MODEL = "llama3.2:7b"            # Better quality
MODEL = "llama3-70b"             # Best (requires GPU)
```

### Adjust Recording Sensitivity
Edit `vad_record.py`:
```python
if silence > 30:  # Increase for longer tolerance (30 = ~1 second)
    break
```

### Change TTS Language
Edit `tts_engine.py` or call with different language:
```python
speak(text, lang="es")  # Spanish
speak(text, lang="fr")  # French
speak(text, lang="de")  # German
```

---

## Running the Voice Assistant

### Option 1: Full Pipeline (Recommended)
```powershell
# Activate environment
..\env_v1\Scripts\Activate

# Run diagnostic first
python diagnose.py

# Start the assistant
python run_assistant.py
```

### Option 2: Original Main Script
```powershell
..\env_v1\Scripts\Activate
python main.py
```

### Option 3: Test Individual Components
```powershell
# Test wake word detection
python -c "from wake_word import wait_for_wake_word; wait_for_wake_word()"

# Test text-to-audio generation
python text_to_audio.py "Hello world" --output test.mp3

# Test with diagnostic tool
python diagnose.py
```

---

## Key Improvements

✅ **Simplified TTS Engine** - Removed complex RealtimeTTS dependency
✅ **No Build Issues** - Uses pure Python gTTS instead of C extensions
✅ **Better Error Handling** - Diagnostic tool catches issues early
✅ **Complete Documentation** - Clear setup and usage guides
✅ **Modular Design** - Each component can be tested independently
✅ **Offline Capable** - All components run locally except gTTS (which is cloud-based)

---

## Testing Checklist

Before running the full assistant, verify:

- [ ] Environment activated: `..\env_v1\Scripts\Activate`
- [ ] Ollama running: `ollama run llama3.2:3b-instruct-q4_K_M`
- [ ] Microphone working in Windows Sound Settings
- [ ] Speakers/headphones plugged in
- [ ] Diagnostic passes: `python diagnose.py`

---

## Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError" | Activate env_v1: `..\env_v1\Scripts\Activate` |
| "Ollama connection failed" | Start Ollama in separate terminal |
| "No audio input" | Check Windows Sound Settings → Input devices |
| "No audio output" | Check Windows Sound Settings → Output devices |
| "No wake word detected" | Speak clearly "Hey Jarvis" near microphone |
| "Slow responses" | Use faster model (phi3:mini) or add GPU |

---

## Next Steps for Enhancement

Possible improvements:
1. Add local VAD alternative to avoid webrtcvad build issues
2. Support multiple languages for wake word
3. Add local TTS option (PiperEngine instead of gTTS)
4. Implement context memory between conversations
5. Add custom command routing
6. Support GPU acceleration for Whisper

---

**Version:** 1.0
**Date:** 2026-06-23
**Status:** Ready for Testing
