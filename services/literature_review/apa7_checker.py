"""
APA7 compliance checker for BibTeX entries.

Rein regelbasiert — kein \gls{AI}/GenAI erforderlich.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Datenmodell
# ---------------------------------------------------------------------------

@dataclass
class ComplianceIssue:
    key: str
    entry_type: str
    severity: str          # "error" | "warning"
    message: str


@dataclass
class EntryResult:
    key: str
    entry_type: str
    issues: list[ComplianceIssue] = field(default_factory=list)
    entry_raw: dict = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)


# ---------------------------------------------------------------------------
# Feldanforderungen pro Entry-Typ (APA7)
# ---------------------------------------------------------------------------

# Jede Regel-Definition:
#   required      – Felder die zwingend vorhanden sein müssen
#   at_least_one  – Listen von Feldern, von denen mind. 1 vorhanden sein muss
#   recommended   – Felder deren Fehlen eine Warnung erzeugt

RULES: dict[str, dict] = {
    "article": {
        "required": ["author", "title", "journal", "year"],
        "recommended": ["volume", "pages", "doi"],
    },
    "book": {
        "required": ["title", "publisher", "year"],
        "at_least_one": [["author", "editor"]],
        "recommended": ["address"],
    },
    "incollection": {
        "required": ["author", "title", "booktitle", "publisher", "year"],
        "recommended": ["editor", "pages"],
    },
    "inbook": {
        "required": ["title", "publisher", "year"],
        "at_least_one": [["author", "editor"]],
        "recommended": ["pages"],
    },
    "misc": {
        "required": ["title"],
        "recommended": ["author", "year"],
    },
    "online": {
        "required": ["author", "title", "url", "urldate"],
        "recommended": ["year"],
    },
    "techreport": {
        "required": ["author", "title", "institution", "year"],
    },
    "report": {
        "required": ["author", "title", "institution", "year"],
    },
    "phdthesis": {
        "required": ["author", "title", "school", "year"],
    },
    "mastersthesis": {
        "required": ["author", "title", "school", "year"],
    },
    "thesis": {
        "required": ["author", "title", "institution", "year"],
    },
}

# Bekannte Varianten → kanonischer Name
ENTRY_TYPE_ALIASES: dict[str, str] = {
    "inproceedings": "incollection",
    "conference": "incollection",
    "manual": "misc",
    "unpublished": "misc",
    "electronic": "online",
    "www": "online",
}

_DOI_BARE_RE = re.compile(r"^10\.\d{4,}", re.IGNORECASE)
_DOI_OLD_PREFIX = re.compile(r"^doi\s*:\s*", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Prüflogik
# ---------------------------------------------------------------------------

def _field_present(fields: dict, name: str) -> bool:
    return bool(fields.get(name, "").strip())


def _check_doi(doi: str) -> str | None:
    """Gibt einen Fehlertext zurück wenn das DOI nicht APA7-konform formatiert ist.

    biblatex-Konvention: Das `doi`-Feld enthält nur den Bezeichner (10.xxxx/...),
    *ohne* URL-Prefix. biblatex fügt https://doi.org/ beim Rendern selbst hinzu.
    Erlaubt sind daher:
      - 10.xxxx/...              (Bare DOI — Standardformat Zotero-Export)
      - https://doi.org/10.xxxx  (Explicit URL — ebenfalls akzeptiert)
    Fehler:
      - doi:10.xxxx/...          (veraltetes Format)
      - http://dx.doi.org/...    (veraltetes HTTP-Resolver-Format)
    """
    doi = doi.strip()
    if _DOI_OLD_PREFIX.match(doi):
        bare = _DOI_OLD_PREFIX.sub("", doi).strip()
        return f"DOI als `doi:` formatiert — muss `{bare}` (bare) oder `https://doi.org/{bare}` sein"
    if doi.startswith("http://dx.doi.org/") or doi.startswith("http://doi.org/"):
        bare = doi.split("doi.org/", 1)[1]
        return f"Veralteter HTTP-DOI-Resolver — muss `https://doi.org/{bare}` sein"
    # Bare DOI (10.xxxx/...) und https://doi.org/... sind beide korrekt
    if _DOI_BARE_RE.match(doi) or doi.startswith("https://doi.org/"):
        return None
    return f"Unbekanntes DOI-Format: `{doi[:60]}` — erwartet bare DOI (`10.xxxx/…`) oder `https://doi.org/…`"



def check_entry(entry: dict) -> EntryResult:
    """Prüft einen einzelnen BibTeX-Eintrag auf APA7-Konformität."""
    key = entry.get("ID", "???")
    raw_type = entry.get("ENTRYTYPE", "").lower()
    entry_type = ENTRY_TYPE_ALIASES.get(raw_type, raw_type)

    # Felder normalisiert (lowercase keys, Werte gestrippt)
    fields: dict[str, str] = {
        k.lower(): str(v).strip()
        for k, v in entry.items()
        if k not in ("ENTRYTYPE", "ID")
    }

    result = EntryResult(key=key, entry_type=raw_type, entry_raw=entry)

    def err(msg: str) -> None:
        result.issues.append(ComplianceIssue(key, raw_type, "error", msg))

    def warn(msg: str) -> None:
        result.issues.append(ComplianceIssue(key, raw_type, "warning", msg))

    rules = RULES.get(entry_type, {})

    # 1. Pflichtfelder
    for req in rules.get("required", []):
        if not _field_present(fields, req):
            err(f"Pflichtfeld fehlt: `{req}`")

    # 2. Mindestens-eines-Gruppen
    for group in rules.get("at_least_one", []):
        if not any(_field_present(fields, f) for f in group):
            err(f"Eines der Felder muss vorhanden sein: {', '.join(f'`{f}`' for f in group)}")

    # 3. Empfohlene Felder
    missing_rec = [f for f in rules.get("recommended", []) if not _field_present(fields, f)]
    if missing_rec:
        warn(f"Empfohlene Felder fehlen: {', '.join(f'`{f}`' for f in missing_rec)}")

    # 4. DOI-Format
    if _field_present(fields, "doi"):
        doi_msg = _check_doi(fields["doi"])
        if doi_msg:
            err(doi_msg)

    # 5. URL ohne Zugriffsdatum
    if _field_present(fields, "url") and not _field_present(fields, "urldate"):
        warn("`url` vorhanden, aber `urldate` fehlt (APA7 erfordert Zugriffsdatum)")

    # 6. Artikel ohne DOI und ohne Seiten
    if entry_type == "article":
        if not _field_present(fields, "doi") and not _field_present(fields, "pages"):
            warn("Artikel ohne `doi` und ohne `pages` — mindestens eines davon sollte vorhanden sein")

    # 7. Unbekannter Entry-Typ
    if entry_type not in RULES and raw_type not in ENTRY_TYPE_ALIASES:
        warn(f"Unbekannter Entry-Typ `@{raw_type}` — keine APA7-Regeln definiert")

    return result


def check_bib(entries: list[dict], ignore_keys: set[str]) -> list[EntryResult]:
    """Prüft alle Einträge, überspringt ignorierte Schlüssel.

    Gibt nur Einträge zurück, die mindestens ein Issue haben.
    """
    results = []
    for entry in entries:
        key = entry.get("ID", "")
        if key in ignore_keys:
            continue
        result = check_entry(entry)
        if result.has_issues:
            results.append(result)
    return results
