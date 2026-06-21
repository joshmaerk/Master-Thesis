"""
MP4/Video → MP3 Audio-Extraktion via ffmpeg.
Wird von transcribe.py automatisch aufgerufen, wenn die Eingabedatei ein Video ist.
"""

import subprocess
import sys
from pathlib import Path


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}


def is_video_file(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTENSIONS


class MP4Extractor:
    def __init__(self, bitrate: str = "128k"):
        self.bitrate = bitrate

    def extract_audio(self, video_path: Path, output_dir: Path) -> Path:
        """
        Extrahiert die Audiospur aus einer Videodatei als MP3.

        video_path:  Pfad zur Eingabe-Videodatei
        output_dir:  Zielverzeichnis für die MP3-Datei
        Rückgabe:    Pfad zur erzeugten MP3-Datei
        """
        self._check_ffmpeg()

        output_path = output_dir / (video_path.stem + ".mp3")

        if output_path.exists():
            print(f"      Hinweis: {output_path.name} existiert bereits — überspringe Extraktion.")
            return output_path

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",                   # kein Video
            "-acodec", "libmp3lame",
            "-ab", self.bitrate,
            "-ar", "44100",          # Sample-Rate für Whisper
            "-y",                    # Überschreiben ohne Nachfrage
            str(output_path),
        ]

        print(f"      ffmpeg: {video_path.name} → {output_path.name}")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            print(f"\nFehler bei der Audio-Extraktion:\n{result.stderr[-1000:]}")
            sys.exit(1)

        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"      → MP3 erstellt: {output_path} ({size_mb:.1f} MB)")
        return output_path

    @staticmethod
    def _check_ffmpeg() -> None:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            print(
                "\nFehler: ffmpeg ist nicht installiert oder nicht im PATH.\n"
                "  macOS:  brew install ffmpeg\n"
                "  Ubuntu: sudo apt install ffmpeg\n"
                "  Windows: https://ffmpeg.org/download.html"
            )
            sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extrahiert Audiospur aus Videodatei.")
    parser.add_argument("video_file", help="Pfad zur Videodatei (MP4, MOV, MKV, ...)")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Ausgabeverzeichnis. Standard: gleiches Verzeichnis wie Eingabedatei.",
    )
    args = parser.parse_args()

    video = Path(args.video_file)
    if not video.exists():
        print(f"Fehler: Datei nicht gefunden: {video}")
        sys.exit(1)

    out_dir = Path(args.output_dir) if args.output_dir else video.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    extractor = MP4Extractor()
    result_path = extractor.extract_audio(video, out_dir)
    print(f"Ausgabe: {result_path}")
