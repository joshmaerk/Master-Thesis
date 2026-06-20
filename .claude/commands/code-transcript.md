# Erster Codierdurchgang — Strukturierende Qualitative Inhaltsanalyse (Kuckartz, 2018)


## Gemeinsame Referenzen

Vor Ausführung bei Bedarf lesen:
- `.claudedocs/services.md`
- `.claudedocs/terminology.md`
- `.claudedocs/user-guide.md`

Codiert ein RTF-Transkript aus `interviews/transcripts/` nach den vier deduktiven
Hauptkategorien HK0–HK3 (Erster Codierdurchgang, Phase 3 nach Kuckartz, 2018).
Ausgabe als LaTeX-Datei in `interviews/coded/`.

## Aufruf

```
/code-transcript <pfad-zum-rtf> [--interview-id IP-01] [--model <modell>] [--dry-run]
```

Beispiel:
```
/code-transcript interviews/transcripts/IP-01.rtf --interview-id IP-01
```

## Anweisungen

$ARGUMENTS

Führe folgende Schritte durch:

1. **Argument prüfen**: Lies den Pfad zum RTF-Transkript aus `$ARGUMENTS`. Falls kein Pfad
   angegeben, liste alle Dateien in `interviews/transcripts/` auf und frage den Nutzer,
   welche verarbeitet werden soll.

2. **Abhängigkeiten prüfen**: Stelle sicher, dass die Requirements installiert sind:
   ```
   pip install -r services/code_transcript/requirements.txt
   ```

3. **API-Key prüfen**: Stelle sicher, dass `services/.env` existiert und `ANTHROPIC_API_KEY`
   gesetzt ist. Falls nicht, weise den Nutzer auf `services/.env.example` hin.

4. **Codierung starten**:
   ```
   python3 services/code_transcript/code_transcript.py <rtf-datei> [--interview-id <id>] [--model <modell>] [--dry-run]
   ```

5. **Fortschritt verfolgen**: Zeige dem Nutzer an, welche Sinneinheit gerade verarbeitet
   wird und wie viele insgesamt zu verarbeiten sind.

6. **Ausgabe melden**: Teile dem Nutzer den Pfad zur fertigen LaTeX-Datei mit und weise
   auf folgende Nächste Schritte hin:
   - Kodierungen manuell prüfen und validieren (konsensuelle Kodierung nach Kuckartz)
   - `\input{interviews/coded/<interview-id>_kodierung}` in `C_Inhalt/Anhang/A2_Kategoriensystem.tex` einfügen
   - Nach Abschluss aller Interviews: induktive Subkategorienbildung (Phase 5 nach Kuckartz)

7. **Fehlerbehandlung**: Bei Fehlern (API-Key fehlt, RTF nicht lesbar, keine B:-Passagen)
   diagnostiziere die Ursache und gib klare Handlungsanweisungen.

## Wichtige Hinweise

- Codierte Transkripte in `interviews/coded/` werden NICHT ins Git eingecheckt (Datenschutz)
- Die KI-Kodierung ist eine wissenschaftliche Arbeitshypothese, **kein finales Ergebnis** —
  jede Zuweisung muss vom Forscher geprüft und ggf. korrigiert werden
- Mehrfachcodierungen (eine Sinneinheit erhält HK1 UND HK2) sind zulässig und erwünscht
- Nur B:-Beiträge (Interviewperson) werden codiert — I:-Zeilen (Interviewer) werden
  vollständig übersprungen
- Die Ausgabedatei kann nach Review per `\input` in `C_Inhalt/Anhang/A2_Kategoriensystem.tex`
  eingebunden werden
- Der Interviewleitfaden liegt unter `C_Inhalt/Anhang/Interviewleitfaden_Masterarbeit_Maerker.pdf`

## Kodierungsstandard

Das Skript wendet Phase 3 der inhaltlich-strukturierenden qualitativen Inhaltsanalyse
nach Kuckartz (2018) an:

| Code | Kategorie | Kerninhalt |
|------|-----------|-----------|
| HK0 | Übergreifende Kontextfaktoren | Org. Rahmenbedingungen, Regulatorik, biograf. Einbettung — motivational relevant, aber keiner SDT-Kategorie zuzuordnen |
| HK1 | Autonomieerleben | Selbstbestimmung, Entscheidungsfreiheit, Handlungsspielraum mit generativer KI (förderlich + frustrierend) |
| HK2 | Kompetenzerleben | Wirksamkeit, Expertise, professionelle Kompetenz mit generativer KI (förderlich + frustrierend) |
| HK3 | Soziale Eingebundenheit | Zugehörigkeit, Beziehungsqualität, Wertschätzung; Teaminteraktion, Führungsbeziehung |

Codiereinheit: **Sinneinheit** — thematisch zusammengehörende Passage eines B:-Sprecherbeitrags
(typisch 2–5 Sätze). Mehrfachkodierungen sind zulässig.
