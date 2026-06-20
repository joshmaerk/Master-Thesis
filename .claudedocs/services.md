# Services

## Scope

Use this document before changing Python services, requirements, external API workflows, transcription, coding, Zotero automation, or literature-review scripts.

## Python baseline

- `services/README.md` documents Python 3.10+ for the Zotero service.
- Keep service scripts runnable from the repository root unless an existing README states otherwise.
- Keep CLI behavior explicit and documented.
- Prefer clear error messages over silent failures.

## Service areas

- `services/zotero_sync.py`: syncs Zotero metadata to `B_Literatur/literatur.bib`.
- `services/zotero_tag_abstracts.py`: tags Zotero collection `92_Abstract`; default is dry-run.
- `services/literature_review/`: APA7 and journal-quality analysis.
- `services/transcribe/`: interview transcription pipeline using audio input and external APIs.
- `services/code_transcript/`: first transcript-coding automation.

## External systems and credentials

- Store API credentials only in `services/.env` or environment variables.
- Do not read, print, commit, or modify secrets unless explicitly instructed.
- Do not write to Zotero, GitHub Issues, OpenAI, Anthropic, or other external systems unless the user explicitly requests the write operation.
- Prefer dry-run modes when available.

## Requirements and docs

- Keep each service's `requirements.txt` aligned with imports.
- If adding a new script, add concise usage documentation to `README.md` and any relevant service README.
- Do not add broad dependencies for narrow tasks.
