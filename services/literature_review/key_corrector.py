#!/usr/bin/env python3
"""
BibTeX-Key-Korrektor.

Scannt alle .tex-Dateien, vergleicht zitierte Keys mit der .bib-Datei
und korrigiert fehlerhafte Keys — automatisch oder interaktiv.

Verwendung (standalone):
    # Automatischer Modus (nur Keys >= Konfidenz-Schwelle)
    python3 services/literature_review/key_corrector.py [--dry-run]

    # Interaktiver Modus (Benutzer entscheidet für jeden Key)
    python3 services/literature_review/key_corrector.py --interactive

Optionen:
    --interactive   Benutzer entscheidet für jeden Key interaktiv
    --dry-run       Keine Dateien ändern, nur Bericht ausgeben
    --verbose       Jede Korrektur einzeln ausgeben (nur Auto-Modus)
    --threshold F   Ähnlichkeitsschwelle für Auto-Korrektur (0–1, Standard: 0.92)
    --suggest-threshold F  Mindest-Ähnlichkeit für Vorschläge (Standard: 0.60)
    --bib DATEI     Pfad zur .bib-Datei
    --tex-root DIR  Wurzelverzeichnis der .tex-Dateien
    --output DATEI  Ausgabedatei für den Bericht (Standard: stdout)
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Alle gängigen biblatex-Zitierbefehle
_CITE_CMDS = (
    r"parencite|Parencite|textcite|Textcite|cite|autocite|Autocite"
    r"|citeauthor|citeauthor\*|citeyear|citealt|citealp"
    r"|footcite|fullcite|nocite|supercite"
)

# Gruppe 1: Befehl inkl. Optionen, Gruppe 2: Schlüsselliste
_CITE_RE = re.compile(
    rf"(\\(?:{_CITE_CMDS})\*?(?:\[[^\]]*\]){{0,2}})"   # Befehl
    r"\{([^}]+)\}",                                      # {key1, key2}
    re.IGNORECASE,
)

_COMMENT_RE = re.compile(r"(?<!\\)%.*$")

_EXCLUDE_DEFAULT = {"archiv", ".git", "utils"}


# ---------------------------------------------------------------------------
# Datenstrukturen
# ---------------------------------------------------------------------------

@dataclass
class Correction:
    """Eine durchgeführte oder vorgeschlagene Korrektur."""
    file: Path
    line: int
    wrong_key: str
    correct_key: str
    confidence: float


@dataclass
class UnresolvableKey:
    """Ein fehlerhafter Key, der übersprungen wurde."""
    file: Path
    line: int
    wrong_key: str
    candidates: list[tuple[str, float]]


@dataclass
class CorrectionReport:
    corrections: list[Correction] = field(default_factory=list)
    unresolvable: list[UnresolvableKey] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _find_candidates(
    wrong_key: str,
    bib_keys: list[str],
    threshold: float,
) -> list[tuple[str, float]]:
    """Gibt die ähnlichsten BibTeX-Keys sortiert nach Ähnlichkeit zurück."""
    scores = [
        (k, difflib.SequenceMatcher(None, wrong_key.lower(), k.lower()).ratio())
        for k in bib_keys
    ]
    return sorted(
        [(k, s) for k, s in scores if s >= threshold],
        key=lambda x: x[1],
        reverse=True,
    )[:5]


def _replace_key_in_match(match: re.Match, wrong_key: str, correct_key: str) -> str:
    """Ersetzt einen Key in einem Zitationsbefehl, lässt andere unverändert."""
    cmd = match.group(1)
    keys = [k.strip() for k in match.group(2).split(",")]
    new_keys = [correct_key if k == wrong_key else k for k in keys]
    return f"{cmd}{{{', '.join(new_keys)}}}"


def _score_bar(score: float, width: int = 10) -> str:
    filled = round(score * width)
    return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------------------
# Kern: Scan-Phase (gemeinsam für Auto- und Interaktiv-Modus)
# ---------------------------------------------------------------------------

def _scan_wrong_keys(
    bib_entries: list[dict],
    tex_root: Path,
    exclude_dirs: set[str],
    suggest_threshold: float,
) -> dict[str, tuple[list[tuple[Path, int]], list[tuple[str, float]]]]:
    """
    Scannt alle .tex-Dateien und sammelt fehlerhafte BibTeX-Keys.

    Returns:
        {wrong_key: ([(datei, zeile), ...], [(kandidat, score), ...])}
        Sortiert nach erstem Vorkommen (Datei, Zeile).
    """
    bib_keys = [e["ID"] for e in bib_entries]
    bib_key_set = set(bib_keys)

    # {wrong_key: [(file, line), ...]} — in Scanreihenfolge
    occurrences: dict[str, list[tuple[Path, int]]] = {}

    for tex_file in sorted(tex_root.rglob("*.tex")):
        if any(part in exclude_dirs for part in tex_file.parts):
            continue
        try:
            text = tex_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for lineno, line in enumerate(text.splitlines(), start=1):
            active = _COMMENT_RE.sub("", line)
            if not _CITE_RE.search(active):
                continue
            for m in _CITE_RE.finditer(active):
                for raw_key in m.group(2).split(","):
                    key = raw_key.strip()
                    if key and key not in bib_key_set:
                        occurrences.setdefault(key, []).append((tex_file, lineno))

    # Kandidaten pro Key berechnen
    result: dict[str, tuple[list[tuple[Path, int]], list[tuple[str, float]]]] = {}
    for key, locs in occurrences.items():
        candidates = _find_candidates(key, bib_keys, suggest_threshold)
        result[key] = (locs, candidates)

    return result


# ---------------------------------------------------------------------------
# Kern: Anwenden von Entscheidungen (gemeinsam für beide Modi)
# ---------------------------------------------------------------------------

def _apply_decisions(
    decisions: dict[str, str],          # wrong_key → correct_key
    wrong_key_locs: dict[str, list],    # wrong_key → [(file, line), ...]
    bib_key_set: set[str],
    tex_root: Path,
    exclude_dirs: set[str],
    dry_run: bool,
) -> list[Correction]:
    """Wendet alle Entscheidungen in den .tex-Dateien an und gibt Corrections zurück."""
    if not decisions:
        return []

    corrections: list[Correction] = []

    # Alle betroffenen Dateien bestimmen
    affected_files: set[Path] = set()
    for key in decisions:
        for f, _ in wrong_key_locs.get(key, []):
            affected_files.add(f)

    for tex_file in sorted(affected_files):
        try:
            original = tex_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        lines = original.splitlines(keepends=True)
        file_modified = False

        for lineno, line in enumerate(lines, start=1):
            active = _COMMENT_RE.sub("", line)
            if not _CITE_RE.search(active):
                continue

            new_line = line
            for m in _CITE_RE.finditer(active):
                for raw_key in m.group(2).split(","):
                    key = raw_key.strip()
                    if key in decisions:
                        correct_key = decisions[key]
                        new_line = _CITE_RE.sub(
                            lambda match, wk=key, ck=correct_key: _replace_key_in_match(match, wk, ck),
                            new_line,
                        )
                        corrections.append(Correction(tex_file, lineno, key, correct_key, 1.0))
                        file_modified = True

            if file_modified:
                lines[lineno - 1] = new_line

        if file_modified and not dry_run:
            tex_file.write_text("".join(lines), encoding="utf-8")

    return corrections


# ---------------------------------------------------------------------------
# Automatischer Modus
# ---------------------------------------------------------------------------

def correct(
    bib_entries: list[dict],
    tex_root: Path,
    exclude_dirs: set[str] | None = None,
    auto_threshold: float = 0.92,
    suggest_threshold: float = 0.60,
    dry_run: bool = False,
    verbose: bool = False,
) -> CorrectionReport:
    """
    Korrigiert fehlerhafte BibTeX-Keys automatisch wenn Konfidenz >= auto_threshold.
    Keys unterhalb der Schwelle landen in CorrectionReport.unresolvable.
    """
    if exclude_dirs is None:
        exclude_dirs = _EXCLUDE_DEFAULT

    bib_key_set = {e["ID"] for e in bib_entries}
    wrong_keys = _scan_wrong_keys(bib_entries, tex_root, exclude_dirs, suggest_threshold)

    decisions: dict[str, str] = {}
    report = CorrectionReport()

    for wrong_key, (locs, candidates) in wrong_keys.items():
        if candidates and candidates[0][1] >= auto_threshold:
            correct_key, confidence = candidates[0]
            decisions[wrong_key] = correct_key
            if verbose:
                print(f"  ✔ {wrong_key!r} → {correct_key!r} ({confidence:.0%})")
        else:
            for f, ln in locs:
                report.unresolvable.append(UnresolvableKey(f, ln, wrong_key, candidates))
            if verbose:
                top = candidates[0][0] if candidates else "—"
                print(f"  ✘ {wrong_key!r} nicht korrigierbar (bester: {top!r})")

    applied = _apply_decisions(decisions, wrong_keys, bib_key_set, tex_root, exclude_dirs, dry_run)

    # confidence aus decisions zurückrechnen
    conf_map = {
        wrong_key: candidates[0][1]
        for wrong_key, (_, candidates) in wrong_keys.items()
        if candidates and wrong_key in decisions
    }
    for c in applied:
        c.confidence = conf_map.get(c.wrong_key, 1.0)
    report.corrections = applied

    return report


# ---------------------------------------------------------------------------
# Interaktiver Modus
# ---------------------------------------------------------------------------

def interactive_correct(
    bib_entries: list[dict],
    tex_root: Path,
    exclude_dirs: set[str] | None = None,
    suggest_threshold: float = 0.60,
    dry_run: bool = False,
) -> CorrectionReport:
    """
    Interaktiver Modus: für jeden fehlerhaften Key entscheidet der Benutzer,
    ob und wie er korrigiert werden soll.
    """
    if exclude_dirs is None:
        exclude_dirs = _EXCLUDE_DEFAULT

    bib_key_set = {e["ID"] for e in bib_entries}
    print("Scanne .tex-Dateien …")
    wrong_keys = _scan_wrong_keys(bib_entries, tex_root, exclude_dirs, suggest_threshold)

    if not wrong_keys:
        print("Keine fehlerhaften BibTeX-Keys gefunden.")
        return CorrectionReport()

    total = len(wrong_keys)
    decisions: dict[str, str] = {}   # wrong_key → correct_key
    skipped: list[str] = []

    print(f"\n{total} fehlerhafte Key(s) gefunden. Für jeden Key bitte eine Auswahl treffen.\n")

    quit_requested = False

    for idx, (wrong_key, (locs, candidates)) in enumerate(wrong_keys.items(), start=1):
        if quit_requested:
            break

        # ── Kopfzeile ────────────────────────────────────────────────────────
        print(f"{'═' * 62}")
        print(f"  [{idx}/{total}]  {wrong_key}")
        print(f"{'─' * 62}")

        # Vorkommen anzeigen (max. 3)
        for f, ln in locs[:3]:
            print(f"  Datei  {f.relative_to(tex_root)} : {ln}")
        if len(locs) > 3:
            print(f"         … und {len(locs) - 3} weitere Fundstelle(n)")
        print()

        # ── Kandidaten ───────────────────────────────────────────────────────
        if candidates:
            print("  Vorschläge:")
            for i, (cand_key, score) in enumerate(candidates, start=1):
                print(f"    [{i}] {cand_key:<52} {score:.0%}  {_score_bar(score)}")
        else:
            print("  Keine ähnlichen Keys in der .bib-Datei gefunden.")

        # ── Eingabeaufforderung ───────────────────────────────────────────────
        print()
        opts = ([f"[1–{len(candidates)}] Vorschlag"] if candidates else [])
        opts += ["[e] eigener Key", "[s] überspringen", "[q] beenden"]
        print(f"  {'  |  '.join(opts)}")

        decided = False
        while not decided:
            try:
                raw = input("  > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nEingabe beendet — verbleibende Keys werden übersprungen.")
                quit_requested = True
                decided = True
                break

            choice = raw.lower()

            if choice == "q":
                print("  Vorzeitig beendet. Bisherige Entscheidungen werden angewendet.\n")
                quit_requested = True
                decided = True

            elif choice == "s":
                skipped.append(wrong_key)
                print(f"  → Übersprungen.\n")
                decided = True

            elif choice == "e":
                try:
                    custom = input("  Eigener Key: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    quit_requested = True
                    decided = True
                    break
                if custom:
                    decisions[wrong_key] = custom
                    print(f"  → {wrong_key!r}  →  {custom!r}\n")
                    decided = True
                else:
                    print("  Kein Key eingegeben, bitte erneut versuchen.")

            elif choice.isdigit():
                i = int(choice) - 1
                if candidates and 0 <= i < len(candidates):
                    decisions[wrong_key] = candidates[i][0]
                    print(f"  → {wrong_key!r}  →  {candidates[i][0]!r}\n")
                    decided = True
                else:
                    print(f"  Ungültige Auswahl. Bitte 1–{len(candidates)} eingeben.")

            else:
                print("  Ungültige Eingabe.")

    # ── Zusammenfassung ───────────────────────────────────────────────────────
    print(f"{'═' * 62}")
    print(f"  Zusammenfassung:")
    print(f"    Zu korrigieren : {len(decisions)}")
    print(f"    Übersprungen   : {len(skipped)}")
    if dry_run:
        print(f"    Modus          : DRY-RUN — keine Dateien werden geändert")
    print(f"{'═' * 62}\n")

    if not decisions:
        print("Keine Änderungen.")
        report = CorrectionReport()
        for wrong_key in skipped:
            locs, cands = wrong_keys[wrong_key]
            for f, ln in locs:
                report.unresolvable.append(UnresolvableKey(f, ln, wrong_key, cands))
        return report

    print("Ausstehende Korrekturen:")
    for wk, ck in decisions.items():
        print(f"  {wk!r}  →  {ck!r}")
    print()

    if not dry_run:
        try:
            confirm = input("Änderungen in .tex-Dateien schreiben? [j/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            confirm = "n"
        if confirm not in ("j", "ja", "y", "yes"):
            print("Abgebrochen. Keine Dateien geändert.")
            return CorrectionReport()

    applied = _apply_decisions(decisions, wrong_keys, bib_key_set, tex_root, exclude_dirs, dry_run)

    report = CorrectionReport()
    report.corrections = applied
    for wrong_key in skipped:
        locs, cands = wrong_keys[wrong_key]
        for f, ln in locs:
            report.unresolvable.append(UnresolvableKey(f, ln, wrong_key, cands))

    n = len(applied)
    if dry_run:
        print(f"[DRY-RUN] {n} Fundstelle(n) würden korrigiert.")
    else:
        print(f"{n} Fundstelle(n) korrigiert.")

    return report


# ---------------------------------------------------------------------------
# Bericht-Formatierung
# ---------------------------------------------------------------------------

def format_report(
    report: CorrectionReport,
    tex_root: Path,
    dry_run: bool = False,
) -> str:
    """Formatiert den Korrekturbericht als Markdown."""
    mode = "DRY-RUN — keine Dateien geändert" if dry_run else "Ausgeführt"
    lines = [
        "# BibTeX-Key-Korrekturbericht\n",
        f"_{mode}_\n\n",
    ]

    # ── Korrekturen ──────────────────────────────────────────────────────────
    if report.corrections:
        seen: set[str] = set()
        unique: list[Correction] = []
        for c in report.corrections:
            if c.wrong_key not in seen:
                seen.add(c.wrong_key)
                unique.append(c)

        action = "würden durchgeführt" if dry_run else "wurden durchgeführt"
        lines.append(f"## Korrekturen ({len(unique)} eindeutige Keys)\n\n")
        lines.append(f"_{len(report.corrections)} Fundstellen {action}._\n\n")
        lines.append("| Datei | Zeile | Fehlerhafter Key | Korrigiert zu | Konfidenz |\n")
        lines.append("|---|---|---|---|---|\n")
        for c in sorted(report.corrections, key=lambda x: (str(x.file), x.line)):
            rel = c.file.relative_to(tex_root)
            conf = f"{c.confidence:.0%}" if c.confidence < 1.0 else "manuell"
            lines.append(
                f"| `{rel}` | {c.line} "
                f"| `{c.wrong_key}` | `{c.correct_key}` | {conf} |\n"
            )
        lines.append("\n")
    else:
        lines.append("## Korrekturen\n\n_Keine Korrekturen durchgeführt._\n\n")

    # ── Übersprungene / nicht auflösbare Keys ─────────────────────────────────
    if report.unresolvable:
        lines.append(
            f"## Übersprungene Keys ({len(report.unresolvable)}) "
            f"— manuelle Prüfung erforderlich\n\n"
        )
        lines.append("| Datei | Zeile | Fehlerhafter Key | Ähnliche Keys in .bib |\n")
        lines.append("|---|---|---|---|\n")
        for u in sorted(report.unresolvable, key=lambda x: (str(x.file), x.line)):
            rel = u.file.relative_to(tex_root)
            cands = (
                ", ".join(f"`{k}` ({s:.0%})" for k, s in u.candidates)
                if u.candidates
                else "_keine ähnlichen Keys_"
            )
            lines.append(
                f"| `{rel}` | {u.line} | `{u.wrong_key}` | {cands} |\n"
            )
        lines.append("\n")
    else:
        lines.append(
            "## Übersprungene Keys\n\n"
            "_Alle gefundenen Fehler wurden korrigiert._\n\n"
        )

    return "".join(lines)


# ---------------------------------------------------------------------------
# Standalone-Verwendung
# ---------------------------------------------------------------------------

def _load_bib(bib_path: Path) -> list[dict]:
    """Minimaler BibTeX-Parser (kopiert aus analyze.py)."""
    import re as _re
    entries = []
    try:
        text = bib_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"Fehler beim Lesen der .bib-Datei: {e}", file=sys.stderr)
        return entries
    _entry_re = _re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", _re.IGNORECASE)
    for m in _entry_re.finditer(text):
        etype = m.group(1).lower()
        if etype in ("comment", "preamble", "string"):
            continue
        entries.append({"ENTRYTYPE": etype, "ID": m.group(2).strip()})
    return entries


def main() -> None:
    """Standalone-Einstiegspunkt."""
    repo_root = Path(__file__).resolve().parent.parent.parent

    parser = argparse.ArgumentParser(
        description="Findet und korrigiert fehlerhafte BibTeX-Keys in .tex-Dateien.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--bib", default=str(repo_root / "B_Literatur" / "literatur.bib"),
                        metavar="DATEI", help="Pfad zur .bib-Datei")
    parser.add_argument("--tex-root", default=str(repo_root),
                        metavar="DIR", help="Wurzelverzeichnis der .tex-Dateien")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interaktiver Modus — Benutzer entscheidet für jeden Key")
    parser.add_argument("--threshold", type=float, default=0.92, metavar="F",
                        help="Konfidenz-Schwelle Auto-Korrektur (Standard: 0.92)")
    parser.add_argument("--suggest-threshold", type=float, default=0.60, metavar="F",
                        help="Mindest-Ähnlichkeit für Vorschläge (Standard: 0.60)")
    parser.add_argument("--dry-run", action="store_true", help="Keine Dateien ändern")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Ausführliche Ausgabe (nur Auto-Modus)")
    parser.add_argument("--output", metavar="DATEI",
                        help="Bericht in Datei schreiben (Standard: stdout)")
    args = parser.parse_args()

    bib_path = Path(args.bib)
    tex_root = Path(args.tex_root)

    print(f"BibTeX-Datei : {bib_path}", file=sys.stderr)
    print(f"LaTeX-Wurzel : {tex_root}", file=sys.stderr)
    if args.dry_run:
        print("[DRY-RUN]", file=sys.stderr)

    bib_entries = _load_bib(bib_path)
    if not bib_entries:
        print("Keine Einträge in der .bib-Datei gefunden.", file=sys.stderr)
        sys.exit(1)
    print(f"{len(bib_entries)} BibTeX-Einträge geladen.\n", file=sys.stderr)

    if args.interactive:
        report = interactive_correct(
            bib_entries=bib_entries,
            tex_root=tex_root,
            suggest_threshold=args.suggest_threshold,
            dry_run=args.dry_run,
        )
    else:
        report = correct(
            bib_entries=bib_entries,
            tex_root=tex_root,
            auto_threshold=args.threshold,
            suggest_threshold=args.suggest_threshold,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )

    md = format_report(report, tex_root, dry_run=args.dry_run)

    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"Bericht geschrieben: {args.output}", file=sys.stderr)
    else:
        print(md)

    if report.unresolvable:
        sys.exit(1)


if __name__ == "__main__":
    main()
