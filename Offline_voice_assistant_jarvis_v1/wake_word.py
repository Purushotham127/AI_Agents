# Vosk-based wake word detection
import json
import os
import time
import urllib.request
import zipfile
import pyaudio
from vosk import KaldiRecognizer, Model

RATE = 16000
MODEL_NAME = "vosk-model-en-us-0.22"
MODEL_DIR = os.path.join(os.path.dirname(__file__), MODEL_NAME)
MODEL_URL = f"https://alphacephei.com/vosk/models/{MODEL_NAME}.zip"


def download_model():
    archive_path = os.path.join(os.path.dirname(__file__), f"{MODEL_NAME}.zip")

    print(f"Downloading Vosk model to {archive_path}...")
    urllib.request.urlretrieve(MODEL_URL, archive_path)

    print("Extracting Vosk model...")
    with zipfile.ZipFile(archive_path, "r") as archive:
        archive.extractall(os.path.dirname(__file__))

    os.remove(archive_path)
    print("Vosk model downloaded and extracted.")


if not os.path.exists(MODEL_DIR):
    try:
        download_model()
    except Exception as exc:
        raise SystemExit(
            "Vosk model download failed. Please download the model manually from "
            f"{MODEL_URL} and extract it to {MODEL_DIR}.\nError: {exc}"
        )

print(f"Using Vosk model: {MODEL_NAME}")
model = Model(MODEL_DIR)
recognizer = KaldiRecognizer(model, RATE)

pa = pyaudio.PyAudio()
stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    frames_per_buffer=4000,
)


def wait_for_wake_word():
    print("Listening for 'hey jarvis'...")
    heard_hey = False
    hey_timestamp = 0.0
    last_partial = ""

    while True:
        try:
            data = stream.read(4000, exception_on_overflow=False)
        except IOError as e:
            print(f"Audio read error: {e}")
            continue

        def handle_text(text: str, kind: str) -> bool:
            nonlocal heard_hey, hey_timestamp, last_partial
            normalized = text.lower().strip()
            if not normalized:
                return False
            if kind == "partial" and normalized == last_partial:
                return False
            if kind == "partial":
                last_partial = normalized
            print(f"[wake-word debug] {kind}: {normalized!r}")

            if "jarvis" in normalized:
                return True
            if "hey" in normalized:
                heard_hey = True
                hey_timestamp = time.time()
            return False

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            phrase = result.get("text", "")
            if handle_text(phrase, "final"):
                print("Wake word detected")
                return
        else:
            partial = json.loads(recognizer.PartialResult()).get("partial", "")
            if handle_text(partial, "partial"):
                print("Wake word detected")
                return

        if heard_hey and time.time() - hey_timestamp > 4:
            heard_hey = False
