from wake_word import wait_for_wake_word
from vad_record import record_speech
from stt import speech_to_text
from llm import query_ollama
from tts_engine import speak_with_interrupt

print("Jarvis Initialized...")

while True:
    wait_for_wake_word()

    audio = record_speech()
    user_text = speech_to_text(audio)
    print("User:", user_text)

    reply = query_ollama(user_text)
    print("Jarvis:", reply)

    speak_with_interrupt(reply)
