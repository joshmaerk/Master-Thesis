# AGENTS.md - Master-Thesis

Diese Datei gibt Coding-Agents die minimal nötigen Projektregeln für dieses Repository. Die kanonische, agentenübergreifende Wissensbasis liegt unter `.claudedocs/`.

## Projektkontext

- Typ: deutschsprachige LaTeX-Masterarbeit.
- Einstiegspunkt: `main.tex`.
- Metadaten: `variables.tex`.
- Literaturdatenbank: `B_Literatur/literatur.bib` und weitere generierte `.bib`-Dateien unter `B_Literatur/`.
- Build-Skripte:
  - Setup: `scripts/setup-tex.sh`.
  - Build: `scripts/build.sh`.

## Gemeinsame Agent-Dokumentation

- Lies `.claudedocs/architecture.md` bei Struktur-, Kapitel- oder Einstiegspunktänderungen.
- Lies `.claudedocs/latex-workflow.md` vor größeren LaTeX-, Glossar-, Layout- oder Build-Änderungen.
- Lies `.claudedocs/bibliography.md` und `.claudedocs/citations-and-sources.md` vor Bibliografie- oder Zitationsarbeiten.
- Lies `.claudedocs/writing-style.md` und `.claudedocs/terminology.md` vor Änderungen am wissenschaftlichen Fließtext.
- Lies `.claudedocs/services.md` vor Änderungen an Python-Services, Requirements oder externen API-Workflows.
- Lies `.claudedocs/quality-checks.md` vor Abschlussprüfungen oder CI-Änderungen.
- Lies `.claudedocs/git-workflow.md` vor Commits.
- Lies `.claudedocs/user-guide.md`, wenn unklar ist, welcher Command, Agent oder welches Skript zu verwenden ist.

## Kernregeln

- Arbeitssprache im Fließtext: Deutsch.
- Wissenschaftlicher Stil, keine Umgangssprache.
- Keine Änderungen an wissenschaftlichen Aussagen ohne expliziten Auftrag.
- Zitationen über BibLaTeX APA; Standard im Fließtext ist `\parencite{...}`.
- Bibliografie-Backend: Biber, nicht BibTeX.
- `B_Literatur/*.bib` nicht manuell bearbeiten; Änderungen in Zotero durchführen und danach `python3 services/zotero_sync.py` ausführen.
- Kleine, gezielte, reversible Änderungen bevorzugen.
- Bestehende Struktur und Dateinamen möglichst beibehalten.
- Bei neuen Skripten immer kurze Nutzungsdoku in `README.md` ergänzen.
- Keine destruktiven Git-Operationen.
- Keine Secrets, Audiodateien, Transkripte, Kodierungen oder Build-Artefakte committen.
