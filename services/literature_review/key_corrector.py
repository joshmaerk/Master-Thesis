#!/usr/bin/env python3
"""
BibTeX-Key-Korrektor.

Scannt alle .tex-Dateien, vergleicht zitierte Keys mit der .bib-Datei
und korrigiert fehlerhafte Keys automatisch — sofern ein eindeutiger
Treffer gefunden wird. Für nicht auflösbare Fälle erscheint ein
Bericht mit Datei + Zeilennummer.

Verwendung (standalone):
    python3 services/literature_review/key_corrector.py [Optionen]

    --dry-run       Keine Dateien ändern, nur Bericht ausgeben
    --verbose       Jede Korrektur einzeln ausgeben
    --threshold F   Ähnlichkeitsschwelle für Auto-Korrektur (0–1, Standard: 0.92)
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


# ---------------------------------------------------------------------------
# Datenstrukturen
# ---------------------------------------------------------------------------

@dataclass
class Correction:
    """Eine automatisch durchgeführte Korrektur."""
    file: Path
    line: int
    wrong_key: str
    correct_key: str
    confidence: float


@dataclass
class UnresolvableKey:
    """Ein fehlerhafter Key, der nicht sicher korrigiert werden konnte."""
    file: Path
    line: int
    wrong_key: str
    candidates: list[tuple[str, float]]  # [(key, score), ...]


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


# ---------------------------------------------------------------------------
# Haupt-Logik
# ---------------------------------------------------------------------------

def correct(
    bib_entries: list[dict],
    tex_root: Path,
    exclude_dirs: set[str] | None = None,
    auto_threshold: float = 0.92,
    suggest_threshold: float = 0.70,
    dry_run: bool = False,
    verbose: bool = False,
) -> CorrectionReport:
    """
    Findet und korrigiert fehlerhafte BibTeX-Keys in allen .tex-Dateien.

    Args:
        bib_entries:       Geparste BibTeX-Einträge
        tex_root:          Wurzelverzeichnis der .tex-Dateien
        auto_threshold:    Konfidenz für automatische Korrektur (Standard: 0.92)
        suggest_threshold: Konfidenz um als Vorschlag zu erscheinen (Standard: 0.70)
        dry_run:           Keine Dateien ändern
        verbose:           Ausführliche Ausgabe

    Returns:
        CorrectionReport mit Korrekturen und unauflösbaren Fällen
    """
    if exclude_dirs is None:
        exclude_dirs = {"archiv", ".git", "utils"}

    bib_keys = [e["ID"] for e in bib_entries]
    bib_key_set = set(bib_keys)
    report = CorrectionReport()

    # Pro Key nur einmal korrigieren (nicht jede Fundstelle einzeln melden)
    already_corrected: dict[str, str] = {}   # wrong → correct
    already_unresolvable: set[str] = set()

    for tex_file in sorted(tex_root.rglob("*.tex")):
        if any(part in exclude_dirs for part in tex_file.parts):
            continue

        try:
            original = tex_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        lines = original.splitlines(keepends=True)
        file_modified = False

        for lineno, line in enumerate(lines, start=1):
            active = _COMMENT_RE.sub("", line)

            # Prüfen ob die Zeile überhaupt Zitationen enthält
            if not _CITE_RE.search(active):
                continue

            new_line = line
            for m in _CITE_RE.finditer(active):
                for raw_key in m.group(2).split(","):
                    key = raw_key.strip()
                    if not key or key in bib_key_set:
                        continue

                    # Bereits bekannte Korrektur anwenden
                    if key in already_corrected:
                        correct_key = already_corrected[key]
                        new_line = _CITE_RE.sub(
                            lambda match, wk=key, ck=correct_key: _replace_key_in_match(match, wk, ck),
                            new_line,
                        )
                        report.corrections.append(
                            Correction(tex_file, lineno, key, correct_key,
                                       next(c.confidence for c in report.corrections
                                            if c.wrong_key == key))
                        )
                        file_modified = not dry_run
                        continue

                    if key in already_unresolvable:
                        continue

                    candidates = _find_candidates(key, bib_keys, suggest_threshold)

                    if candidates and candidates[0][1] >= auto_threshold:
                        correct_key, confidence = candidates[0]
                        already_corrected[key] = correct_key

                        report.corrections.append(
                            Correction(tex_file, lineno, key, correct_key, confidence)
                        )

                        if not dry_run:
                            new_line = _CITE_RE.sub(
                                lambda match, wk=key, ck=correct_key: _replace_key_in_match(match, wk, ck),
                                new_line,
                            )
                            file_modified = True

                        if verbose:
                            rel = tex_file.relative_to(tex_root)
                            print(
                                f"  ✔ {key!r} → {correct_key!r} "
                                f"({confidence:.0%})  {rel}:{lineno}"
                            )
                    else:
                        already_unresolvable.add(key)
                        report.unresolvable.append(
                            UnresolvableKey(tex_file, lineno, key, candidates)
                        )
                        if verbose:
                            rel = tex_file.relative_to(tex_root)
                            top = candidates[0][0] if candidates else "—"
                            print(f"  ✘ {key!r} nicht korrigierbar (bester: {top!r})  {rel}:{lineno}")

            if file_modified and new_line != line:
                lines[lineno - 1] = new_line

        if file_modified:
            tex_file.write_text("".join(lines), encoding="utf-8")

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
        # Deduplizieren für die Tabelle (pro unique wrong_key nur beste Zeile)
        seen: set[str] = set()
        unique: list[Correction] = []
        for c in report.corrections:
            if c.wrong_key not in seen:
                seen.add(c.wrong_key)
                unique.append(c)

        action = "würden durchgeführt werden" if dry_run else "wurden durchgeführt"
        lines.append(f"## Automatische Korrekturen ({len(unique)} eindeutige Keys)\n\n")
        lines.append(f"_{len(report.corrections)} Fundstellen {action}._\n\n")
        lines.append("| Datei | Zeile | Fehlerhafter Key | Korrigiert zu | Konfidenz |\n")
        lines.append("|---|---|---|---|---|\n")
        for c in sorted(report.corrections, key=lambda x: (str(x.file), x.line)):
            rel = c.file.relative_to(tex_root)
            lines.append(
                f"| `{rel}` | {c.line} "
                f"| `{c.wrong_key}` | `{c.correct_key}` | {c.confidence:.0%} |\n"
            )
        lines.append("\n")
    else:
        lines.append("## Automatische Korrekturen\n\n_Keine fehlerhaften Keys gefunden._\n\n")

    # ── Nicht auflösbare Keys ─────────────────────────────────────────────────
    if report.unresolvable:
        lines.append(
            f"## Nicht korrigierbare Keys ({len(report.unresolvable)}) "
            f"— manuelle Prüfung erforderlich\n\n"
        )
        lines.append(
            "> Diese Keys kommen im Text vor, sind aber nicht in der `.bib`-Datei,\n"
            "> und es wurde kein ausreichend ähnlicher Key gefunden.\n\n"
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
            "## Nicht korrigierbare Keys\n\n"
            "_Alle gefundenen Fehler konnten automatisch korrigiert werden._\n\n"
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
    parser.add_argument(
        "--bib",
        default=str(repo_root / "B_Literatur" / "literatur.bib"),
        metavar="DATEI",
        help="Pfad zur .bib-Datei (Standard: B_Literatur/literatur.bib)",
    )
    parser.add_argument(
        "--tex-root",
        default=str(repo_root),
        metavar="DIR",
        help="Wurzelverzeichnis der .tex-Dateien (Standard: Repo-Root)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.92,
        metavar="F",
        help="Konfidenz-Schwelle für Auto-Korrektur, 0–1 (Standard: 0.92)",
    )
    parser.add_argument(
        "--suggest-threshold",
        type=float,
        default=0.70,
        metavar="F",
        help="Mindest-Ähnlichkeit für Vorschläge, 0–1 (Standard: 0.70)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Keine Dateien ändern")
    parser.add_argument("--verbose", "-v", action="store_true", help="Ausführliche Ausgabe")
    parser.add_argument(
        "--output",
        metavar="DATEI",
        help="Bericht in Datei schreiben statt auf stdout",
    )
    args = parser.parse_args()

    bib_path = Path(args.bib)
    tex_root = Path(args.tex_root)

    print(f"BibTeX-Datei: {bib_path}", file=sys.stderr)
    print(f"LaTeX-Wurzel: {tex_root}", file=sys.stderr)
    if args.dry_run:
        print("[DRY-RUN] Keine Dateien werden geändert.", file=sys.stderr)

    bib_entries = _load_bib(bib_path)
    if not bib_entries:
        print("Keine Einträge in der .bib-Datei gefunden.", file=sys.stderr)
        sys.exit(1)

    print(f"{len(bib_entries)} BibTeX-Einträge geladen.", file=sys.stderr)

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

    # Exit-Code: 1 wenn es unauflösbare Keys gibt
    if report.unresolvable:
        sys.exit(1)


if __name__ == "__main__":
    main()
