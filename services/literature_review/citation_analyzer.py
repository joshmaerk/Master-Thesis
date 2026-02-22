#!/usr/bin/env python3
"""
Zitationsfrequenz-Analyse.

Scannt alle .tex-Dateien nach Zitationsbefehlen und gibt zurück:
  - Wie oft jeder BibTeX-Key zitiert wird
  - Welche Einträge der .bib nicht zitiert werden
  - Welche Keys im Text zitiert werden, aber nicht in der .bib existieren
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# Alle gängigen biblatex-Zitierbefehle (auch Großschreibungsvarianten)
_CITE_CMDS = (
    r"parencite|Parencite|textcite|Textcite|cite|autocite|Autocite"
    r"|citeauthor|citeauthor\*|citeyear|citealt|citealp"
    r"|footcite|fullcite|nocite|supercite"
)

# Erkennt: \cmd[pre][post]{key1, key2}  und  \cmd*[...]{key1}
_CITE_RE = re.compile(
    rf"\\(?:{_CITE_CMDS})\*?"      # Befehlsname
    r"(?:\[[^\]]*\]){0,2}"          # optionale pre-/post-notes
    r"\{([^}]+)\}",                 # {key1, key2, ...}
    re.IGNORECASE,
)

# Inline-Kommentare entfernen (aber \% nicht)
_COMMENT_RE = re.compile(r"(?<!\\)%.*$")


@dataclass
class CitationLocation:
    file: Path
    line: int


@dataclass
class CitationStats:
    """Vollständige Zitationsanalyse."""

    # Wie oft jeder Key zitiert wurde (inkl. Keys die nicht in .bib sind)
    counts: Counter = field(default_factory=Counter)

    # Alle Fundstellen pro Key: {key: [CitationLocation, ...]}
    locations: dict[str, list[CitationLocation]] = field(default_factory=dict)

    # Keys in .bib die nicht im Text zitiert werden
    uncited: list[str] = field(default_factory=list)

    # Keys die im Text zitiert werden aber NICHT in .bib sind
    # Liste von (key, location)
    missing: list[tuple[str, CitationLocation]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Kern-Scanning
# ---------------------------------------------------------------------------

def scan_tex_files(
    tex_root: Path,
    exclude_dirs: set[str] | None = None,
) -> dict[str, list[CitationLocation]]:
    """
    Durchsucht alle .tex-Dateien rekursiv nach Zitationsbefehlen.

    Returns:
        {bib_key: [CitationLocation, ...]}
    """
    if exclude_dirs is None:
        exclude_dirs = {"archiv", ".git", "utils"}

    result: dict[str, list[CitationLocation]] = {}

    for tex_file in sorted(tex_root.rglob("*.tex")):
        # Ausgeschlossene Verzeichnisse überspringen
        if any(part in exclude_dirs for part in tex_file.parts):
            continue

        try:
            text = tex_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for lineno, raw_line in enumerate(text.splitlines(), start=1):
            # Kommentare entfernen
            line = _COMMENT_RE.sub("", raw_line)

            for m in _CITE_RE.finditer(line):
                for raw_key in m.group(1).split(","):
                    key = raw_key.strip()
                    if key:
                        loc = CitationLocation(file=tex_file, line=lineno)
                        result.setdefault(key, []).append(loc)

    return result


# ---------------------------------------------------------------------------
# Haupt-API
# ---------------------------------------------------------------------------

def analyze(
    bib_entries: list[dict],
    tex_root: Path,
    ignore_keys: set[str] | None = None,
) -> CitationStats:
    """
    Führt die vollständige Zitationsfrequenz-Analyse durch.

    Args:
        bib_entries:  Geparste BibTeX-Einträge (aus analyze.load_bib)
        tex_root:     Wurzelverzeichnis des LaTeX-Projekts
        ignore_keys:  BibTeX-Keys die übersprungen werden sollen

    Returns:
        CitationStats
    """
    ignore_keys = ignore_keys or set()
    bib_key_set = {e["ID"] for e in bib_entries if e["ID"] not in ignore_keys}

    locations = scan_tex_files(tex_root)

    stats = CitationStats()
    stats.locations = locations
    stats.counts = Counter({k: len(v) for k, v in locations.items()})

    # Nicht zitierte Einträge: in .bib aber nicht im Text
    # \nocite{*} würde alle einschließen — wird hier nicht gesondert behandelt
    stats.uncited = sorted(bib_key_set - set(locations.keys()))

    # Fehlerhafte Keys: im Text zitiert aber nicht in .bib
    for key, locs in locations.items():
        if key not in bib_key_set and key not in ignore_keys:
            for loc in locs:
                stats.missing.append((key, loc))

    return stats
