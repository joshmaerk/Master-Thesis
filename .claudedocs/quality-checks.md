# Quality Checks

## Scope

Use this document before finalizing changes, running CI-related checks, or validating agent documentation.

## Common checks

- LaTeX build: `bash scripts/build.sh`.
- Agent documentation consistency: `python3 scripts/check-agent-docs.py`.
- Git whitespace/conflict check: `git diff --check`.
- Citation check: use `/check-citations` or inspect citation keys against `B_Literatur/literatur.bib`.

## When to run checks

- Run `python3 scripts/check-agent-docs.py` after editing `CLAUDE.md`, `AGENTS.md`, `.claudedocs/**`, `.claude/agents/**`, `.claude/rules/**`, or `.claude/commands/**`.
- Run `bash scripts/build.sh` after changes to LaTeX content, bibliography, glossary, build scripts, or LaTeX configuration.
- Run service-specific commands or tests after changing Python services.

## GitHub Actions

- `.github/workflows/build-latex.yml` manually builds the thesis PDF.
- `.github/workflows/literature-review.yml` runs literature-review automation.
- Do not add CI workflows or external-write steps without clear benefit and explicit review.

## Privacy and secrets

- Do not print secrets from `.env` files.
- Do not commit local interview audio, transcripts, coding outputs, generated private files, or build artifacts.
