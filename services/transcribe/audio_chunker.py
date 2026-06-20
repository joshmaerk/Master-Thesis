"""
Audio-Splitting für Transkriptions-Service.
Teilt Audiodateien in 5-Minuten-Chunks mit 15-Sekunden-Überlapp.
"""

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class AudioChunk:
    path: Path
    start_time: float  # Sekunden vom Anfang der Originaldatei
    end_time: float
    index: int
    is_temp: bool = True

    def cleanup(self) -> None:
        if self.is_temp and self.path.exists():
            self.path.unlink()


class AudioChunker:
    def __init__(self, chunk_duration: int = 300, overlap: int = 15):
        """
        chunk_duration: Chunk-Länge in Sekunden (Standard: 5 Minuten)
        overlap: Überlapp in Sekunden (verhindert abgeschnittene Sätze an Grenzen)
        """
        self.chunk_duration = chunk_duration
        self.overlap = overlap

    def split(self, audio_path: Path) -> List[AudioChunk]:
        """
        Teilt eine Audiodatei in Chunks auf.
        Gibt Liste von AudioChunk-Objekten zurück.
        Kleine Dateien (< 24 MB und kürzer als chunk_duration) werden nicht geteilt.
        """
        try:
            from pydub import AudioSegment
        except ImportError:
            raise RuntimeError(
                "pydub ist nicht installiert. Bitte ausführen:\n"
                "  pip install -r services/transcribe/requirements.txt"
            )

        print(f"  Lade Audiodatei: {audio_path.name}")
        audio = AudioSegment.from_file(str(audio_path))
        total_seconds = len(audio) / 1000.0
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)

        print(f"  Dauer: {total_seconds / 60:.1f} Minuten, Dateigröße: {file_size_mb:.1f} MB")

        # Datei passt in einen einzelnen Whisper-Aufruf
        if total_seconds <= self.chunk_duration and file_size_mb < 24:
            print("  → Datei wird als einzelner Chunk verarbeitet.")
            return [AudioChunk(
                path=audio_path,
                start_time=0.0,
                end_time=total_seconds,
                index=0,
                is_temp=False,
            )]

        chunks = []
        chunk_ms = self.chunk_duration * 1000
        overlap_ms = self.overlap * 1000
        step_ms = chunk_ms - overlap_ms
        start_ms = 0
        index = 0

        while start_ms < len(audio):
            end_ms = min(start_ms + chunk_ms, len(audio))
            segment = audio[start_ms:end_ms]

            tmp = tempfile.NamedTemporaryFile(
                suffix=".mp3",
                prefix=f"transkript_chunk_{index:03d}_",
                delete=False,
            )
            segment.export(tmp.name, format="mp3", bitrate="128k")

            chunks.append(AudioChunk(
                path=Path(tmp.name),
                start_time=start_ms / 1000.0,
                end_time=end_ms / 1000.0,
                index=index,
                is_temp=True,
            ))

            if end_ms >= len(audio):
                break

            start_ms += step_ms
            index += 1

        print(f"  → Datei in {len(chunks)} Chunks aufgeteilt "
              f"({self.chunk_duration // 60} Min. mit {self.overlap} Sek. Überlapp).")
        return chunks
