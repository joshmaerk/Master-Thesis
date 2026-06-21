"""
Speaker-Diarisierung via pyannote.audio (Phase 2 — optional).

Identifiziert, wer wann spricht, auf Basis von Audiomerkmalen (kein Video nötig).
Gibt Zeitstempel-Segmente pro Sprecher zurück, die dann als Kontext an Claude
übergeben werden. Damit muss Claude nur noch SPEAKER_00 / SPEAKER_01 auf I: / B:
abbilden statt beides selbst zu erkennen.

Voraussetzungen:
  pip install pyannote.audio
  HF_TOKEN=hf_...  (Hugging Face Access Token, in services/.env oder Umgebungsvariable)
  Modell akzeptiert unter: https://huggingface.co/pyannote/speaker-diarization-3.1

Verwendung:
  from speaker_diarizer import SpeakerDiarizer
  segments = SpeakerDiarizer(hf_token="hf_...").diarize(audio_path)
  # → [{"speaker": "SPEAKER_00", "start": 0.0, "end": 4.2}, ...]

Aufruf über transcribe.py: --diarize Flag aktiviert dieses Modul.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import NamedTuple


class SpeakerSegment(NamedTuple):
    speaker: str   # z.B. "SPEAKER_00", "SPEAKER_01"
    start: float   # Sekunden
    end: float


class SpeakerDiarizer:
    MODEL_ID = "pyannote/speaker-diarization-3.1"

    def __init__(self, hf_token: str | None = None, num_speakers: int = 2):
        """
        hf_token:     Hugging Face Access Token. Wird aus HF_TOKEN-Env-Variable gelesen,
                      falls nicht direkt übergeben.
        num_speakers: Anzahl Sprecher (für Interview-Setting typischerweise 2: I + B).
        """
        self.hf_token = hf_token or os.environ.get("HF_TOKEN", "")
        self.num_speakers = num_speakers

        if not self.hf_token:
            raise ValueError(
                "Kein Hugging Face Token gefunden.\n"
                "  Option 1: HF_TOKEN=hf_... in services/.env setzen.\n"
                "  Option 2: SpeakerDiarizer(hf_token='hf_...') aufrufen.\n"
                "  Token erstellen unter: https://huggingface.co/settings/tokens\n"
                "  Modell-Zugang beantragen unter: "
                "https://huggingface.co/pyannote/speaker-diarization-3.1"
            )

    def diarize(self, audio_path: Path) -> list[SpeakerSegment]:
        """
        Führt Speaker-Diarisierung durch.

        audio_path:  Pfad zur MP3/WAV-Audiodatei
        Rückgabe:    Sortierte Liste von SpeakerSegment (speaker, start, end)
        """
        self._check_pyannote()

        from pyannote.audio import Pipeline
        import torch

        print(f"  Lade Diarisierungs-Modell ({self.MODEL_ID})...")
        pipeline = Pipeline.from_pretrained(
            self.MODEL_ID,
            use_auth_token=self.hf_token,
        )

        # MPS (Apple Silicon) oder CUDA falls verfügbar
        device = self._best_device()
        if device:
            print(f"  Nutze Device: {device}")
            pipeline.to(torch.device(device))

        print(f"  Diarisierung läuft: {audio_path.name}")
        diarization = pipeline(
            str(audio_path),
            num_speakers=self.num_speakers,
        )

        segments: list[SpeakerSegment] = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append(SpeakerSegment(
                speaker=speaker,
                start=round(turn.start, 3),
                end=round(turn.end, 3),
            ))

        segments.sort(key=lambda s: s.start)
        print(f"  → {len(segments)} Sprecher-Segment(e) erkannt.")
        return segments

    def segments_to_context(self, segments: list[SpeakerSegment]) -> str:
        """
        Formatiert Diarisierungs-Ergebnis als lesbaren Kontext-String für Claude.
        Claude nutzt diese Zeitstempel, um I: / B: zuzuordnen.
        """
        lines = ["Sprecher-Diarisierung (wer spricht wann):"]
        for seg in segments:
            lines.append(
                f"  {seg.speaker}: {self._fmt_time(seg.start)} – {self._fmt_time(seg.end)}"
            )
        return "\n".join(lines)

    @staticmethod
    def _fmt_time(seconds: float) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    @staticmethod
    def _best_device() -> str | None:
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            if torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return None

    @staticmethod
    def _check_pyannote() -> None:
        try:
            import pyannote.audio  # noqa: F401
        except ImportError:
            print(
                "\nFehler: pyannote.audio ist nicht installiert.\n"
                "  pip install pyannote.audio\n"
                "  (Benötigt außerdem einen Hugging Face Account und Modell-Zugang.)"
            )
            sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Speaker-Diarisierung für Audiodatei.")
    parser.add_argument("audio_file", help="Pfad zur Audiodatei (MP3, WAV)")
    parser.add_argument("--num-speakers", type=int, default=2, help="Anzahl Sprecher (Standard: 2)")
    args = parser.parse_args()

    audio = Path(args.audio_file)
    if not audio.exists():
        print(f"Fehler: Datei nicht gefunden: {audio}")
        sys.exit(1)

    hf_token = os.environ.get("HF_TOKEN", "")
    diarizer = SpeakerDiarizer(hf_token=hf_token, num_speakers=args.num_speakers)
    segs = diarizer.diarize(audio)

    print("\nErgebnis:")
    print(diarizer.segments_to_context(segs))
