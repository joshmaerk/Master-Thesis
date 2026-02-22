# Literature-Review-Service

Automatisierte Analyse der BibTeX-Bibliographie auf APA7-Konformität und Literaturqualität.

---

## Übersicht

| Funktion | AI benötigt | Beschreibung |
|---|---|---|
| APA7-Prüfung | ❌ Nein | Regelbasierte Pflichtfeld- und Formatprüfung |
| GitHub Issues | ❌ Nein | Erstellt Issues für nicht-konforme Einträge |
| Score-PDF-Extraktion | ✅ Ja | Liest Zeitschriften-Rankings aus PDFs |
| Journal-Bewertung | ✅ Ja | Bewertet Journals nicht in PDFs |
| Autoren-Bewertung | ✅ Ja | Bewertet wichtige Autoren (≥ 2 Werke) |

---

## Verzeichnisstruktur

```
services/literature_review/
├── analyze.py              # Hauptskript (Einstiegspunkt)
├── apa7_checker.py         # APA7-Regelprüfung (kein AI)
├── issue_manager.py        # GitHub Issue-Verwaltung (kein AI)
├── journal_rater.py        # Journal- & Autoren-Bewertung (AI)
├── report_generator.py     # Markdown-Report-Generator
├── .literatureignore       # Ausschlussliste (analog .gitignore)
├── scores/                 # ← Hier PDFs mit Rankings ablegen
│   └── .gitkeep
├── journal_report.md       # Generierter Report (nach Analyse)
├── requirements.txt
└── README.md
```

---

## Einrichtung

### Voraussetzungen

- Python 3.11+
- GitHub-Repository mit Issues aktiviert

```bash
pip install -r services/literature_review/requirements.txt
```

### Umgebungsvariablen

| Variable | Pflicht | Beschreibung |
|---|---|---|
| `GITHUB_TOKEN` | Für Issues | PAT oder Actions-Token mit `issues:write` |
| `GITHUB_REPOSITORY` | Für Issues | Format: `owner/repo` |
| `ANTHROPIC_API_KEY` | Für AI-Bewertung | Anthropic API-Schlüssel |

In GitHub Actions werden `GITHUB_TOKEN` und `GITHUB_REPOSITORY` automatisch gesetzt.

---

## Verwendung

### Via GitHub Actions (empfohlen)

**Workflow**: `.github/workflows/literature-review.yml`
**Auslösen**: Repository → Actions → **Literature Review** → Run workflow

Eingaben:

| Eingabe | Standard | Beschreibung |
|---|---|---|
| `check_apa7` | ✅ | APA7-Prüfung + Issue-Erstellung |
| `rate_journals` | ✅ | Journal-Bewertung + Report |
| `skip_ai` | ❌ | AI-Aufrufe überspringen |
| `dry_run` | ❌ | Testlauf ohne Schreiben |
| `bib_file` | `B_Literatur/literatur.bib` | Pfad zur BibTeX-Datei |
| `ignore_file` | `services/literature_review/.literatureignore` | Ausschlussliste |

**Secrets** (einmalig einrichten: *Settings → Secrets → Actions*):
- `ANTHROPIC_API_KEY` — nur für AI-Bewertung erforderlich

### Lokal ausführen

```bash
# Aus dem Repo-Stammverzeichnis

# Nur APA7-Prüfung (Dry-Run)
python3 services/literature_review/analyze.py --check-apa7 --dry-run

# Vollständige Analyse ohne AI
python3 services/literature_review/analyze.py \
    --check-apa7 --rate-journals --skip-ai

# Vollständige Analyse mit AI
export GITHUB_TOKEN=ghp_...
export GITHUB_REPOSITORY=joshmaerk/Master-Thesis
export ANTHROPIC_API_KEY=sk-ant-...
python3 services/literature_review/analyze.py \
    --check-apa7 --rate-journals

# Andere BibTeX-Datei
python3 services/literature_review/analyze.py \
    --rate-journals --bib pfad/zu/andere.bib
```

---

## Score-PDFs hinterlegen

Um Zeitschriften-Rankings aus externen Quellen einzulesen:

1. PDF-Datei in `services/literature_review/scores/` ablegen
2. Analyse starten (mit AI) — das Skript extrahiert automatisch Scores
3. Unterstützte Ranking-Systeme (werden automatisch erkannt):
   - VHB-JOURQUAL3
   - ABS Academic Journal Guide
   - Scimago (SJR)
   - Beliebige tabellarische Listen

Die PDFs werden **nicht** in Git eingecheckt (`.gitignore`).

---

## Ausschluss-Datei (`.literatureignore`)

Analog zu `.gitignore` können einzelne BibTeX-Schlüssel von der Analyse ausgenommen werden:

```
# Kommentare mit #
deci_what_2000          # exakter Schlüssel
berger*                 # Wildcard: alle Schlüssel die mit "berger" beginnen
*2006                   # alle Schlüssel die mit "2006" enden
noauthor_*              # alle Online-Ressourcen ohne Autor
```

---

## GitHub Issues

Für jeden nicht-APA7-konformen Eintrag wird ein Issue angelegt:

- **Titel**: `[APA7] \`key\` — N Fehler, M Warnungen`
- **Label**: `apa7-compliance` (wird automatisch erstellt)
- **Inhalt**: Detaillierte Problembeschreibung + BibTeX-Eintrag

**Deduplication**: Bestehende Issues (offen oder geschlossen) werden erkannt und nicht doppelt angelegt.

### APA7-Geprüfte Felder

| Entry-Typ | Pflichtfelder | Warnungen |
|---|---|---|
| `@article` | author, title, journal, year | volume, pages, doi |
| `@book` | title, publisher, year + (author oder editor) | address |
| `@incollection` | author, title, booktitle, publisher, year | editor, pages |
| `@misc` | title | author, year |
| `@techreport` | author, title, institution, year | — |
| DOI-Format | — | muss `https://doi.org/…` sein |
| URL ohne Datum | — | urldate fehlt |

---

## Generierter Report (`journal_report.md`)

Der Report enthält drei Abschnitte:

1. **Zeitschriften-Artikel**: Tabelle mit Fachrichtung, VHB/ABS-Rating, Peer-Review-Status, Impact
2. **Bücher und sonstige Literatur**: Aufgeteilt nach Typ (Buch, Bericht, Online, etc.)
3. **Autorenqualität**: Autoren mit ≥ 2 Werken im Bib, Institution, Bekannte Beiträge

KI-gestützte Bewertungen sind mit *(KI-bewertet)* gekennzeichnet und sollten manuell verifiziert werden.

---

## Fehlerbehebung

**`bibtexparser` ImportError**
→ `pip install bibtexparser`

**HTTP 403 bei Issue-Erstellung**
→ Token hat keine `issues:write`-Berechtigung

**`ANTHROPIC_API_KEY` nicht gesetzt**
→ AI-Schritte werden automatisch übersprungen; Analyse läuft weiter

**PDF-Scores werden nicht erkannt**
→ `pdfplumber` installiert? Text-extrahierbar (keine reinen Bild-PDFs)?
