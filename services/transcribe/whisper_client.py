"""
OpenAI Whisper API-Client für Transkriptions-Service.
Transkribiert Audiochunks mit Segment-Level-Timestamps.
"""

from pathlib import Path
from typing import Any, Dict, List


class WhisperClient:
    def __init__(self, api_key: str):
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError(
                "openai ist nicht installiert. Bitte ausführen:\n"
                "  pip install -r services/transcribe/requirements.txt"
            )
        self._client = OpenAI(api_key=api_key)

    def transcribe(
        self,
        audio_path: Path,
        language: str = "de",
        time_offset: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Transkribiert eine Audiodatei via OpenAI Whisper API.
        time_offset: Zeitversatz in Sekunden (für Chunks: Startzeit des Chunks)

        Gibt Dict zurück mit:
          - 'text': vollständiger Rohtext
          - 'segments': Liste mit {start, end, text} (Timestamps global adjustiert)
          - 'language': erkannte Sprache
        """
        client = self._client

        with open(audio_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        segments: List[Dict[str, Any]] = []
        if hasattr(response, "segments") and response.segments:
            for seg in response.segments:
                segments.append({
                    "start": seg.start + time_offset,
                    "end": seg.end + time_offset,
                    "text": seg.text.strip(),
                })
        else:
            # Fallback: kein Segment-Timestamp verfügbar — gesamten Text als ein Segment
            segments.append({
                "start": time_offset,
                "end": time_offset,
                "text": response.text.strip(),
            })

        return {
            "text": response.text,
            "segments": segments,
            "language": getattr(response, "language", "de"),
        }
