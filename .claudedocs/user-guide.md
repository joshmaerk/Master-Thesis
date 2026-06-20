# Agent and Automation User Guide

## Quick start

- Build the thesis: `bash scripts/build.sh`.
- Validate agent documentation: `python3 scripts/check-agent-docs.py`.
- Sync bibliography only after Zotero changes: `python3 services/zotero_sync.py`.
- Use `.claudedocs/` as the shared knowledge base for Claude, Codex, and other agents.

## Slash commands

| Task | Use | What happens | Main docs |
|---|---|---|---|
| Check citations | `/check-citations` | Finds broken and unused citation keys | `.claudedocs/citations-and-sources.md`, `.claudedocs/bibliography.md` |
| Draft a section | `/draft-section 4.2` | Creates a German academic working draft | `.claudedocs/writing-style.md`, `.claudedocs/terminology.md` |
| Review a section | `/review-section C_Inhalt/...` | Reviews style, terminology, citations, and LaTeX conventions | `.claudedocs/writing-style.md`, `.claudedocs/terminology.md` |
| Cross-check argument | `/cross-check` | Checks theory, findings, and discussion consistency | `.claudedocs/terminology.md`, `.claudedocs/citations-and-sources.md` |
| Extract literature gaps | `/lit-gaps` | Clusters research gaps from local literature metadata | `.claudedocs/citations-and-sources.md` |
| Transcribe audio | `/transcribe <audio>` | Runs the transcription service and writes ignored transcript output | `.claudedocs/services.md` |
| Code transcript | `/code-transcript <rtf>` | Runs transcript coding and writes ignored coding output | `.claudedocs/services.md`, `.claudedocs/terminology.md` |
| Pre-code transcript | `/pre-code <rtf>` | Produces an initial coding suggestion | `.claudedocs/terminology.md` |
| Suggest subcategories | `/subcategory-suggest HK1` | Suggests inductive subcategories from coded material | `.claudedocs/terminology.md` |

## Subagents

| Need | Agent |
|---|---|
| German academic style review | `academic-style-reviewer` |
| LaTeX build, structure, glossary, or compilation issues | `latex-build-maintainer` |
| Bibliography, citation keys, or source checks | `bibliography-citation-auditor` |
| Theory-method-results-discussion consistency | `research-consistency-checker` |
| Python helper services and requirements | `python-services-maintainer` |

## Scripts

| Script | Command | Purpose |
|---|---|---|
| TeX setup | `bash scripts/setup-tex.sh` | Installs required TeX packages via `tlmgr` |
| Thesis build | `bash scripts/build.sh` | Clean rebuild and timestamped PDF copy |
| Agent docs check | `python3 scripts/check-agent-docs.py` | Validates doc references, rule frontmatter, and subagent frontmatter |
| Zotero sync | `python3 services/zotero_sync.py` | Syncs Zotero bibliography into generated `.bib` files |
| Zotero tagging | `python3 services/zotero_tag_abstracts.py --collection-name 92_Abstract` | Tags Zotero collection; dry-run by default |
| Literature review | `python3 services/literature_review/analyze.py --check-apa7 --dry-run` | Checks literature metadata |
| Transcription | `python3 services/transcribe/transcribe.py <audio> --interview-id IP-01` | Transcribes audio via external APIs |
| Transcript coding | `python3 services/code_transcript/code_transcript.py <rtf> --interview-id IP-01` | Creates first coding draft |

## Sensitive data

- Do not commit `services/.env`, audio files, transcripts, coded interview data, build artifacts, or generated private outputs.
- Prefer dry-run modes before external writes.
- Manually verify transcript and coding outputs before using them as scientific evidence.

## Before committing agent-documentation changes

1. Run `python3 scripts/check-agent-docs.py`.
2. Run `git diff --check`.
3. Review `CLAUDE.md`, `AGENTS.md`, `.claudedocs/`, `.claude/rules/`, `.claude/agents/`, and changed Commands for duplicate or conflicting rules.
