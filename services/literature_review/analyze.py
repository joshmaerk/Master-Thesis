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

bib_file = Path("B_Literatur/literatur.bib").resolve()
repo_root = Path("/home/runner/work/Master-Thesis/Master-Thesis").resolve()  # Example; possibly use Path.cwd() or Path(__file__).parent

try:
    relative_path = bib_file.relative_to(repo_root)
except ValueError:
    # Handle the error, or skip using relative_to if not in subpath
    relative_path = bib_file


# Eigene Module aus demselben Verzeichnis importierbar machen
sys.path.insert(0, str(Path(__file__).parent))

import apa7_checker
import citation_analyzer
import issue_manager
import journal_rater
import key_corrector
import report_generator

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_BIB = REPO_ROOT / "B_Literatur" / "literatur.bib"
DEFAULT_IGNORE = Path(__file__).parent / ".literatureignore"
DEFAULT_SCORES = Path(__file__).parent / "scores"

# ---------------------------------------------------------------------------
# .env laden (services/.env hat Vorrang vor services/literature_review/.env)
# ---------------------------------------------------------------------------

def _load_env(path: Path) -> int:
    """Liest KEY=VALUE aus einer .env-Datei; setzt nur noch nicht gesetzte Variablen.
    Gibt Anzahl der geladenen Keys zurück."""
    if not path.exists():
        return 0
    loaded = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
                loaded += 1
    return loaded


# Suchreihenfolge: services/.env → services/literature_review/.env
_ENV_CANDIDATES = [
    REPO_ROOT / "services" / ".env",
    Path(__file__).parent / ".env",
]

for _env_path in _ENV_CANDIDATES:
    _n = _load_env(_env_path)
    if _n:
        print(f"[.env] {_n} Variable(n) aus {_env_path.relative_to(REPO_ROOT)} geladen")
DEFAULT_REPORT = Path(__file__).parent / "journal_report.md"


# ---------------------------------------------------------------------------
# BibTeX laden
# ---------------------------------------------------------------------------

def load_bib(bib_path: Path) -> list[dict]:
    """
    Toleranter BibTeX-Parser ohne externe Abhängigkeiten.
    Doppelte Felder: letzter Wert gewinnt (Zotero-Export kann doppelte DOI haben).
    """
    import re

    text = bib_path.read_text(encoding="utf-8", errors="replace")

    # Alle @type{key, ...} Blöcke finden
    entries = []
    # Findet @entrytype{key, ...} inkl. geschachtelter {}
    pos = 0
    entry_re = re.compile(r"@(\w+)\s*\{", re.IGNORECASE)
    field_re  = re.compile(
        r"(\w+)\s*=\s*(?:"
        r"\{((?:[^{}]|\{[^{}]*\})*)\}"   # {value} (ein Level geschachtelt)
        r'|"([^"]*)"'                     # "value"
        r"|(\w+)"                         # bare value
        r")",
        re.DOTALL,
    )

    while pos < len(text):
        m = entry_re.search(text, pos)
        if not m:
            break
        etype = m.group(1).lower()
        if etype in ("comment", "preamble", "string"):
            pos = m.end()
            continue

        # Klammertiefe-Tracking um Eintragsende zu finden
        depth = 1
        i = m.end()
        while i < len(text) and depth > 0:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        block = text[m.end():i - 1]
        pos = i

        # Schlüssel ist das erste Komma-getrennte Token
        comma = block.find(",")
        if comma == -1:
            continue
        key = block[:comma].strip()
        body = block[comma + 1:]

        row: dict = {"ID": key, "ENTRYTYPE": etype}
        for fm in field_re.finditer(body):
            fname = fm.group(1).lower()
            fval  = (fm.group(2) or fm.group(3) or fm.group(4) or "").strip()
            row[fname] = fval   # Duplikat: letzter Wert gewinnt

        entries.append(row)

    print(f"BibTeX geladen: {len(entries)} Einträge aus {bib_path.relative_to(REPO_ROOT)}")
    return entries


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
    parser.add_argument("--check-citations", action="store_true",
                        help="Zitationsfrequenz analysieren (zitiert/nicht zitiert)")
    parser.add_argument("--fix-keys", action="store_true",
                        help="Fehlerhafte BibTeX-Keys in .tex-Dateien finden und korrigieren")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interaktiver Modus für --fix-keys: Benutzer entscheidet für jeden Key")
    parser.add_argument("--fix-threshold", type=float, default=0.92, metavar="F",
                        help="Konfidenz-Schwelle für Auto-Korrektur, 0–1 (Standard: 0.92)")
    parser.add_argument("--key-report-output", type=Path,
                        default=Path(__file__).parent / "key_correction_report.md",
                        metavar="DATEI",
                        help="Ausgabepfad für den Key-Korrekturbericht")
    parser.add_argument("--skip-ai", action="store_true",
                        help="AI/GenAI-Schritte überspringen")
    parser.add_argument("--dry-run", action="store_true",
                        help="Keine Issues erstellen, keinen Report schreiben, keine Dateien ändern")
    parser.add_argument("--verbose", action="store_true", default=True,
                        help="Ausführliche Ausgabe")

    args = parser.parse_args()

    # Mindestens eine Aktion erforderlich
    if not any([args.check_apa7, args.rate_journals, args.check_citations, args.fix_keys]):
        parser.error(
            "Mindestens eine Aktion erforderlich: "
            "--check-apa7, --rate-journals, --check-citations, --fix-keys"
        )

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

    # ── Zitationsfrequenz-Analyse ──────────────────────────────────────────
    cit_stats = None
    if args.check_citations or args.rate_journals:
        print("\n=== Zitationsfrequenz-Analyse ===")
        cit_stats = citation_analyzer.analyze(
            bib_entries=entries,
            tex_root=REPO_ROOT,
            ignore_keys=ignore_keys,
        )
        bib_key_set = {e["ID"] for e in entries}
        cited_count = len([k for k in cit_stats.counts if k in bib_key_set])
        total_active = len(entries) - len(ignore_keys)
        print(f"Zitiert:          {cited_count} / {total_active}")
        print(f"Nicht zitiert:    {len(cit_stats.uncited)} / {total_active}")
        print(f"Gesamtzitationen: {sum(cit_stats.counts.values())}")
        if cit_stats.missing:
            unique_missing = len({k for k, _ in cit_stats.missing})
            print(f"Fehlerhafte Keys: {unique_missing} (run --fix-keys)")

        # Detaillierte Liste der nicht zitierten Einträge
        if cit_stats.uncited and args.check_citations:
            bib_map = {e["ID"]: e for e in entries}
            print(f"\nNicht zitierte Einträge ({len(cit_stats.uncited)}):")
            for key in cit_stats.uncited:
                entry = bib_map.get(key, {})
                author_raw = entry.get("author", "")
                # Ersten Autor kürzen: "Nachname, V." oder "Nachname"
                first_author = author_raw.split(" and ")[0].split(",")[0].strip() if author_raw else "—"
                year = entry.get("year", "—")
                etype = entry.get("ENTRYTYPE", "?")
                print(f"  {key:<45}  {first_author} ({year})  [{etype}]")

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
            citation_stats=cit_stats,
            bib_entries=entries,
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

    # ── BibTeX-Key-Korrektur ───────────────────────────────────────────────
    if args.fix_keys:
        mode_label = "interaktiv" if args.interactive else "automatisch"
        print(f"\n=== BibTeX-Key-Korrektur ({mode_label}) ===")
        if args.dry_run:
            print("[DRY-RUN] Keine Dateien werden geändert.")

        if args.interactive:
            correction_report = key_corrector.interactive_correct(
                bib_entries=entries,
                tex_root=REPO_ROOT,
                dry_run=args.dry_run,
            )
        else:
            correction_report = key_corrector.correct(
                bib_entries=entries,
                tex_root=REPO_ROOT,
                auto_threshold=args.fix_threshold,
                dry_run=args.dry_run,
                verbose=args.verbose,
            )

        auto = len({c.wrong_key for c in correction_report.corrections})
        unres = len(correction_report.unresolvable)
        action = "würden korrigiert" if args.dry_run else "korrigiert"
        print(f"{auto} eindeutige Keys {action}, {unres} nicht auflösbar")

        report_md = key_corrector.format_report(
            correction_report, REPO_ROOT, dry_run=args.dry_run
        )

        if args.dry_run:
            print("\n--- Bericht-Vorschau (erste 20 Zeilen) ---")
            for line in report_md.splitlines()[:20]:
                print(line)
        else:
            args.key_report_output.parent.mkdir(parents=True, exist_ok=True)
            args.key_report_output.write_text(report_md, encoding="utf-8")
            print(f"Bericht gespeichert: {args.key_report_output.relative_to(REPO_ROOT)}")

    print("\nAnalyse abgeschlossen.")


if __name__ == "__main__":
    main()
