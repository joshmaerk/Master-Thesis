---
paths:
  - "services/**/*.py"
---

# Python Services Rule

- Read `.claudedocs/services.md` before changing Python services.
- Preserve CLI behavior unless the task requires a change.
- Keep credentials in environment variables or `services/.env`; do not print or commit secrets.
- Prefer dry-run modes for external-write workflows.
