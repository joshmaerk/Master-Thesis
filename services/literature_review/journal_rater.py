"""
Journal- und Autoren-Qualitätsbewertung.

Priorität der Datenbasis (höchste zuerst):
  1. journal_scores.json  — kuratierte Datenbank (VHB-JOURQUAL3, ABS, SJR)
  2. User-PDFs in scores/ — per AI extrahiert (pdfplumber + Claude)
  3. Claude AI            — für Journals die in keiner der o.g. Quellen sind

AI/GenAI wird NUR für Punkt 2 und 3 verwendet.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Pfad zur kuratierten JSON-Datenbank (im selben Verzeichnis)
_DB_PATH = Path(__file__).parent / "journal_scores.json"

# ---------------------------------------------------------------------------
# Datenmodelle
# ---------------------------------------------------------------------------

@dataclass
class JournalRating:
    name: str                               # Exakter Name aus BibTeX
    field: str = "Unbekannt"               # Fachrichtung
    sub_field: str = ""
    peer_reviewed: bool | None = None
    journal_type: str = "unbekannt"         # empirical|review|mixed|practitioner
    impact_level: str = "unbekannt"         # high|medium|low
    vhb_rating: str = "nicht bewertet"     # A+|A|B|C|D
    abs_rating: str = "nicht bewertet"     # 4*|4|3|2|1
    pdf_score: str = ""                    # Score direkt aus Nutzer-PDF
    pdf_source: str = ""                   # Name der Quell-PDF
    notes: str = ""
    ai_assessed: bool = False
    bib_keys: list[str] = field(default_factory=list)  # welche Einträge nutzen diesen Journal


@dataclass
class AuthorInfo:
    name: str
    papers_in_bib: int = 0
    affiliation: str = ""
    known_for: str = ""
    quality_note: str = ""
    ai_assessed: bool = False


@dataclass
class NonJournalEntry:
    key: str
    entry_type: str
    title: str
    authors: str
    year: str
    publisher: str = ""
    institution: str = ""


# ---------------------------------------------------------------------------
# BibTeX-Extraktion (kein AI)
# ---------------------------------------------------------------------------

def extract_journals(entries: list[dict], ignore_keys: set[str]) -> dict[str, JournalRating]:
    """Gibt eine Map journal_name → JournalRating zurück."""
    journals: dict[str, JournalRating] = {}
    for entry in entries:
        key = entry.get("ID", "")
        if key in ignore_keys:
            continue
        etype = entry.get("ENTRYTYPE", "").lower()
        journal_name = entry.get("journal", "").strip()
        if journal_name and etype in ("article",):
            if journal_name not in journals:
                journals[journal_name] = JournalRating(name=journal_name)
            journals[journal_name].bib_keys.append(key)
    return journals


def extract_non_journal(entries: list[dict], ignore_keys: set[str]) -> list[NonJournalEntry]:
    """Extrahiert Bücher, Berichte, Misc-Einträge."""
    results = []
    journal_types = {"article"}
    for entry in entries:
        key = entry.get("ID", "")
        if key in ignore_keys:
            continue
        etype = entry.get("ENTRYTYPE", "").lower()
        if etype in journal_types:
            continue
        results.append(NonJournalEntry(
            key=key,
            entry_type=etype,
            title=entry.get("title", "").strip(),
            authors=entry.get("author", entry.get("editor", "")).strip(),
            year=str(entry.get("year", "")).strip(),
            publisher=entry.get("publisher", "").strip(),
            institution=entry.get("institution", "").strip(),
        ))
    return results


def extract_authors(entries: list[dict], ignore_keys: set[str]) -> dict[str, AuthorInfo]:
    """Zählt Autorenaufkommen über alle nicht-ignorierten Einträge."""
    counts: dict[str, int] = {}
    for entry in entries:
        if entry.get("ID", "") in ignore_keys:
            continue
        raw_authors = entry.get("author", "")
        # BibTeX-Autorformat: "Last, First and Last2, First2"
        for author_str in re.split(r"\s+and\s+", raw_authors, flags=re.IGNORECASE):
            name = author_str.strip()
            if name:
                counts[name] = counts.get(name, 0) + 1

    return {
        name: AuthorInfo(name=name, papers_in_bib=count)
        for name, count in sorted(counts.items(), key=lambda x: -x[1])
    }


# ---------------------------------------------------------------------------
# Kuratierte JSON-Datenbank (kein AI)
# ---------------------------------------------------------------------------

def load_scores_from_db(
    journal_map: dict[str, JournalRating],
    db_path: Path = _DB_PATH,
) -> set[str]:
    """
    Liest journal_scores.json und befüllt bekannte JournalRating-Objekte.

    Returns:
        Set der Journal-Namen die in der DB gefunden wurden.
    """
    if not db_path.exists():
        print(f"  Hinweis: {db_path.name} nicht gefunden — überspringe DB-Lookup.")
        return set()

    with open(db_path, encoding="utf-8") as f:
        db: dict = json.load(f)

    db.pop("_meta", None)   # Metadaten-Eintrag überspringen

    found: set[str] = set()
    for jname, rating in journal_map.items():
        # 1. Exakter Treffer
        data = db.get(jname)
        # 2. Fallback: case-insensitiver Vergleich
        if data is None:
            jname_lower = jname.lower()
            for db_key, db_val in db.items():
                if db_key.lower() == jname_lower:
                    data = db_val
                    break
        if data is None:
            continue

        rating.field = data.get("field", rating.field)
        rating.sub_field = data.get("sub_field", "")
        rating.peer_reviewed = data.get("peer_reviewed")
        rating.journal_type = data.get("journal_type", rating.journal_type)
        rating.impact_level = data.get("impact_level", rating.impact_level)
        rating.vhb_rating = data.get("vhb_rating", "nicht bewertet")
        rating.abs_rating = data.get("abs_rating", "nicht bewertet")
        rating.notes = data.get("notes", "")
        rating.ai_assessed = False   # aus kuratierter DB, kein AI
        found.add(jname)

    print(f"  Journal-DB: {len(found)}/{len(journal_map)} Journals erkannt")
    return found


# ---------------------------------------------------------------------------
# PDF-Score-Extraktion (AI erforderlich)
# ---------------------------------------------------------------------------

def _extract_text_from_pdf(pdf_path: Path) -> str:
    """Extrahiert Text aus einer PDF-Datei."""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:30]:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n".join(text_parts)
    except ImportError:
        print("  Hinweis: pdfplumber nicht installiert — PDF-Extraktion nicht möglich.")
        return ""
    except Exception as exc:
        print(f"  Fehler beim Lesen von {pdf_path.name}: {exc}")
        return ""


def load_scores_from_pdfs(
    scores_dir: Path,
    known_journals: set[str],
    client,                     # anthropic.Anthropic, bereits initialisiert
) -> dict[str, tuple[str, str]]:
    """
    Liest alle PDFs im scores/-Ordner und sucht nach Einträgen für bekannte Journals.

    Returns:
        Dict journal_name → (score, pdf_source)
    """
    score_map: dict[str, tuple[str, str]] = {}
    pdf_files = list(scores_dir.glob("*.pdf"))

    if not pdf_files:
        return score_map

    for pdf_path in pdf_files:
        print(f"  Lese Score-PDF: {pdf_path.name}")
        text = _extract_text_from_pdf(pdf_path)
        if not text.strip():
            continue

        # Nur relevante Journals in den Prompt schreiben
        journals_list = "\n".join(f"- {j}" for j in sorted(known_journals))
        prompt = f"""Du analysierst eine Zeitschriften-Rankingliste (extrahiert aus einer PDF).
Deine Aufgabe: Finde für die folgenden Zeitschriften ihre Bewertung/Score in der Tabelle.

Gesuchte Zeitschriften:
{journals_list}

Text aus der PDF (erste 8000 Zeichen):
{text[:8000]}

Gib ein JSON-Array zurück. Führe NUR Zeitschriften auf, die du in der PDF gefunden hast:
[
  {{
    "journal_name": "Exakter Name aus der Suchliste (unverändert übernehmen)",
    "score": "Bewertung genau wie in der PDF (z.B. A+, A, B, 4*, 3, 2.1, etc.)",
    "ranking_system": "Name des Rankings (z.B. VHB-JOURQUAL3, ABS 2021)"
  }}
]

Gib NUR das JSON-Array zurück, keine Erklärungen. Wenn keine Zeitschrift gefunden, gib [] zurück."""

        try:
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text.strip()
            # JSON robustly extrahieren
            m = re.search(r"\[.*\]", raw, re.DOTALL)
            if m:
                entries = json.loads(m.group())
                for item in entries:
                    jname = item.get("journal_name", "").strip()
                    score = item.get("score", "").strip()
                    system = item.get("ranking_system", pdf_path.stem).strip()
                    if jname and score and jname in known_journals:
                        score_map[jname] = (score, f"{system} ({pdf_path.name})")
        except Exception as exc:
            print(f"  AI-Fehler bei {pdf_path.name}: {exc}")

    return score_map


# ---------------------------------------------------------------------------
# AI-basierte Journal-Bewertung
# ---------------------------------------------------------------------------

def _assess_journals_via_ai(
    journals: list[str],
    client,
) -> dict[str, dict]:
    """
    Bewertet eine Liste unbekannter Zeitschriften via Claude.
    Batchverarbeitung: alle Journals in einem Aufruf.
    """
    if not journals:
        return {}

    journals_json = json.dumps(journals, ensure_ascii=False)
    prompt = f"""Du bist Experte für akademische Bibliometrie und Zeitschriftenbewertung.

Bewerte die folgenden Zeitschriften für eine Masterarbeit im Bereich
Wirtschaft/Management/Organisationspsychologie (DACH-Raum, deutschsprachig).

Zeitschriften:
{journals_json}

Antworte mit einem JSON-Objekt, wobei der Key der exakte Zeitschriftenname ist:
{{
  "Zeitschrift A": {{
    "field": "Hauptfachrichtung (z.B. Organizational Psychology, Management, Information Systems)",
    "sub_field": "Unterfachrichtung (z.B. Work Motivation, AI & Technology)",
    "peer_reviewed": true,
    "journal_type": "empirical",
    "impact_level": "high",
    "vhb_rating": "A",
    "abs_rating": "3",
    "notes": "Kurze Einschätzung (1-2 Sätze)",
    "confidence": "high"
  }},
  ...
}}

Werte für journal_type: empirical | review | mixed | practitioner | unknown
Werte für impact_level: high | medium | low | unknown
VHB-Rating: A+ | A | B | C | D | nicht bewertet
ABS-Rating: 4* | 4 | 3 | 2 | 1 | nicht bewertet

Gib NUR das JSON zurück, keine weiteren Erklärungen. Sei ehrlich — wenn du dir nicht sicher bist, verwende "unknown"/"nicht bewertet" und niedrigen confidence-Wert."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    # Robustes JSON-Parsing
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return {}


def _assess_authors_via_ai(
    authors: list[str],
    client,
) -> dict[str, dict]:
    """Bewertet die wichtigsten Autoren (mind. 2 Werke im Bib) via Claude."""
    if not authors:
        return {}

    authors_json = json.dumps(authors, ensure_ascii=False)
    prompt = f"""Du bist Experte für Wissenschaftsforschung und Bibliometrie.

Bewerte die folgenden Wissenschaftler, die in einer Masterarbeit zu den Themen
Self-Determination Theory, Generative AI, Leadership und Arbeitspsychologie zitiert werden.

Autoren:
{authors_json}

Antworte mit einem JSON-Objekt:
{{
  "Nachname, Vorname": {{
    "affiliation": "Hauptinstitution/Universität (aktuell bekannt)",
    "known_for": "Bekanntestes Werk oder Forschungsgebiet (1 Satz)",
    "quality_note": "Einschätzung Reputation/Impact im Forschungsfeld (1 Satz)",
    "confidence": "high|medium|low"
  }},
  ...
}}

Wenn du einen Autor nicht kennst, gib {{ "affiliation": "unbekannt", "known_for": "unbekannt", "quality_note": "Keine Informationen verfügbar", "confidence": "low" }} zurück.
Gib NUR das JSON zurück."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return {}


# ---------------------------------------------------------------------------
# Haupt-API
# ---------------------------------------------------------------------------

def rate(
    entries: list[dict],
    ignore_keys: set[str],
    scores_dir: Path,
    use_ai: bool = True,
    api_key: str | None = None,
) -> tuple[dict[str, JournalRating], list[NonJournalEntry], dict[str, AuthorInfo]]:
    """
    Vollständige Bewertung: Journals, Nicht-Journal-Literatur, Autoren.

    Returns:
        (journal_ratings, non_journal_entries, author_infos)
    """
    # Datenextraktion
    journal_map = extract_journals(entries, ignore_keys)
    non_journal = extract_non_journal(entries, ignore_keys)
    author_map = extract_authors(entries, ignore_keys)

    print(f"Gefunden: {len(journal_map)} Zeitschriften, {len(non_journal)} Nicht-Journal-Einträge")
    print(f"Autoren gesamt: {len(author_map)}")

    # ── Schritt 1: Kuratierte JSON-Datenbank (immer, kein AI) ────────────
    db_found = load_scores_from_db(journal_map)
    unknown_journals = [j for j in journal_map if j not in db_found]
    print(f"  Nicht in DB: {len(unknown_journals)} Journals")

    if not use_ai:
        print("AI-Bewertung deaktiviert (--skip-ai). Überspringe PDF- und AI-Bewertung.")
        return journal_map, non_journal, author_map

    # ── Schritt 2: Anthropic-Client ───────────────────────────────────────
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        print("ANTHROPIC_API_KEY nicht gesetzt — überspringe AI-Bewertung.")
        return journal_map, non_journal, author_map

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
    except ImportError:
        print("anthropic-Paket nicht installiert — überspringe AI-Bewertung.")
        return journal_map, non_journal, author_map

    # ── Schritt 3: PDF-Scores (AI) — nur für Journals ohne DB-Eintrag ────
    if unknown_journals:
        pdf_scores = load_scores_from_pdfs(
            scores_dir, set(unknown_journals), client
        )
        print(f"  Scores aus PDFs: {len(pdf_scores)} Journals")
        for jname, (score, source) in pdf_scores.items():
            if jname in journal_map:
                journal_map[jname].pdf_score = score
                journal_map[jname].pdf_source = source

    # ── Schritt 4: AI-Bewertung — nur für wirklich unbekannte Journals ───
    # Noch unbekannt = nicht in DB UND kein vollständiger Eintrag durch PDF
    still_unknown = [
        j for j in unknown_journals
        if not journal_map[j].field or journal_map[j].field == "Unbekannt"
    ]
    if still_unknown:
        print(f"  Bewerte {len(still_unknown)} unbekannte Journals via AI …")
        ai_journal_data = _assess_journals_via_ai(still_unknown, client)
        for jname, data in ai_journal_data.items():
            if jname not in journal_map or not data:
                continue
            rating = journal_map[jname]
            rating.field = data.get("field", rating.field)
            rating.sub_field = data.get("sub_field", "")
            rating.peer_reviewed = data.get("peer_reviewed")
            rating.journal_type = data.get("journal_type", "unbekannt")
            rating.impact_level = data.get("impact_level", "unbekannt")
            if rating.vhb_rating == "nicht bewertet":
                rating.vhb_rating = data.get("vhb_rating", "nicht bewertet")
            if rating.abs_rating == "nicht bewertet":
                rating.abs_rating = data.get("abs_rating", "nicht bewertet")
            rating.notes = data.get("notes", "")
            rating.ai_assessed = True
    else:
        print("  Alle Journals in kuratierter DB gefunden — kein AI-Journal-Lookup nötig.")

    # ── Schritt 5: Autoren bewerten (AI) — nur ≥ 2 Werke im Bib ─────────
    notable_authors = [
        name for name, info in author_map.items() if info.papers_in_bib >= 2
    ]
    if notable_authors:
        print(f"  Bewerte {len(notable_authors)} Autoren (≥2 Werke) via AI …")
        ai_author_data = _assess_authors_via_ai(notable_authors, client)
        for name, data in ai_author_data.items():
            if name in author_map:
                author_map[name].affiliation = data.get("affiliation", "")
                author_map[name].known_for = data.get("known_for", "")
                author_map[name].quality_note = data.get("quality_note", "")
                author_map[name].ai_assessed = True

    return journal_map, non_journal, author_map
