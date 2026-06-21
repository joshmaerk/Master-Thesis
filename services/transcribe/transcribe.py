#!/usr/bin/env python3
"""
Transkriptions-Service für Masterarbeit-Interviews.
Transkribiert Audiodateien nach dem einfachen Transkriptionssystem von Dresing & Pehl (2017).

Verwendung (vom Repo-Root):
    python3 services/transcribe/transcribe.py interviews/audio/interview_01.mp3
    python3 services/transcribe/transcribe.py interviews/audio/interview_01.mp3 --interview-id IP-01
    python3 services/transcribe/transcribe.py interviews/audio/interview_01.mp3 --no-finalize

Umgebungsvariablen (in services/.env):
    OPENAI_API_KEY     — OpenAI API-Schlüssel (Whisper)
    ANTHROPIC_API_KEY  — Anthropic API-Schlüssel (Claude)
    ANTHROPIC_MODEL    — Claude-Modell (optional, Standard: claude-opus-4-8)
"""

import argparse
import os
import sys
from pathlib import Path


def _load_env() -> None:
    """Lädt .env-Datei aus services/.env oder .env im Repo-Root."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent

    candidates = [
        script_dir.parent / ".env",       # services/.env
        repo_root / ".env",               # Repo-Root/.env
    ]

    for env_file in candidates:
        if env_file.exists():
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and key not in os.environ:
                            os.environ[key] = value
            print(f"  Umgebungsvariablen geladen aus: {env_file}")
            return

    print("  Hinweis: Keine .env-Datei gefunden. Nutze System-Umgebungsvariablen.")


def _require_env(key: str, hint: str = "") -> str:
    """Gibt Umgebungsvariable zurück oder beendet mit Fehlermeldung."""
    value = os.environ.get(key, "").strip()
    if not value:
        msg = f"\nFehler: Umgebungsvariable '{key}' ist nicht gesetzt."
        if hint:
            msg += f"\n{hint}"
        msg += "\nBitte services/.env nach dem Vorbild von services/.env.example befüllen."
        print(msg)
        sys.exit(1)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transkription nach Dresing & Pehl (2017) via Whisper + Claude."
    )
    parser.add_argument(
        "audio_file",
        help="Pfad zur Audiodatei (MP3, WAV, M4A, FLAC, ...)",
    )
    parser.add_argument(
        "--interview-id",
        default="B",
        help="Kürzel der befragten Person (z.B. IP-01). Standard: B",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Ausgabeverzeichnis für RTF-Datei. Standard: interviews/transcripts/",
    )
    parser.add_argument(
        "--language",
        default="de",
        help="Sprache für Whisper (ISO 639-1). Standard: de",
    )
    parser.add_argument(
        "--no-finalize",
        action="store_true",
        help="Abschließenden Konsistenz-Pass (Claude) überspringen.",
    )
    parser.add_argument(
        "--chunk-minutes",
        type=int,
        default=5,
        help="Chunk-Länge in Minuten. Standard: 5",
    )
    parser.add_argument(
        "--diarize",
        action="store_true",
        help="Speaker-Diarisierung via pyannote.audio aktivieren (benötigt HF_TOKEN in .env).",
    )
    parser.add_argument(
        "--no-pseudonymize",
        action="store_true",
        help="Pseudonymisierung (Claude) überspringen.",
    )
    args = parser.parse_args()

    # ── Pfade ──────────────────────────────────────────────────────────────────
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"\nFehler: Audiodatei nicht gefunden: {audio_path}")
        sys.exit(1)

    repo_root = Path(__file__).parent.parent.parent
    output_dir = Path(args.output_dir) if args.output_dir else repo_root / "interviews" / "transcripts"
    output_path = output_dir / (audio_path.stem + ".rtf")

    print(f"\n{'='*60}")
    print(f"  Transkriptions-Service — Dresing & Pehl (2017)")
    print(f"{'='*60}")
    print(f"  Eingabedatei: {audio_path}")
    print(f"  Interview-ID: {args.interview_id}")
    print(f"  Ausgabe     : {output_path}")
    print(f"{'='*60}\n")

    # ── Schritt 0: Video → Audio (falls nötig) ────────────────────────────────
    sys.path.insert(0, str(Path(__file__).parent))
    from mp4_extractor import is_video_file, MP4Extractor

    if is_video_file(audio_path):
        print("[0/5] Audiospur aus Video extrahieren...")
        audio_path = MP4Extractor().extract_audio(
            video_path=audio_path,
            output_dir=audio_path.parent,
        )
        print()

    # ── Umgebungsvariablen ─────────────────────────────────────────────────────
    _load_env()

    openai_key = _require_env(
        "OPENAI_API_KEY",
        "  Hinweis: OpenAI API-Key erstellen unter: platform.openai.com → API Keys"
    )
    anthropic_key = _require_env(
        "ANTHROPIC_API_KEY",
        "  Hinweis: Anthropic API-Key erstellen unter: console.anthropic.com → API Keys"
    )
    claude_model = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

    # ── Imports (nach Env-Check, damit Fehler frühzeitig sichtbar) ───────────
    from audio_chunker import AudioChunker
    from whisper_client import WhisperClient
    from dresing_pehl_formatter import DresingPehlFormatter
    from rtf_writer import RTFWriter

    # ── Schritt 0b: Speaker-Diarisierung (optional) ───────────────────────────
    diarization_context = ""
    if args.diarize:
        from speaker_diarizer import SpeakerDiarizer
        hf_token = os.environ.get("HF_TOKEN", "")
        print("[0b/5] Speaker-Diarisierung (pyannote.audio)...")
        diarizer = SpeakerDiarizer(hf_token=hf_token)
        segments = diarizer.diarize(audio_path)
        diarization_context = diarizer.segments_to_context(segments)
        print()

    # ── Schritt 1: Audio aufteilen ─────────────────────────────────────────────
    print("[1/5] Audio aufteilen...")
    chunker = AudioChunker(
        chunk_duration=args.chunk_minutes * 60,
        overlap=15,
    )
    chunks = chunker.split(audio_path)
    print(f"      → {len(chunks)} Chunk(s) für Verarbeitung bereit.\n")

    # ── Schritt 2: Transkription + Formatierung ────────────────────────────────
    whisper = WhisperClient(api_key=openai_key)
    formatter = DresingPehlFormatter(api_key=anthropic_key, model=claude_model)

    formatted_blocks: list[str] = []
    previous_context = ""

    total = len(chunks)
    remaining_chunks = list(chunks)
    try:
        for chunk in chunks:
            remaining_chunks = remaining_chunks[1:]
            i = chunk.index
            print(f"[2/5] Chunk {i + 1}/{total}  ({chunk.start_time / 60:.1f}–{chunk.end_time / 60:.1f} Min.)")

            # Whisper-Transkription
            print("      Whisper-Transkription...")
            try:
                raw = whisper.transcribe(
                    audio_path=chunk.path,
                    language=args.language,
                    time_offset=chunk.start_time,
                )
            except Exception as exc:
                print(f"      FEHLER bei Whisper-Transkription: {exc}")
                chunk.cleanup()
                sys.exit(1)

            seg_count = len(raw["segments"])
            print(f"      → {seg_count} Segment(s) erkannt (Sprache: {raw['language']}).")

            # Dresing & Pehl Formatierung via Claude
            print("      Formatierung nach Dresing & Pehl (Claude)...")
            try:
                formatted = formatter.format_chunk(
                    raw_segments=raw["segments"],
                    previous_context=previous_context,
                    chunk_index=i,
                    diarization_context=diarization_context,
                )
            except Exception as exc:
                print(f"      FEHLER bei Claude-Formatierung: {exc}")
                chunk.cleanup()
                sys.exit(1)

            formatted_blocks.append(formatted)
            # Letzten ~400 Zeichen als Kontext für nächsten Chunk
            previous_context = formatted[-400:] if len(formatted) > 400 else formatted

            chunk.cleanup()
            print(f"      ✓ Chunk {i + 1} abgeschlossen.\n")
    finally:
        for leftover in remaining_chunks:
            leftover.cleanup()

    # ── Schritt 3: Zusammenführen ──────────────────────────────────────────────
    print("[3/5] Transkript zusammenführen...")
    full_transcript = "\n\n".join(formatted_blocks)

    if not args.no_finalize:
        print("      Abschließender Konsistenz-Pass (Claude)...")
        try:
            full_transcript = formatter.finalize(full_transcript)
        except Exception as exc:
            print(f"      Warnung: Finalisierung fehlgeschlagen ({exc}). Verwende unfinalisierten Text.")
    else:
        print("      (Finalisierung übersprungen via --no-finalize)")

    # ── Schritt 4: Pseudonymisierung ───────────────────────────────────────────
    print("\n[4/5] Pseudonymisierung...")
    mapping_path = output_path.with_suffix(".mapping.json")
    if not args.no_pseudonymize:
        from pseudonymizer import Pseudonymizer
        try:
            pseudo = Pseudonymizer(api_key=anthropic_key, model=claude_model)
            full_transcript = pseudo.pseudonymize(
                transcript=full_transcript,
                interview_id=args.interview_id,
                mapping_output_path=mapping_path,
            )
            print(f"      ✓ Pseudonymisierung abgeschlossen.\n")
        except Exception as exc:
            print(f"      Warnung: Pseudonymisierung fehlgeschlagen ({exc}). Verwende nicht-pseudonymisierten Text.")
    else:
        print("      (Pseudonymisierung übersprungen via --no-pseudonymize)")

    # ── Schritt 5: RTF-Ausgabe ─────────────────────────────────────────────────
    print("[5/5] RTF-Datei schreiben...")
    writer = RTFWriter()
    writer.write(
        transcript=full_transcript,
        output_path=output_path,
        interview_name=audio_path.stem,
    )

    print(f"\n{'='*60}")
    print(f"  Transkription abgeschlossen!")
    print(f"  Ausgabe: {output_path}")
    if not args.no_pseudonymize and mapping_path.exists():
        print(f"  Zuordnung: {mapping_path}")
    print(f"{'='*60}")
    print(f"\n  Nächste Schritte:")
    print(f"  1. RTF-Datei in MAXQDA importieren")
    print(f"  2. Transkript manuell gegen Aufnahme gegenhören")
    print(f"  3. Speaker-Zuweisung (I:/B:) überprüfen und korrigieren")
    print(f"  4. Pseudonymisierung gegen Zuordnungstabelle prüfen")
    print()

    # KI-Nutzung protokollieren
    import subprocess
    ki_log = repo_root / "services" / "ki_log" / "ki_log.py"
    if ki_log.exists():
        subprocess.run(
            [
                sys.executable, str(ki_log), "add",
                "--kapitel",  "Kapitel 3, Methodik / Datenerhebung / Transkription",
                "--tool",     f"OpenAI Whisper-1 + Anthropic Claude ({claude_model})",
                "--zweck",    f"Automatische Rohtranskription nach Dresing & Pehl (2017); Interview-ID: {args.interview_id}",
                "--pruefung", "Manuelles Gegenhören und Korrektur des Transkripts gegen Originalaufnahme",
                "--einfluss", "Transkriptgrundlage erstellt; inhaltliche Aussagen durch manuelle Korrektur gesichert",
            ],
            check=False,
        )


if __name__ == "__main__":
    main()
