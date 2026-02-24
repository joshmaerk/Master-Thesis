# CLAUDE.md — Master-Thesis Repository Guide

This file provides \gls{AI} assistants with the context needed to work effectively in this repository.

## Project Overview

This is a **LaTeX academic master's thesis** written in German, submitted to:

- **Institution**: MCI | Die Unternehmerische Hochschule® (Executive Education)
- **Author**: Joshua Märker (Matriculation: 52416743)
- **Supervisor**: Assoz. FH-Prof. Mag. (FH) Martina Kohlberger, PhD
- **Submission**: 28.08.2026

### Research Topic

**Title**: *Zwischen Effizienzversprechen und Motivation: Generative KI in der Führungsarbeit*
(Between Efficiency Promise and Motivation: Generative \gls{AI} in Leadership Work)

**Research question**: How do middle managers in banks in the \gls{DACH} region (Germany, Austria, Switzerland) experience the use of generative \gls{AI} in decision-preparation processes motivationally — and under what conditions is this technology perceived as supporting or restricting autonomy, competence, and social relatedness?

**Theoretical framework**: Self-Determination Theory (\gls{SDT}) with its three basic psychological needs:
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
│
├── A_Template/               # Reusable template components
│   ├── 00_basics.tex         # Placeholder (preamble lives in main.tex)
│   ├── 01_deckblatt.tex      # Cover page layout
│   ├── 02_sperrvermerk.tex   # Confidentiality notice (currently commented out)
│   ├── 03_eidesstattliche_erklaerung.tex  # Statutory declaration (commented out)
│   ├── 04_abstract.tex       # Abstract (commented out)
│   ├── 06_abkuerzungsverzeichnis.tex      # List of abbreviations
│   └── 99_author_contribution.tex         # \gls{AI} usage declaration (commented out)
│
├── B_Literatur/
│   └── literatur.bib         # BibTeX bibliography — GENERATED via Zotero sync, do not edit manually
│
├── C_Inhalt/                 # Main thesis content
│   ├── 00_gliederung.tex     # Skeleton outline for chapters 4–6
│   ├── 01_introduction.tex   # Chapter 1: Introduction (COMPLETE)
│   ├── 02_theoretischerrahmen.tex  # Chapter 2 wrapper (COMPLETE)
│   ├── 02_Theorie/           # Chapter 2 subsections (COMPLETE)
│   │   ├── 02 01 generative ki.tex   # Generative \gls{AI} as sociotechnical system
│   │   ├── 02 02 fuehrungsarbeit.tex # Leadership work in middle management
│   │   ├── 02 03 sdt.tex             # Self-Determination Theory
│   │   └── 02 04 synthese.tex        # Theoretical synthesis
│   ├── 03_methodik.tex       # Chapter 3 wrapper (COMPLETE)
│   ├── 03_Methodik/          # Chapter 3 subsections (COMPLETE)
│   │   ├── 03_01 Forschungsdesign.tex  # Research design
│   │   ├── 03_02 Datenerhebung.tex     # Data collection
│   │   └── 03 03 bis 06 methodik.tex  # Analysis, quality criteria, ethics
│   ├── 04_Ergebnisse.tex     # Chapter 4: Results (SKELETON ONLY)
│   ├── 05_diskussion.tex     # Chapter 5: Discussion (SKELETON ONLY)
│   ├── 06_fazit.tex          # Chapter 6: Conclusion (SKELETON ONLY)
│   ├── 07_anhang.tex         # Appendix (mostly commented out)
│   └── Anhang/               # Appendix materials
│       ├── A1_Interviewleitfaden.tex           # Interview guide
│       ├── Interviewleitfaden_Masterarbeit_Maerker.pdf  # Interview guide PDF
│       ├── ai_ob_playground.tex                # Experimental/scratch content
│       └── ob_sdt_vertical_map.tex             # Conceptual map figure
│
├── services/                 # Helper scripts (run from repo root)
│   ├── zotero_sync.py        # Fetches Zotero library → B_Literatur/literatur.bib
│   ├── .env.example          # Template for ZOTERO_API_KEY / ZOTERO_USER_ID
│   ├── requirements.txt      # pip dependency: requests
│   └── README.md             # Setup and usage instructions
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

### Build Command

Standard LaTeX + Biber build sequence:

```bash
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

Or with `latexmk`:

```bash
latexmk -pdf -bibtex main.tex
```

### Output

- Entry point: `main.tex`
- Output: `main.pdf`
- Bibliography backend: **Biber** (not BibTeX) — the `biber main` step is required

### Draft Mode

The document currently has a DRAFT watermark enabled (`\usepackage{draftwatermark}`). To remove it before submission, comment out or remove:

```latex
\usepackage{draftwatermark}
\SetWatermarkText{DRAFT\\\DTMtoday\\\DTMcurrenttime}
\SetWatermarkScale{0.4}
\SetWatermarkLightness{0.95}
```

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

- Figures are labeled "Abbildung N:" (not "Figure N:X")
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

## Current Completion Status

| Chapter | Title | Status |
|---|---|---|
| 1 | Einführung (Introduction) | Complete |
| 2 | Theoretischer Hintergrund (Theory) | Complete |
| 3 | Methodisches Vorgehen (Methodology) | Complete |
| 4 | Ergebnisse (Results) | Skeleton only |
| 5 | Diskussion (Discussion) | Skeleton only |
| 6 | Zusammenfassung und Ausblick (Conclusion) | Skeleton only |
| Appendix | Interviewleitfaden, Einwilligungserklärung, Kategoriensystem | Partial |

Chapters 4–6 are declared in `main.tex` but currently commented out — the active placeholder is `C_Inhalt/00_gliederung.tex`.

---

## Git Workflow

### Branches

- `master` — primary development branch
- `claude/add-claude-documentation-cFVaJ` — Claude Code feature branch

### Commit Convention

Use clear, descriptive commit messages referencing the chapter or component changed:

```
Add Section 2.1: Generative KI als soziotechnisches System
Update methodology: Kuckartz analysis procedure
Fix bibliography: missing DOI for Deci & Ryan 2000
```

---

## Key Academic Context

Understanding the thesis content helps when assisting with writing or editing:

- **Target group**: Middle managers (mittleres Management) in \gls{DACH}-region banks
- **Technology studied**: Generative \gls{AI} tools (e.g., GPT-4, Claude, Gemini) used in decision-preparation workflows
- **Theoretical lens**: Self-Determination Theory (\gls{SDT}) — Deci & Ryan
  - Autonomy: perceived self-determination in decisions
  - Competence (Kompetenzerleben): perceived effectiveness and capability
  - Relatedness (Eingebundenheit): sense of connection and belonging
- **Research method**: Problem-centered interviews (Witzel, 2000), structured qualitative content analysis (Kuckartz, 2018)
- **Sector context**: German-speaking banking sector, regulatory environment (documentation obligations, accountability)

### Key Literature (frequently cited)

| Key | Reference |
|---|---|
| `deciWhatWhyGoal2000` | Deci & Ryan (2000) — \gls{SDT} basics |
| `deciSelfDeterminationTheoryWork2017` | Deci et al. (2017) — \gls{SDT} at work |
| `brynjolfssonGenerativeAIWork2025` | Brynjolfsson et al. — GenAI productivity |
| `bankinsMultilevelReviewArtificial2024` | Bankins et al. — multilevel \gls{AI} review |
| `kuckartz_qualitative_2018` | Kuckartz (2018) — qualitative content analysis |
| `floydManagingStrategicConsensus1997` | Floyd & Wooldridge — middle management |
