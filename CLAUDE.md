# CLAUDE.md — Master-Thesis Repository Guide

This file provides AI assistants with the context needed to work effectively in this repository.

## Project Overview

This is a **LaTeX academic master's thesis** written in German, submitted to:

- **Institution**: MCI | Die Unternehmerische Hochschule® (Executive Education)
- **Author**: Joshua Märker (Matriculation: 52416743)
- **Supervisor**: Assoz. FH-Prof. Mag. (FH) Martina Kohlberger, PhD
- **Submission**: 28.08.2026

### Research Topic

**Title**: *Zwischen Effizienzversprechen und Motivation: Generative KI in der Führungsarbeit*
(Between Efficiency Promise and Motivation: Generative AI in Leadership Work)

**Research question**: How do middle managers in banks in the DACH region (Germany, Austria, Switzerland) experience the use of generative AI in decision-preparation processes motivationally — and under what conditions is this technology perceived as supporting or restricting autonomy, competence, and social relatedness?

**Theoretical framework**: Self-Determination Theory (SDT) with its three basic psychological needs:
- Autonomy (Autonomie)
- Competence / Perceived Competence (Kompetenzerleben)
- Social Relatedness (Soziale Eingebundenheit)

**Methodology**: Qualitative research design — problem-centered interviews (problemzentrierte Interviews), analyzed using structured qualitative content analysis (strukturierende qualitative Inhaltsanalyse) after Kuckartz (2018).

---

## Repository Structure

```
Master-Thesis/
├── main.tex                  # Entry point — full LaTeX preamble + document structure
├── variables.tex             # Thesis metadata (title, author, supervisor, dates)
├── KI Einsatz.tex            # Standalone AI usage documentation table (landscape)
│
├── A_Template/               # Reusable template components
│   ├── 00_basics.tex         # Placeholder (preamble lives in main.tex)
│   ├── 01_deckblatt.tex      # Cover page layout
│   ├── 02_sperrvermerk.tex   # Confidentiality notice (currently commented out)
│   ├── 03_eidesstattliche_erklaerung.tex  # Statutory declaration (commented out)
│   ├── 04_abstract.tex       # Abstract (active — included in main.tex)
│   ├── 06_abkuerzungsverzeichnis.tex      # Legacy abbreviation list (superseded by glossary.tex)
│   ├── glossary.tex          # Centralized acronym definitions (active — \newacronym entries)
│   └── 99_author_contribution.tex         # AI usage declaration (commented out)
│
├── B_Literatur/
│   └── literatur.bib         # BibTeX bibliography — GENERATED via Zotero sync, do not edit manually
│
├── C_Inhalt/                 # Main thesis content
│   ├── forschungsfrage.tex   # Research question excerpt (included where needed)
│   ├── 01_introduction.tex   # Chapter 1: Introduction (COMPLETE)
│   ├── 02_theoretischerrahmen.tex  # Chapter 2 wrapper (COMPLETE)
│   ├── 02_Theorie/           # Chapter 2 subsections (COMPLETE)
│   │   ├── 02 01 generative ki.tex   # Generative AI as sociotechnical system
│   │   ├── 02 02 fuehrungsarbeit.tex # Leadership work in middle management
│   │   ├── 02 03 sdt.tex             # Self-Determination Theory
│   │   ├── 02 04 synthese.tex        # Theoretical synthesis
│   │   └── fig_synthese.tex          # TikZ figure for synthesis model
│   ├── 03_methodik.tex       # Chapter 3 wrapper (COMPLETE)
│   ├── 03_Methodik/          # Chapter 3 subsections (COMPLETE)
│   │   ├── 03_01 Forschungsdesign.tex  # Research design
│   │   ├── 03_02 Datenerhebung.tex     # Data collection
│   │   └── 03 03 bis 06 methodik.tex  # Analysis, quality criteria, ethics
│   ├── 04_Ergebnisse.tex     # Chapter 4: Results (SKELETON — sections defined, content pending)
│   ├── 05_diskussion.tex     # Chapter 5: Discussion (SKELETON — sections defined, content pending)
│   ├── 06_fazit.tex          # Chapter 6: Conclusion (SKELETON — sections defined, content pending)
│   ├── 07_anhang.tex         # Appendix wrapper (mostly commented out)
│   └── Anhang/               # Appendix materials
│       ├── A1_Interviewleitfaden.tex           # Interview guide
│       └── Interviewleitfaden_Masterarbeit_Maerker.pdf  # Interview guide PDF
│
├── D_Extended Abstract/      # Separate sub-project: Extended Abstract
│   └── Extended Abstract/
│       ├── main.tex          # Extended Abstract entry point (standalone document)
│       ├── variables.tex     # Extended Abstract metadata
│       ├── .latexmkrc        # latexmk config for sub-project
│       ├── A_Template/       # Cover page and abstract template
│       ├── B_Literatur/      # Bibliography (own copy)
│       └── D_Extended Abstract/
│           └── extended_abstract_qualitativ.tex  # Extended Abstract content
│
├── interviews/               # Interview data (audio + transcripts git-ignored for privacy)
│   ├── audio/                # Source audio files (MP3/WAV/M4A — not committed)
│   └── transcripts/          # RTF transcripts output by transcribe service (not committed)
│
├── scripts/                  # Build and setup scripts (run from repo root)
│   ├── build.sh              # Clean rebuild → timestamped PDF in builds/
│   └── setup-tex.sh          # Install required TeX Live packages via tlmgr
│
├── services/                 # Automation scripts (run from repo root)
│   ├── zotero_sync.py        # Fetches Zotero library → B_Literatur/literatur.bib
│   ├── .env.example          # Template for API keys (ZOTERO, OPENAI, ANTHROPIC)
│   ├── requirements.txt      # pip dependency: requests
│   ├── literature_review/    # Literature quality analysis service
│   │   ├── analyze.py        # Entry point — APA7 check + journal rating
│   │   ├── apa7_checker.py   # Rule-based APA7 field validation
│   │   ├── issue_manager.py  # Creates GitHub Issues for non-compliant entries
│   │   ├── journal_rater.py  # AI-powered journal & author quality scoring
│   │   ├── report_generator.py  # Generates journal_report.md
│   │   ├── citation_analyzer.py # Citation usage analysis
│   │   ├── key_corrector.py  # BibTeX key correction utilities
│   │   ├── .literatureignore # Keys/patterns excluded from analysis (like .gitignore)
│   │   ├── journal_report.md # Generated report (committed after workflow run)
│   │   ├── journal_scores.json  # Cached journal scores
│   │   ├── scores/           # Place ranking PDFs here (VHB, ABS, SJR — not committed)
│   │   └── requirements.txt  # bibtexparser, anthropic, pdfplumber, requests
│   └── transcribe/           # Interview transcription service
│       ├── transcribe.py     # Entry point — transcribes audio → RTF
│       ├── audio_chunker.py  # Splits audio into overlapping chunks
│       ├── whisper_client.py # OpenAI Whisper API client
│       ├── dresing_pehl_formatter.py  # Claude formats transcript (Dresing & Pehl 2017)
│       ├── rtf_writer.py     # Writes formatted RTF output
│       └── requirements.txt  # openai, pydub, anthropic; requires ffmpeg
│
├── .github/
│   └── workflows/
│       ├── build-latex.yml       # Manual workflow: compile PDF (with/without draft watermark)
│       └── literature-review.yml # Manual workflow: APA7 check + journal rating
│
├── .latexmkrc                # latexmk config: biber backend + makeglossaries support
├── .gitignore                # Excludes build artifacts, PDFs, .env, audio, transcripts
│
└── utils/                    # Working files and archives
    ├── outline.tex           # Detailed structural outline (earlier planning)
    ├── literaturliste.txt    # Notes on literature
    ├── backup.txt            # Text backup
    ├── 2026-01-29_18_46_29_export.csv  # Data export (interview/coding data)
    └── archiv/               # Archived/superseded drafts of theory sections
```

---

## LaTeX Setup and Compilation

### Document Class and Key Packages

```latex
\documentclass[12pt,a4paper]{report}
```

| Package | Purpose |
|---|---|
| `biblatex` (APA, biber) | Bibliography in APA format, German labels |
| `geometry` | Margins: left 3.5cm, right/top/bottom 2.5cm |
| `setspace` | 1.5 line spacing (`\onehalfspacing`) |
| `titlesec` | Uniform heading sizes (all `\normalsize\bfseries`) |
| `fancyhdr` | Page numbers bottom-right, no header/footer lines |
| `tikz` | Flowcharts and diagrams |
| `tabularx`, `booktabs` | Professional tables |
| `csquotes` | Correct German quotation marks |
| `draftwatermark` | DRAFT watermark with date/time |
| `babel` (ngerman) | German language hyphenation and labels |
| `pdfpages` | Include external PDFs (e.g., appendix documents) |
| `glossaries` (acronym) | Acronym management — `\gls{}`, `\acrshort{}` |
| `datetime2` | Date/time in watermark |

### New Machine Setup

Install required TeX Live packages:

```bash
bash scripts/setup-tex.sh
```

This script uses `tlmgr` and handles `sudo` automatically if TeX Live is system-wide.

### Build Commands

**Recommended — clean rebuild with timestamped PDF:**

```bash
bash scripts/build.sh
```

This runs `latexmk -C` (clean) followed by a full rebuild and saves the result as:
```
builds/YYYYMMDD-HHMM Master Thesis Joshua Maerker.pdf
```

**Manual full build sequence:**

```bash
pdflatex main.tex
biber main
makeglossaries main
pdflatex main.tex
pdflatex main.tex
```

**Or with `latexmk` (reads `.latexmkrc` automatically):**

```bash
latexmk -pdf main.tex
```

The `.latexmkrc` configures Biber as the bibliography backend and adds `makeglossaries` as a custom dependency, so `latexmk` handles the full pipeline including acronyms.

### Output

- Entry point: `main.tex`
- Output: `main.pdf` (also copied to `builds/` by `build.sh`)
- Bibliography backend: **Biber** (not BibTeX) — required by `biblatex` APA style

### Draft Mode

The document has a DRAFT watermark enabled. To remove it before submission, comment out or remove these lines in `main.tex`:

```latex
\usepackage{draftwatermark}
\SetWatermarkText{DRAFT\\\DTMtoday\\\DTMcurrenttime}
\SetWatermarkScale{0.4}
\SetWatermarkLightness{0.95}
```

The `build-latex.yml` GitHub Actions workflow accepts a `draft_mode` input that automates this.

---

## Document Organization Conventions

### Chapter Structure

Chapters follow a two-level pattern:
1. **Wrapper file** (`C_Inhalt/0X_chaptername.tex`) — declares `\chapter{}` and inputs subsection files
2. **Subsection files** (`C_Inhalt/0X_Subfolder/`) — contain the actual section content

Example (Chapter 2):
```latex
% 02_theoretischerrahmen.tex
\chapter{Theoretischer Hintergrund}
\input{C_Inhalt/02_Theorie/02 01 generative ki}
\input{C_Inhalt/02_Theorie/02 02 fuehrungsarbeit}
...
```

All chapters 1–6 are currently **active** in `main.tex` (none commented out). Chapters 4–6 have their section structure defined but the body text is still to be written.

### Thesis Metadata

All thesis-level variables are centralized in `variables.tex`:

```latex
\ThesisTitle    % Full title
\Module         % "Master Thesis"
\AuthorName     % Author name
\MatriculationNumber
\Supervisor     % Supervisor name
\SubmissionDate % Submission date
```

To update metadata, edit only `variables.tex`.

### Glossary / Acronyms

Acronyms are defined in `A_Template/glossary.tex` and loaded in `main.tex` before `\begin{document}`:

```latex
\input{A_Template/glossary}
```

Usage in text:

| Command | First use | Subsequent |
|---|---|---|
| `\gls{ki}` | Künstliche Intelligenz (KI) | KI |
| `\acrshort{sdt}` | SDT | SDT |
| `\acrlong{sdt}` | Self-Determination Theory | Self-Determination Theory |

Key acronyms defined: `ki`, `genai`, `llm`, `rag`, `sdt`, `jdr`, `tam`, `utaut`, `dach`, `bafin`, `fma`, `finma`, `crr`, `dsgvo`, `erp`, `clv`.

To add a new acronym, edit `A_Template/glossary.tex` only.

### Bibliography

- File: `B_Literatur/literatur.bib`
- Style: APA (via `biblatex`)
- Language: `ngerman`
- Citation command: `\parencite{key}` (parenthetical, APA-style)
- Print: `\printbibliography[heading=bibintoc]` (appears in table of contents)

> **IMPORTANT — do not edit `literatur.bib` manually.**
> The file is the single source of truth exported from Zotero.
> Any manual changes will be overwritten on the next sync.
> To add or modify entries, use Zotero and then run:
> ```bash
> python3 services/zotero_sync.py
> ```
> See `services/README.md` for setup instructions.

### Heading Formatting

All heading levels (chapter, section, subsection) use identical formatting: `\normalfont\bfseries\normalsize`. This is a deliberate style choice per the thesis formatting guidelines — do not change heading font sizes.

Spacing above and below all headings: 0.5cm (`\titlespacing`).

### Page Numbering

- Front matter (ToC, lists, abbreviations): Roman numerals (I, II, III...)
- Main text (chapters 1–6 + bibliography + appendix): Arabic numerals restarting at 1

### Figures and Tables

- Figures are labeled "Abbildung N:" (not "Figure N:")
- Tables are labeled "Tabelle N:" (not "Table N:")
- Numbering is sequential (no chapter prefix): `\arabic{figure}`, `\arabic{table}`

---

## Writing Conventions

### Language

- Thesis text: **German** (formal academic register)
- Comments in `.tex` files: German or English
- Variable names, file names, LaTeX commands: English/LaTeX conventions

### Citations

Use `\parencite{}` for all in-text citations (APA parenthetical style):

```latex
\parencite{deciWhatWhyGoal2000}
\parencite{brynjolfssonGenerativeAIWork2025, noyExperimentalEvidenceProductivity2023}
```

### Special Characters

- The document declares `\DeclareUnicodeCharacter{202F}{\,}` to handle narrow no-break spaces (e.g., "z. B." or "z.\,B." in German abbreviations)
- Use `\,` for thin spaces in abbreviations: `z.\,B.`, `d.\,h.`, `u.\,a.`

### Paragraph Style

- No paragraph indentation (`\parindent=0pt`)
- 0.5em spacing between paragraphs (`\parskip=0.5em`)

---

## Services

### Zotero Sync

Syncs Zotero library to `B_Literatur/literatur.bib`. Requires `ZOTERO_API_KEY` and `ZOTERO_USER_ID` in `services/.env` (see `services/.env.example`).

```bash
python3 services/zotero_sync.py
```

### Literature Review Service

Automated analysis of `literatur.bib` for APA7 compliance and journal quality.

```bash
# From repo root — APA7 check only (dry run, no GitHub Issues created)
python3 services/literature_review/analyze.py --check-apa7 --dry-run

# Full analysis without AI calls
python3 services/literature_review/analyze.py --check-apa7 --rate-journals --skip-ai

# Full analysis with AI-powered journal rating
export ANTHROPIC_API_KEY=sk-ant-...
export GITHUB_TOKEN=ghp_...
export GITHUB_REPOSITORY=joshmaerk/Master-Thesis
python3 services/literature_review/analyze.py --check-apa7 --rate-journals
```

For non-compliant entries, GitHub Issues are created with label `apa7-compliance`. To exclude specific keys from analysis, add them to `services/literature_review/.literatureignore`.

**Via GitHub Actions**: Trigger the "Literature Review" workflow manually from the Actions tab.

### Transcription Service

Transcribes interview audio files to RTF format following the Dresing & Pehl (2017) simplified transcription system. Uses OpenAI Whisper for speech-to-text and Claude for formatting.

```bash
# Install system dependency: ffmpeg
# Install Python dependencies:
pip install -r services/transcribe/requirements.txt

# Transcribe an audio file
python3 services/transcribe/transcribe.py interviews/audio/interview_01.mp3 --interview-id IP-01
```

Requires in `services/.env`:
- `OPENAI_API_KEY` — for Whisper transcription
- `ANTHROPIC_API_KEY` — for Dresing & Pehl formatting via Claude
- `ANTHROPIC_MODEL` (optional, default: `claude-opus-4-8`)

Output: `interviews/transcripts/<filename>.rtf` (git-ignored for privacy/pseudonymization).

**Post-transcription checklist:**
1. Import RTF into MAXQDA
2. Manually verify against recording
3. Check speaker labels (`I:` / `B:`)
4. Verify pseudonymization (names → interview ID)

---

## GitHub Actions Workflows

### Build LaTeX PDF (`build-latex.yml`)

Manual trigger only (`workflow_dispatch`). Compiles `main.tex` using the full `pdflatex → biber → pdflatex → pdflatex` pipeline on Ubuntu. Accepts a `draft_mode` boolean input to optionally strip the watermark.

- Artifact: `thesis-pdf` (retained 30 days)
- On failure: uploads `main.log` and `main.blg`

### Literature Review (`literature-review.yml`)

Manual trigger. Runs `services/literature_review/analyze.py` with configurable inputs. Commits the generated `journal_report.md` back to the repository when not in dry-run mode.

Required secret: `ANTHROPIC_API_KEY` (only for AI-powered journal rating).

---

## Current Completion Status

| Chapter | Title | Status |
|---|---|---|
| 1 | Einführung (Introduction) | Complete |
| 2 | Theoretischer Hintergrund (Theory) | Complete |
| 3 | Methodisches Vorgehen (Methodology) | Complete |
| 4 | Ergebnisse (Results) | Skeleton — section headings defined, body text pending |
| 5 | Diskussion (Discussion) | Skeleton — section headings defined, body text pending |
| 6 | Zusammenfassung und Ausblick (Conclusion) | Skeleton — section headings defined, body text pending |
| Appendix | Interviewleitfaden, Einwilligungserklärung, Kategoriensystem | Partial |

All chapters are **included** in `main.tex`. The document compiles end-to-end with chapter skeletons in place.

### Chapter 4 Section Structure

1. Darstellung der Interviewpartner:innen
2. Autonomieerleben im Kontext generativer KI
3. Kompetenzerleben im Kontext generativer KI
4. Soziale Eingebundenheit im Kontext generativer KI
5. Übergreifende Deutungsmuster und situative Bedingungen

### Chapter 5 Section Structure

1. Interpretation der Ergebnisse vor dem Hintergrund der SDT
2. Einordnung in den Forschungsstand
3. Implikationen für die Gestaltung von KI in Führungskontexten
4. Limitationen der Studie

### Chapter 6 Section Structure

1. Zusammenfassung der zentralen Befunde
2. Beitrag zur Forschung
3. Praktische Handlungsempfehlungen
4. Zukünftiger Forschungsbedarf

---

## Git Workflow

### Branches

- `main` — primary development branch
- `claude/claude-md-docs-631qhq` — current Claude Code feature branch

### Commit Convention

Use clear, descriptive commit messages referencing the chapter or component changed:

```
Add Section 4.2: Autonomieerleben im Kontext generativer KI
Update methodology: Kuckartz analysis procedure
Fix bibliography: missing DOI for Deci & Ryan 2000
```

### Privacy and .gitignore

Audio files and transcripts in `interviews/` are intentionally excluded from git for data protection and pseudonymization compliance. Do not commit them. Score PDFs for journal rating (`services/literature_review/scores/`) and `.env` files with API keys are also excluded.

---

## Key Academic Context

Understanding the thesis content helps when assisting with writing or editing:

- **Target group**: Middle managers (mittleres Management) in DACH-region banks
- **Technology studied**: Generative AI tools (e.g., GPT-4, Claude, Gemini) used in decision-preparation workflows
- **Theoretical lens**: Self-Determination Theory (SDT) — Deci & Ryan
  - Autonomy: perceived self-determination in decisions
  - Competence (Kompetenzerleben): perceived effectiveness and capability
  - Relatedness (Eingebundenheit): sense of connection and belonging
- **Research method**: Problem-centered interviews (Witzel, 2000), structured qualitative content analysis (Kuckartz, 2018)
- **Sector context**: German-speaking banking sector, regulatory environment (documentation obligations, accountability)

### Key Literature (frequently cited)

| Key | Reference |
|---|---|
| `deciWhatWhyGoal2000` | Deci & Ryan (2000) — SDT basics |
| `deciSelfDeterminationTheoryWork2017` | Deci et al. (2017) — SDT at work |
| `brynjolfssonGenerativeAIWork2025` | Brynjolfsson et al. — GenAI productivity |
| `bankinsMultilevelReviewArtificial2024` | Bankins et al. — multilevel AI review |
| `kuckartz_qualitative_2018` | Kuckartz (2018) — qualitative content analysis |
| `floydManagingStrategicConsensus1997` | Floyd & Wooldridge — middle management |
