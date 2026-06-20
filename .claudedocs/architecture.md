# Architecture

## Purpose

Use this document when changing project structure, entry points, chapter organization, or repository-level documentation.

## Repository layout

- `main.tex`: main thesis entry point and current LaTeX preamble.
- `variables.tex`: thesis metadata such as title, author, supervisor, and submission date.
- `A_Template/`: reusable template parts, cover page, abstract, declarations, and `glossary.tex`.
- `B_Literatur/`: generated bibliography files from Zotero; do not edit manually.
- `C_Inhalt/`: thesis chapters and appendix sources.
- `D_Extended Abstract/Extended Abstract/`: standalone extended-abstract LaTeX subproject; use the same general LaTeX rules.
- `services/`: Python helper services for Zotero, literature review, transcription, and transcript coding.
- `scripts/`: shell scripts for TeX setup and reproducible builds.
- `utils/`: working notes, exports, and archived drafts.
- `interviews/`: local interview audio, transcripts, and coding outputs; privacy-sensitive and git-ignored.

## Thesis structure

- Keep the existing chapter file structure unless explicitly asked to reorganize.
- Prefer wrapper files for chapters and separate subsection files for complex chapters.
- Keep thesis metadata in `variables.tex`.
- Keep acronym definitions in `A_Template/glossary.tex`.
- Do not move scientific content between chapters unless explicitly requested.

## Separation of concerns

- Keep scientific content in `C_Inhalt/`.
- Keep layout and reusable template components in `A_Template/` or the preamble in `main.tex`.
- Keep automation in `services/` or `scripts/`.
- Keep agent/project knowledge in `.claudedocs/`; use `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, and `.claude/agents/` as entry points or adapters.
