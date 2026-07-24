import argparse
from pathlib import Path

from gtts import gTTS


def synthesize_text_to_file(text: str, output_path: Path, lang: str = "en") -> None:
    """Generate speech from text using Google Text-to-Speech and save to file."""
    tts = gTTS(text=text, lang=lang, slow=False)
    
    # Save to the specified file path
    tts.save(str(output_path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert text to speech and save audio to a file")
    parser.add_argument("text", type=str, help="Text to convert to speech")
    parser.add_argument("--output", default="output.mp3", help="Output audio file path (default: output.mp3)")
    parser.add_argument("--lang", default="en", help="Language code (default: en)")
    args = parser.parse_args()

    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating speech for text: {args.text}")
    print(f"Saving audio to: {output_file}")

    synthesize_text_to_file(args.text, output_file, lang=args.lang)

    print("Done.")


if __name__ == "__main__":
    main()
