# 🎤 Jarvis Voice Assistant - Quick Start

## 1-Minute Setup

### Prerequisites
- ✅ env_v1 virtual environment (already set up)
- ✅ Ollama installed and model downloaded

### Get Started

**Terminal 1 - Start Ollama:**
```powershell
ollama run llama3.2:3b-instruct-q4_K_M
```

**Terminal 2 - Activate and Run:**
```powershell
cd c:\Users\purus\codebase\voice_assitant_offline
..\env_v1\Scripts\Activate
python diagnose.py          # Run once to verify everything works
python run_assistant.py     # Start the voice assistant!
```

## Usage

The assistant works like this:

1. **Say:** "Hey Jarvis" (wake word)
2. **Speak:** Your question or command
3. **Wait:** It stops recording after silence
4. **Listen:** Jarvis responds with audio

Example:
```
Say: "Hey Jarvis"
     ↓ (wake word detected)
Say: "What is the capital of France?"
     ↓ (stops recording after 1 sec silence)
Listen: "The capital of France is Paris"
```

## Files Overview

| File | Purpose |
|------|---------|
| `run_assistant.py` | Main assistant - run this! |
| `diagnose.py` | Test all components before running |
| `text_to_audio.py` | Convert text to MP3 (standalone utility) |
| `audio_to_text.py` | Convert audio to text (standalone utility) |
| `main.py` | Alternative complete pipeline |
| `VOICE_ASSISTANT_README.md` | Full documentation |
| `IMPLEMENTATION_SUMMARY.md` | Technical details |

## Quick Troubleshooting

```powershell
# Check if everything is working
python diagnose.py

# No Ollama connection?
# → Make sure "ollama run llama3.2:3b-instruct-q4_K_M" is running in Terminal 1

# No audio input/output?
# → Check Windows Sound Settings

# Module not found?
# → Make sure to activate: ..\env_v1\Scripts\Activate

# Want to test text-to-audio?
python text_to_audio.py "Hello world" --output test.mp3
```

## Configuration

Change the AI model in `llm.py`:
```python
MODEL = "phi3:mini"              # Fastest response (recommended for testing)
MODEL = "llama3.2:3b"            # Default (good balance)
MODEL = "llama3-70b"             # Best quality (slow, needs GPU)
```

## Tips

- 🎤 Speak clearly near your microphone
- 🔊 Use headphones for better mic input quality  
- ⏱️ The assistant stops recording after ~1 second of silence
- 🚀 Use `phi3:mini` for fastest responses
- 💾 Check `output.mp3` for the last generated speech file

---

**Need help?** Read `VOICE_ASSISTANT_README.md` for detailed documentation.
