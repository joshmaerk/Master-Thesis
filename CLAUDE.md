# CLAUDE.md

## Tech Stack

- Work in a German academic LaTeX master's thesis.
- Use `main.tex` as the thesis entry point and `variables.tex` for metadata.
- Use BibLaTeX APA with Biber; never use BibTeX as the backend.
- Treat Zotero as the bibliography source; treat `B_Literatur/*.bib` as generated build inputs.
- Maintain Python 3.10+ helper services under `services/` and Bash scripts under `scripts/`.

## Build & Dev Commands

- Set up TeX packages with `bash scripts/setup-tex.sh`.
- Build the thesis with `bash scripts/build.sh`.
- Sync bibliography with `python3 services/zotero_sync.py` only after Zotero changes.
- Validate agent documentation with `python3 scripts/check-agent-docs.py` after editing agent docs.
- Run service-specific commands from the repository root and read `.claudedocs/services.md` first.

## Core Code Style

- Write thesis prose in formal German academic style.
- Do not change scientific claims, empirical findings, or interpretations without explicit user instruction.
- Cite with `\parencite{...}` unless a task explicitly requires another BibLaTeX command.
- Keep edits small, reversible, and consistent with existing file names and structure.
- Do not manually edit `B_Literatur/*.bib`, secrets, audio files, transcripts, or coded interview data.
- Do not commit `.env`, ignored interview data, build artifacts, or generated private files.

## Code Behavior

- Read `.claudedocs/karpathy-guidelines.md` before any code change (Python, Bash, LaTeX macros).
- State assumptions explicitly; stop and ask when intent is unclear.
- Write the minimum code that solves the problem — no speculative features.
- Touch only what the task requires; mention but do not remove unrelated dead code.
- Define a verifiable success criterion before multi-step tasks.

## Text Generation

- When generating thesis prose, apply `/humanizer` to the draft before delivering the final text.
- After completing any task that touches thesis content or generates AI-assisted output, append a KI-Nutzung log entry:
  `python3 services/ki_log/ki_log.py add --kapitel "..." --tool "Claude Code (claude-sonnet-4-6)" --zweck "..." --pruefung "Manuell überprüft" --einfluss "..."`

## Referenced Docs

- Read `.claudedocs/architecture.md` when changing project structure, entry points, or chapter organization.
- Read `.claudedocs/latex-workflow.md` before substantial LaTeX, glossary, layout, or build changes.
- Read `.claudedocs/bibliography.md` and `.claudedocs/citations-and-sources.md` before bibliography or citation work.
- Read `.claudedocs/writing-style.md` and `.claudedocs/terminology.md` before editing thesis prose.
- Read `.claudedocs/services.md` before changing Python services, external API workflows, or requirements.
- Read `.claudedocs/quality-checks.md` before final checks or CI-related changes.
- Read `.claudedocs/git-workflow.md` before committing.
- Read `.claudedocs/user-guide.md` to choose the right command, agent, or script.
- Read `.claudedocs/karpathy-guidelines.md` before any code change (Python, Bash, LaTeX macros).
