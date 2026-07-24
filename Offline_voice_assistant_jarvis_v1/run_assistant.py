#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Complete Pipeline
Detects wake word -> Records speech -> Converts to text -> Gets LLM response -> Converts back to audio
"""

from wake_word import wait_for_wake_word
from vad_record import record_speech
from stt import speech_to_text
from llm import query_ollama
from tts_engine import speak_with_interrupt


def main():
    print("=" * 60)
    print("🤖 Jarvis Voice Assistant Initialized")
    print("=" * 60)
    print("\nStarting voice assistant pipeline...")
    print("Waiting for wake word: 'Hey Jarvis'\n")
    
    try:
        while True:
            # Step 1: Wait for wake word
            print("\n[1/5] Listening for wake word...")
            wait_for_wake_word()
            
            # Step 2: Record speech until silence
            print("[2/5] Recording your speech...")
            audio_data = record_speech()
            
            # Step 3: Convert speech to text
            print("[3/5] Converting speech to text...")
            user_text = speech_to_text(audio_data)
            print(f"You: {user_text}")
            
            # Step 4: Get response from LLM
            print("[4/5] Processing with AI...")
            response = query_ollama(user_text)
            
            # Step 5: Convert response to speech
            print("[5/5] Converting response to speech...")
            speak_with_interrupt(response)
            
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Jarvis...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
