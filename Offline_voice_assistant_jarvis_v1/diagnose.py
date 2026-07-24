#!/usr/bin/env python3
"""
Diagnostic script to verify all voice assistant components are working.
Run this before starting the full assistant.
"""

import sys
from pathlib import Path


def check_imports():
    """Verify all required packages are installed."""
    print("\n" + "=" * 60)
    print("🔍 Checking Python Imports...")
    print("=" * 60)
    
    required_modules = {
        "numpy": "NumPy",
        "pyaudio": "PyAudio",
        "faster_whisper": "Faster Whisper",
        "requests": "Requests",
        "gtts": "Google Text-to-Speech",
        "webrtcvad": "WebRTC VAD",
    }
    
    missing = []
    for module, name in required_modules.items():
        try:
            __import__(module)
            print(f"  ✅ {name:30} - Installed")
        except ImportError:
            print(f"  ❌ {name:30} - NOT FOUND")
            missing.append(module)
    
    return len(missing) == 0


def check_local_modules():
    """Verify all local Python modules exist."""
    print("\n" + "=" * 60)
    print("📁 Checking Local Modules...")
    print("=" * 60)
    
    modules = {
        "wake_word.py": "Wake Word Detection",
        "vad_record.py": "Speech Recording",
        "stt.py": "Speech-to-Text",
        "llm.py": "LLM Integration",
        "tts_engine.py": "Text-to-Speech Engine",
        "audio_to_text.py": "Audio-to-Text Utility",
        "text_to_audio.py": "Text-to-Audio Utility",
        "main.py": "Main Assistant",
        "run_assistant.py": "Assistant Runner",
    }
    
    missing = []
    for filename, name in modules.items():
        if Path(filename).exists():
            print(f"  ✅ {name:30} - Found")
        else:
            print(f"  ❌ {name:30} - NOT FOUND")
            missing.append(filename)
    
    return len(missing) == 0


def check_ollama():
    """Check if Ollama server is running."""
    print("\n" + "=" * 60)
    print("🤖 Checking Ollama Server...")
    print("=" * 60)
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("  ✅ Ollama Server is running on http://localhost:11434")
            try:
                models = response.json().get("models", [])
                if models:
                    print(f"  ✅ Found {len(models)} installed model(s):")
                    for model in models:
                        print(f"     - {model.get('name', 'Unknown')}")
                    return True
                else:
                    print("  ⚠️  No models found. Run: ollama pull llama3.2:3b-instruct-q4_K_M")
                    return False
            except:
                return True
        else:
            print("  ❌ Ollama server returned unexpected response")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Ollama server is NOT running")
        print("     Start Ollama with: ollama run llama3.2:3b-instruct-q4_K_M")
        return False
    except Exception as e:
        print(f"  ⚠️  Error checking Ollama: {e}")
        return False


def check_audio_devices():
    """Check if audio devices are accessible."""
    print("\n" + "=" * 60)
    print("🎤 Checking Audio Devices...")
    print("=" * 60)
    
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        device_count = pa.get_device_count()
        if device_count > 0:
            print(f"  ✅ Found {device_count} audio device(s)")
            default_input = pa.get_default_input_device_info()
            default_output = pa.get_default_output_device_info()
            print(f"     Default Input:  {default_input['name']}")
            print(f"     Default Output: {default_output['name']}")
            pa.terminate()
            return True
        else:
            print("  ❌ No audio devices found")
            return False
    except Exception as e:
        print(f"  ❌ Error checking audio: {e}")
        return False


def run_quick_tests():
    """Run quick functional tests."""
    print("\n" + "=" * 60)
    print("⚡ Running Quick Functional Tests...")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Text-to-Audio conversion
    print("\n[1] Testing text-to-audio (gTTS)...")
    tests_total += 1
    try:
        from gtts import gTTS
        import tempfile
        import os
        
        temp_file = os.path.join(tempfile.gettempdir(), "test_tts.mp3")
        tts = gTTS(text="Test", lang="en")
        tts.save(temp_file)
        if os.path.exists(temp_file):
            print("    ✅ gTTS working correctly")
            tests_passed += 1
            os.remove(temp_file)
        else:
            print("    ❌ gTTS failed to create audio file")
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    # Test 2: Faster Whisper model loading
    print("\n[2] Testing Faster Whisper model loading...")
    tests_total += 1
    try:
        from faster_whisper import WhisperModel
        print("    ⏳ Loading tiny model (first time may take a moment)...")
        model = WhisperModel("tiny")
        print("    ✅ Whisper model loaded successfully")
        tests_passed += 1
    except Exception as e:
        print(f"    ❌ Error loading Whisper: {e}")
    
    # Test 3: PyAudio stream
    print("\n[3] Testing PyAudio stream...")
    tests_total += 1
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024,
        )
        stream.close()
        pa.terminate()
        print("    ✅ PyAudio stream created successfully")
        tests_passed += 1
    except Exception as e:
        print(f"    ❌ Error creating audio stream: {e}")
    
    print(f"\n✨ Tests passed: {tests_passed}/{tests_total}")
    return tests_passed == tests_total


def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🎤 Voice Assistant Diagnostic Tool  ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    checks = [
        ("Imports", check_imports),
        ("Local Modules", check_local_modules),
        ("Audio Devices", check_audio_devices),
        ("Ollama Server", check_ollama),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Error during {name} check: {e}")
            results[name] = False
    
    # Run quick tests
    try:
        run_quick_tests()
    except Exception as e:
        print(f"\n⚠️  Skipping quick tests: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Diagnostic Summary")
    print("=" * 60)
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check_name:20} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✨ All checks passed! Ready to run the voice assistant.")
        print("\nStart with:")
        print("  python run_assistant.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Ensure env_v1 is activated: ..\env_v1\Scripts\Activate")
        print("  2. Start Ollama: ollama run llama3.2:3b-instruct-q4_K_M")
        print("  3. Check microphone in Windows Sound Settings")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
