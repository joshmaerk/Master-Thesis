# Git Workflow

## Scope

Use this document before staging, committing, or preparing a pull request.

## Rules

- Prefer small, focused commits.
- Use clear commit messages that mention the changed component or chapter.
- Do not run destructive Git operations.
- Do not commit secrets, `.env` files, interview audio, transcripts, coded interview data, build artifacts, or private generated outputs.
- Check `git status --short` before staging and before committing.
- Run relevant checks from `.claudedocs/quality-checks.md` before commit.

## Generated and sensitive files

- LaTeX build artifacts and PDFs are ignored unless explicitly whitelisted.
- `B_Literatur/literatur_backup_*.bib` is ignored.
- `interviews/audio/`, `interviews/transcripts/`, and `interviews/coded/` contain privacy-sensitive local data.
- `services/.env` contains credentials and must remain uncommitted.
