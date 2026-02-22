# AGENTS.md - Master-Thesis

Diese Datei gibt \gls{AI}-Coding-Agents die nötigen Projektregeln für dieses Repository.

## Projektkontext

- Typ: Masterarbeit (LaTeX, deutschsprachig)
- Einstiegspunkt: `main.tex`
- Metadaten: `variables.tex`
- Literaturdatenbank: `B_Literatur/literatur.bib`
- Build-Skripte:
  - Setup: `scripts/setup-tex.sh`
  - Build: `scripts/build.sh`

## Inhalt und Struktur

- `A_Template/`: wiederverwendbare Template-Bausteine
- `B_Literatur/`: Literaturdatenbank (Zotero-Export)
- `C_Inhalt/`: Kapitelinhalte der Arbeit
- `services/`: Hilfsskripte, u. a. Zotero-Sync
- `utils/`: Arbeits- und Archivdateien

## Schreib- und Inhaltsregeln

- Arbeitssprache im Fließtext: Deutsch.
- Wissenschaftlicher Stil, keine Umgangssprache.
- Zitationen über `biblatex` (APA) und `\parencite{...}`.
- Keine Änderungen an wissenschaftlichen Aussagen ohne expliziten Auftrag.

## LaTeX-Regeln

- Bibliographie-Backend: `biber` (nicht BibTeX).
- Relevante Pakete sind in der Präambel in `A_Template/00_basics.tex`.
- Vor Submission ggf. Draft-Wasserzeichen deaktivieren (`draftwatermark`).

## Build-Workflow

- Empfohlen für reproduzierbaren Build:
  - `bash scripts/build.sh`
- Das Skript:
  - führt einen sauberen Rebuild aus (`latexmk -C`, `latexmk -gg -pdf main.tex`)
  - legt eine timestamped PDF unter `builds/` ab.

## Bibliographie-Regeln (wichtig)

- `B_Literatur/literatur.bib` nicht manuell bearbeiten.
- Änderungen immer in Zotero durchführen und anschließend synchronisieren:
  - `python3 services/zotero_sync.py`

## Änderungen durch Agents

- Kleine, gezielte Änderungen bevorzugen.
- Bestehende Struktur/Dateinamen beibehalten.
- Bei neuen Skripten immer kurze Nutzungsdoku in `README.md` ergänzen.
- Keine destruktiven Git-Operationen.

