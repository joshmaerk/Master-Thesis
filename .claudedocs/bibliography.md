# Bibliography Workflow

## Scope

Use this document before editing bibliography workflows, bibliography files, citation keys, Zotero sync scripts, or literature-review services.

## Source of truth

- Zotero is the authoritative source for bibliography metadata.
- `B_Literatur/*.bib` files are generated build inputs and must not be manually edited.
- Manual changes to generated `.bib` files can be overwritten by the next sync.

## Sync workflow

- Run Zotero sync from the repository root: `python3 services/zotero_sync.py`.
- Use `python3 services/zotero_sync.py --dry-run` to inspect without writing.
- Read `services/README.md` for Zotero API setup and troubleshooting.
- Keep Zotero credentials in `services/.env`; never commit this file.

## Validation

- After bibliography sync or citation changes, check for broken citations.
- Use `/check-citations` in Claude Code or inspect `\parencite{...}` keys against `B_Literatur/literatur.bib`.
- Run `bash scripts/build.sh` when bibliography or citation changes should be validated end-to-end.

## Restrictions

- Do not invent citation keys.
- Do not add or edit literature metadata directly in `.bib` files.
- Do not write to Zotero or external systems unless the user explicitly requests it.
