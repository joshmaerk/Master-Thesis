#!/usr/bin/env python3
"""
Literature-Review-Analyse — Hauptskript

Verwendung:
    python3 services/literature_review/analyze.py [Optionen]

Beispiele:
    # Nur APA7-Prüfung
    python3 services/literature_review/analyze.py --check-apa7

    # Journal-Bewertung ohne AI
    python3 services/literature_review/analyze.py --rate-journals --skip-ai

    # Komplette Analyse
    python3 services/literature_review/analyze.py --check-apa7 --rate-journals

    # Testlauf (keine Issues anlegen, kein Schreiben)
    python3 services/literature_review/analyze.py --check-apa7 --rate-journals --dry-run
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import sys
from pathlib import Path

# Eigene Module aus demselben Verzeichnis importierbar machen
sys.path.insert(0, str(Path(__file__).parent))

import apa7_checker
import issue_manager
import journal_rater
import report_generator

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_BIB = REPO_ROOT / "B_Literatur" / "literatur.bib"
DEFAULT_IGNORE = Path(__file__).parent / ".literatureignore"
DEFAULT_SCORES = Path(__file__).parent / "scores"
DEFAULT_REPORT = Path(__file__).parent / "journal_report.md"


# ---------------------------------------------------------------------------
# BibTeX laden
# ---------------------------------------------------------------------------

def load_bib(bib_path: Path) -> list[dict]:
    try:
        import bibtexparser
        from bibtexparser.bparser import BibTexParser
        from bibtexparser.customization import convert_to_unicode
    except ImportError:
        print("Fehler: bibtexparser ist nicht installiert.")
        print("  pip install bibtexparser")
        sys.exit(1)

    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode

    with open(bib_path, encoding="utf-8") as f:
        bib = bibtexparser.load(f, parser=parser)

    print(f"BibTeX geladen: {len(bib.entries)} Einträge aus {bib_path.relative_to(REPO_ROOT)}")
    return bib.entries


# ---------------------------------------------------------------------------
# Ignore-Datei laden
# ---------------------------------------------------------------------------

def load_ignore(ignore_path: Path) -> set[str]:
    """
    Liest .literatureignore — gibt Menge der ignorierten BibTeX-Schlüssel zurück.
    Unterstützt:
      - Kommentare mit #
      - Exakte Schlüssel
      - fnmatch-Wildcards (*,?)
    """
    if not ignore_path.exists():
        return set()

    patterns: list[str] = []
    with open(ignore_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            patterns.append(line)

    return set(patterns)  # Rückgabe der Patterns (Matching erfolgt später)


def is_ignored(key: str, patterns: set[str]) -> bool:
    """Prüft ob ein BibTeX-Schlüssel von einem Pattern gematched wird."""
    for pattern in patterns:
        if fnmatch.fnmatchcase(key, pattern) or key == pattern:
            return True
    return False


def resolve_ignore_keys(entries: list[dict], patterns: set[str]) -> set[str]:
    """Ermittelt alle BibTeX-Keys die durch die Patterns ignoriert werden sollen."""
    return {
        entry.get("ID", "")
        for entry in entries
        if is_ignored(entry.get("ID", ""), patterns)
    }


# ---------------------------------------------------------------------------
# Argparse
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Literaturanalyse: APA7-Prüfung + Journal-Bewertung",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--bib", type=Path, default=DEFAULT_BIB,
                        metavar="DATEI", help="BibTeX-Quelldatei")
    parser.add_argument("--ignore", type=Path, default=DEFAULT_IGNORE,
                        metavar="DATEI", help=".literatureignore-Datei")
    parser.add_argument("--scores-dir", type=Path, default=DEFAULT_SCORES,
                        metavar="ORDNER", help="Ordner mit Score-PDFs")
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT,
                        metavar="DATEI", help="Ausgabepfad für Markdown-Report")
    parser.add_argument("--check-apa7", action="store_true",
                        help="APA7-Konformitätsprüfung durchführen")
    parser.add_argument("--rate-journals", action="store_true",
                        help="Journal-Qualitätsbewertung und Report erstellen")
    parser.add_argument("--skip-ai", action="store_true",
                        help="AI/GenAI-Schritte überspringen")
    parser.add_argument("--dry-run", action="store_true",
                        help="Keine Issues erstellen, keinen Report schreiben")
    parser.add_argument("--verbose", action="store_true", default=True,
                        help="Ausführliche Ausgabe")

    args = parser.parse_args()

    # Mindestens eine Aktion erforderlich
    if not args.check_apa7 and not args.rate_journals:
        parser.error("Mindestens eine Aktion erforderlich: --check-apa7 und/oder --rate-journals")

    return args


# ---------------------------------------------------------------------------
# Hauptprogramm
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    # BibTeX laden
    if not args.bib.exists():
        print(f"Fehler: BibTeX-Datei nicht gefunden: {args.bib}")
        sys.exit(1)
    entries = load_bib(args.bib)

    # Ignore-Liste laden und auflösen
    patterns = load_ignore(args.ignore)
    ignore_keys = resolve_ignore_keys(entries, patterns)
    if ignore_keys:
        print(f"Ignoriert: {len(ignore_keys)} Einträge ({', '.join(sorted(ignore_keys)[:5])}"
              f"{'…' if len(ignore_keys) > 5 else ''})")

    # ── APA7-Prüfung ──────────────────────────────────────────────────────
    if args.check_apa7:
        print("\n=== APA7-Konformitätsprüfung ===")
        results = apa7_checker.check_bib(entries, ignore_keys)

        errors = [r for r in results if r.has_errors]
        warnings = [r for r in results if not r.has_errors and r.has_issues]
        print(f"Einträge mit Problemen: {len(results)} "
              f"({len(errors)} Fehler, {len(warnings)} nur Warnungen)")

        if results:
            if args.dry_run:
                print("\n[DRY-RUN] GitHub Issues die erstellt würden:")
                for r in results:
                    issues_str = "; ".join(i.message for i in r.issues[:2])
                    print(f"  • {r.key}: {issues_str}")
            else:
                print("\nErstelle GitHub Issues …")
                outcome = issue_manager.process_issues(
                    results,
                    dry_run=args.dry_run,
                    verbose=args.verbose,
                )
                created = sum(1 for v in outcome.values() if v.startswith("http"))
                skipped = sum(1 for v in outcome.values() if v == "skipped")
                print(f"Issues: {created} neu erstellt, {skipped} bereits vorhanden")
        else:
            print("Alle Einträge sind APA7-konform.")

    # ── Journal-Bewertung ─────────────────────────────────────────────────
    if args.rate_journals:
        print("\n=== Journal-Qualitätsbewertung ===")
        use_ai = not args.skip_ai and bool(os.environ.get("ANTHROPIC_API_KEY"))

        if not use_ai and not args.skip_ai:
            print("Hinweis: ANTHROPIC_API_KEY nicht gesetzt — AI-Bewertung wird übersprungen.")

        journals, non_journal, authors = journal_rater.rate(
            entries,
            ignore_keys=ignore_keys,
            scores_dir=args.scores_dir,
            use_ai=use_ai,
        )

        report_md = report_generator.generate(
            journals,
            non_journal,
            authors,
            bib_path=str(args.bib.relative_to(REPO_ROOT)),
        )

        if args.dry_run:
            print(f"\n[DRY-RUN] Report würde nach {args.report_output} geschrieben.")
            print("--- Vorschau (erste 30 Zeilen) ---")
            for line in report_md.splitlines()[:30]:
                print(line)
        else:
            args.report_output.parent.mkdir(parents=True, exist_ok=True)
            args.report_output.write_text(report_md, encoding="utf-8")
            print(f"Report gespeichert: {args.report_output.relative_to(REPO_ROOT)}")

    print("\nAnalyse abgeschlossen.")


if __name__ == "__main__":
    main()
