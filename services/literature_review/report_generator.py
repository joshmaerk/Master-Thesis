"""
Markdown-Report-Generator für die Literaturqualitätsbewertung.

Kein \gls{AI}/GenAI — rein datengetrieben aus den Bewertungsergebnissen.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from journal_rater import AuthorInfo, JournalRating, NonJournalEntry

if TYPE_CHECKING:
    from citation_analyzer import CitationStats


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
    # Nur Autoren mit ≥ 2 Werken oder \gls{AI}-Bewertung
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
# Zitationsfrequenz-Abschnitt
# ---------------------------------------------------------------------------

def _section_citation_stats(
    stats: CitationStats,
    bib_entries: list[dict],
    journals: dict[str, JournalRating] | None = None,
) -> str:
    """Abschnitt: Zitationsfrequenz-Analyse mit vollständiger Quellenliste."""

    bib_map: dict[str, dict] = {e["ID"]: e for e in bib_entries}

    # Nur Keys die tatsächlich in der .bib sind
    cited_keys = {k for k in stats.counts if k in bib_map}
    uncited_count = len(stats.uncited)
    total_bib = len(bib_map)
    total_citations = sum(stats.counts[k] for k in cited_keys)
    avg = total_citations / len(cited_keys) if cited_keys else 0.0
    pct_cited = len(cited_keys) / total_bib * 100 if total_bib else 0.0
    pct_uncited = uncited_count / total_bib * 100 if total_bib else 0.0

    # Reverse-Lookup: bib_key → JournalRating (für Qualitätsanzeige)
    key_to_journal: dict[str, JournalRating] = {}
    if journals:
        for jr in journals.values():
            for k in jr.bib_keys:
                key_to_journal[k] = jr

    unique_missing = len({key for key, _ in stats.missing})

    lines: list[str] = [
        "## 4. Zitationsfrequenz-Analyse",
        "",
        "### Zusammenfassung",
        "",
        "| Metrik | Wert |",
        "|---|---|",
        f"| Einträge in .bib | {total_bib} |",
        f"| Davon zitiert | {len(cited_keys)} ({pct_cited:.0f}%) |",
        f"| Nicht zitiert | {uncited_count} ({pct_uncited:.0f}%) |",
        f"| Gesamtzitationen im Text | {total_citations} |",
        f"| Ø Zitationen je Eintrag | {avg:.1f} |",
    ]
    if unique_missing:
        lines.append(f"| Fehlerhafte Keys im Text | {unique_missing} ⚠️ |")
    lines.append("")

    # ── Vollständige Quellenliste ─────────────────────────────────────────────
    lines += [
        "### Vollständige Quellenliste (zitierte Einträge)",
        "",
        "Sortiert nach Zitationshäufigkeit — VHB/ABS nur für Zeitschriften-Artikel:",
        "",
        "| # | Zit. | BibTeX-Key | Autor (Jahr) | Typ | VHB | ABS |",
        "|---|---|---|---|---|---|---|",
    ]

    cited_sorted = sorted(
        [(k, stats.counts[k]) for k in cited_keys],
        key=lambda x: x[1],
        reverse=True,
    )

    for rank, (key, count) in enumerate(cited_sorted, start=1):
        entry = bib_map.get(key, {})
        author = _author_short(entry.get("author", "—"))
        year = entry.get("year", "—")
        typ = _etype_label(entry.get("ENTRYTYPE", "article"))

        vhb, abs_r = "—", "—"
        if key in key_to_journal:
            jr = key_to_journal[key]
            vhb = jr.vhb_rating or "—"
            abs_r = str(jr.abs_rating) if jr.abs_rating else "—"

        lines.append(
            f"| {rank} | **{count}** | `{key}` "
            f"| {_escape_md(author)} ({year}) "
            f"| {typ} | {vhb} | {abs_r} |"
        )

    lines.append("")

    # ── Nicht zitierte Einträge ───────────────────────────────────────────────
    if stats.uncited:
        lines += [
            f"### Nicht zitierte Einträge ({len(stats.uncited)})",
            "",
            "| BibTeX-Key | Autor (Jahr) | Typ |",
            "|---|---|---|",
        ]
        for key in stats.uncited:
            entry = bib_map.get(key, {})
            author = _author_short(entry.get("author", "—"))
            year = entry.get("year", "—")
            typ = _etype_label(entry.get("ENTRYTYPE", ""))
            lines.append(
                f"| `{key}` | {_escape_md(author)} ({year}) | {typ} |"
            )
        lines.append("")
    else:
        lines += [
            "### Nicht zitierte Einträge",
            "",
            "_Alle Einträge werden im Text zitiert._ ✅",
            "",
        ]

    # ── Fehlerhafte Keys ─────────────────────────────────────────────────────
    if stats.missing:
        lines += [
            f"### ⚠️ Fehlerhafte Keys im Text ({unique_missing} eindeutige Keys)",
            "",
            "> Diese Keys kommen im Text vor, sind aber **nicht in der .bib-Datei**.",
            "> Bitte `key_corrector.py` ausführen.",
            "",
            "| Key | Datei | Zeile |",
            "|---|---|---|",
        ]
        seen_keys: set[str] = set()
        for key, loc in sorted(stats.missing, key=lambda x: (x[0], str(x[1].file), x[1].line)):
            marker = "" if key in seen_keys else ""
            seen_keys.add(key)
            lines.append(
                f"| `{key}` {marker}| `{loc.file.name}` | {loc.line} |"
            )
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Haupt-API
# ---------------------------------------------------------------------------

def generate(
    journals: dict[str, JournalRating],
    non_journal: list[NonJournalEntry],
    authors: dict[str, AuthorInfo],
    bib_path: str = "B_Literatur/literatur.bib",
    citation_stats: CitationStats | None = None,
    bib_entries: list[dict] | None = None,
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

    sections: list[str] = [
        header,
        _section_summary(journals, non_journal, authors),
        "\n---\n",
        _section_journals(journals),
        "\n---\n",
        _section_non_journal(non_journal),
        "\n---\n",
        _section_authors(authors),
    ]

    if citation_stats is not None and bib_entries is not None:
        sections += [
            "\n---\n",
            _section_citation_stats(citation_stats, bib_entries, journals),
        ]

    sections += [
        "\n---\n",
        "*Dieser Report wird automatisch durch den Literature-Review-Service generiert.*  \n"
        "*Manuelle Änderungen werden beim nächsten Lauf überschrieben.*\n",
    ]

    return "\n".join(sections)
