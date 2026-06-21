# /testing-expert — Python-Tests und Qualitätssicherung

Delegiert an den Subagent `testing-expert` (`.claude/agents/testing-expert.md`).

## Gemeinsame Referenzen

Vor Ausführung bei Bedarf lesen:
- `.claudedocs/services.md`

## Anweisungen

$ARGUMENTS

Starte den Subagent **testing-expert**, um Tests (pytest) für die Python-Dienste unter `services/` zu entwerfen, zu schreiben oder auszuführen. Ohne Argument: frage, welcher Dienst getestet werden soll.
