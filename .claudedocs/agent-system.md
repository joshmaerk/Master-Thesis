# Agent System

## Purpose

This document defines how shared project knowledge, Claude Code adapters, Codex instructions, commands, and subagents stay coordinated.

## Canonical knowledge ownership

| Topic | Canonical file | Other files may |
|---|---|---|
| Architecture | `.claudedocs/architecture.md` | Link to it |
| LaTeX workflow | `.claudedocs/latex-workflow.md` | Link to it |
| Bibliography workflow | `.claudedocs/bibliography.md` | Link to it |
| Citations and sources | `.claudedocs/citations-and-sources.md` | Link to it |
| Writing style | `.claudedocs/writing-style.md` | Link to it |
| Terminology | `.claudedocs/terminology.md` | Link to it |
| Quality checks | `.claudedocs/quality-checks.md` | Link to it |
| Git workflow | `.claudedocs/git-workflow.md` | Link to it |
| Services | `.claudedocs/services.md` | Link to it |
| User-facing command/agent guide | `.claudedocs/user-guide.md` | Link to it |

## Adapter files

- `CLAUDE.md`: compact Claude Code entry point.
- `AGENTS.md`: compact Codex and general agent entry point.
- `.claude/rules/*.md`: Claude Code path-scoped rules; keep short and link to `.claudedocs/`.
- `.claude/agents/*.md`: Claude Code subagent definitions; define role, tools, boundaries, and required docs.
- `.claude/commands/*.md`: user-facing Claude Code workflows; keep existing workflows and link to canonical docs.

## Consistency rules

- Do not duplicate full rules across adapter files.
- Use relative repository paths only.
- Do not reference non-existent files.
- Run `python3 scripts/check-agent-docs.py` after changing agent documentation.
- Prefer check scripts and CI over autonomous documentation loops.
- Do not add MCP servers, hooks, or external-write automation without explicit user approval.
