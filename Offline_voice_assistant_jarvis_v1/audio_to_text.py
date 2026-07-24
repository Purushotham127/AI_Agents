import argparse
import sys
from pathlib import Path

from faster_whisper import WhisperModel


def transcribe_file(audio_path: Path, model_name: str = "base", device: str = "cpu") -> str:
    model = WhisperModel(model_name, device=device)
    segments, _ = model.transcribe(str(audio_path))
    return " ".join(segment.text for segment in segments).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe an audio file to text")
    parser.add_argument("audio_path", type=str, help="Path to the audio file to transcribe")
    parser.add_argument("--model", default="base", help="Whisper model name or path (default: base)")
    parser.add_argument("--device", default="cpu", help="Device to run inference on (cpu or cuda)")
    args = parser.parse_args()

    audio_file = Path(args.audio_path)
    if not audio_file.exists():
        print(f"Audio file not found: {audio_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Transcribing {audio_file} using model {args.model} on device {args.device}...")
    text = transcribe_file(audio_file, args.model, args.device)

    print("\nTranscription:")
    print(text)


if __name__ == "__main__":
    main()
