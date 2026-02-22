"""
Markdown-Report-Generator für die Literaturqualitätsbewertung.

Kein AI/GenAI — rein datengetrieben aus den Bewertungsergebnissen.
"""

from __future__ import annotations

from datetime import datetime
from journal_rater import AuthorInfo, JournalRating, NonJournalEntry


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _bool_icon(value: bool | None) -> str:
    if value is True:
        return "✅"
    if value is False:
        return "❌"
    return "❓"


def _impact_icon(level: str) -> str:
    return {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(level.lower(), "⬜")


def _escape_md(text: str) -> str:
    """Escaped Pipe-Zeichen für Markdown-Tabellen."""
    return str(text).replace("|", "\\|")


def _author_short(author_str: str) -> str:
    """Kürzt lange Autorenlisten auf erste 3 Autoren."""
    authors = [a.strip() for a in author_str.split(" and ") if a.strip()]
    if len(authors) > 3:
        return "; ".join(authors[:3]) + " et al."
    return "; ".join(authors)


def _type_label(t: str) -> str:
    return {
        "empirical": "Empirisch",
        "review": "Review/Übersicht",
        "mixed": "Empirisch + Review",
        "practitioner": "Praxisorientiert",
    }.get(t.lower(), t.capitalize() if t else "Unbekannt")


def _etype_label(t: str) -> str:
    return {
        "book": "Buch",
        "incollection": "Buchkapitel",
        "inbook": "Buchkapitel",
        "techreport": "Bericht",
        "report": "Bericht",
        "misc": "Sonstiges",
        "online": "Online-Ressource",
        "phdthesis": "Dissertation",
        "mastersthesis": "Masterarbeit",
        "thesis": "Abschlussarbeit",
        "inproceedings": "Konferenzbeitrag",
        "conference": "Konferenzbeitrag",
    }.get(t.lower(), t.capitalize())


# ---------------------------------------------------------------------------
# Abschnitte
# ---------------------------------------------------------------------------

def _section_journals(journals: dict[str, JournalRating]) -> str:
    if not journals:
        return "## Zeitschriften-Artikel\n\n*Keine Zeitschriften-Artikel in der Bibliographie.*\n"

    # Sortiert nach VHB-Rating, dann ABS, dann Name
    _vhb_order = {"A+": 0, "A": 1, "B": 2, "C": 3, "D": 4, "nicht bewertet": 5}
    sorted_journals = sorted(
        journals.values(),
        key=lambda j: (
            _vhb_order.get(j.vhb_rating, 5),
            j.abs_rating == "nicht bewertet",
            j.name.lower(),
        ),
    )

    lines = [
        "## 1. Zeitschriften-Artikel",
        "",
        f"Gesamt: **{len(journals)}** unterschiedliche Zeitschriften",
        "",
        "| Zeitschrift | Fachrichtung | Typ | VHB | ABS | Impact | Peer Rev. | Score (PDF) | Schlüssel |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for j in sorted_journals:
        keys_short = ", ".join(f"`{k}`" for k in j.bib_keys[:3])
        if len(j.bib_keys) > 3:
            keys_short += f" (+{len(j.bib_keys) - 3})"
        pdf_info = f"{j.pdf_score} *({j.pdf_source})*" if j.pdf_score else "—"
        lines.append(
            f"| {_escape_md(j.name)} "
            f"| {_escape_md(j.research_field)} "
            f"| {_type_label(j.journal_type)} "
            f"| {j.vhb_rating} "
            f"| {j.abs_rating} "
            f"| {_impact_icon(j.impact_level)} {j.impact_level.capitalize()} "
            f"| {_bool_icon(j.peer_reviewed)} "
            f"| {pdf_info} "
            f"| {keys_short} |"
        )

    lines += [
        "",
        "### Anmerkungen zu den Zeitschriften",
        "",
    ]
    for j in sorted_journals:
        if j.notes or j.ai_assessed:
            ai_tag = " *(KI-bewertet)*" if j.ai_assessed else ""
            sub = f" — {j.sub_field}" if j.sub_field else ""
            lines.append(f"**{j.name}**{sub}{ai_tag}: {j.notes or '—'}")
            lines.append("")

    return "\n".join(lines)


def _section_non_journal(entries: list[NonJournalEntry]) -> str:
    if not entries:
        return "## 2. Bücher und sonstige Literatur\n\n*Keine Einträge.*\n"

    # Gruppieren nach Typ
    groups: dict[str, list[NonJournalEntry]] = {}
    for e in entries:
        label = _etype_label(e.entry_type)
        groups.setdefault(label, []).append(e)

    lines = [
        "## 2. Bücher und sonstige Literatur",
        "",
        f"Gesamt: **{len(entries)}** Einträge",
        "",
    ]

    for group_label, group_entries in sorted(groups.items()):
        lines += [
            f"### {group_label} ({len(group_entries)})",
            "",
            "| Schlüssel | Autor(en) | Titel | Jahr | Verlag/Institution |",
            "|---|---|---|---|---|",
        ]
        for e in sorted(group_entries, key=lambda x: x.year or "0000", reverse=True):
            publisher = e.publisher or e.institution or "—"
            lines.append(
                f"| `{e.key}` "
                f"| {_escape_md(_author_short(e.authors))} "
                f"| {_escape_md(e.title[:80])}{'…' if len(e.title) > 80 else ''} "
                f"| {e.year or '—'} "
                f"| {_escape_md(publisher)} |"
            )
        lines.append("")

    return "\n".join(lines)


def _section_authors(authors: dict[str, AuthorInfo]) -> str:
    # Nur Autoren mit ≥ 2 Werken oder AI-Bewertung
    notable = {
        name: info
        for name, info in authors.items()
        if info.papers_in_bib >= 2 or info.ai_assessed
    }

    if not notable:
        return "## 3. Autorenqualität\n\n*Keine Autoren mit ≥ 2 Werken in der Bibliographie.*\n"

    sorted_authors = sorted(notable.values(), key=lambda a: -a.papers_in_bib)

    lines = [
        "## 3. Autorenqualität",
        "",
        f"Autoren mit ≥ 2 Werken in der Bibliographie: **{len(notable)}**",
        "",
        "| Autor | Werke im Bib | Institution | Bekannt für | Einschätzung |",
        "|---|---|---|---|---|",
    ]

    for a in sorted_authors:
        ai_tag = " *(KI)*" if a.ai_assessed else ""
        lines.append(
            f"| {_escape_md(a.name)}{ai_tag} "
            f"| {a.papers_in_bib} "
            f"| {_escape_md(a.affiliation or '—')} "
            f"| {_escape_md(a.known_for[:80] if a.known_for else '—')} "
            f"| {_escape_md(a.quality_note[:100] if a.quality_note else '—')} |"
        )

    return "\n".join(lines)


def _section_summary(
    journals: dict[str, JournalRating],
    non_journal: list[NonJournalEntry],
    authors: dict[str, AuthorInfo],
) -> str:
    total = len(journals) + len(non_journal)
    peer_reviewed = sum(1 for j in journals.values() if j.peer_reviewed is True)
    high_impact = sum(1 for j in journals.values() if j.impact_level == "high")
    ai_count = sum(1 for j in journals.values() if j.ai_assessed)

    lines = [
        "## Zusammenfassung",
        "",
        f"| Metrik | Wert |",
        f"|---|---|",
        f"| Gesamteinträge | {total} |",
        f"| Zeitschriften-Artikel (einzigartige Journals) | {len(journals)} |",
        f"| Bücher / Sonstiges | {len(non_journal)} |",
        f"| Peer-reviewte Journals | {peer_reviewed} / {len(journals)} |",
        f"| Journals mit hohem Impact | {high_impact} / {len(journals)} |",
        f"| Autoren gesamt | {len(authors)} |",
        f"| AI-bewertete Journals | {ai_count} |",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Haupt-API
# ---------------------------------------------------------------------------

def generate(
    journals: dict[str, JournalRating],
    non_journal: list[NonJournalEntry],
    authors: dict[str, AuthorInfo],
    bib_path: str = "B_Literatur/literatur.bib",
) -> str:
    """Erstellt den vollständigen Markdown-Report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    header = f"""# Literaturqualitäts-Bericht

> **Generiert am:** {now}
> **Quelle:** `{bib_path}`
> Bewertungen mit *(KI-bewertet)* wurden mittels Claude (claude-haiku-4-5) ermittelt
> und sollten manuell verifiziert werden.
> VHB = VHB-JOURQUAL3 | ABS = ABS Academic Journal Guide

---

"""

    sections = [
        header,
        _section_summary(journals, non_journal, authors),
        "\n---\n",
        _section_journals(journals),
        "\n---\n",
        _section_non_journal(non_journal),
        "\n---\n",
        _section_authors(authors),
        "\n---\n",
        "*Dieser Report wird automatisch durch den Literature-Review-Service generiert.*  \n"
        "*Manuelle Änderungen werden beim nächsten Lauf überschrieben.*\n",
    ]

    return "\n".join(sections)
