# Transkriptions-Skill — Dresing & Pehl (2017)


## Gemeinsame Referenzen

Vor Ausführung bei Bedarf lesen:
- `.claudedocs/services.md`
- `.claudedocs/user-guide.md`

Transkribiere eine Audiodatei nach dem einfachen Transkriptionssystem von Dresing & Pehl (2017).
Sprecher werden automatisch zugewiesen (I: = Interviewer, B: = Befragte Person).
Ausgabe als RTF-Datei in interviews/transcripts/.

## Aufruf

```
/transcribe <pfad-zur-audiodatei> [--interview-id IP-01]
```

Beispiel:
```
/transcribe interviews/audio/interview_01.mp3 --interview-id IP-01
```

## Anweisungen

$ARGUMENTS

Führe folgende Schritte durch:

1. **Argument prüfen**: Lies den Pfad zur Audiodatei aus `$ARGUMENTS`. Falls kein Pfad angegeben,
   liste alle Dateien in `interviews/audio/` auf und frage den Nutzer, welche verarbeitet werden soll.

2. **Abhängigkeiten prüfen**: Stelle sicher, dass die Requirements installiert sind:
   ```
   pip install -r services/transcribe/requirements.txt
   ```

3. **API-Keys prüfen**: Stelle sicher, dass `services/.env` existiert und `OPENAI_API_KEY`
   sowie `ANTHROPIC_API_KEY` gesetzt sind. Falls nicht, weise den Nutzer auf `services/.env.example` hin.

4. **Transkription starten**:
   ```
   python3 services/transcribe/transcribe.py <audiodatei> [--interview-id <id>]
   ```

5. **Fortschritt verfolgen**: Zeige dem Nutzer an, welcher Chunk gerade verarbeitet wird
   und wie viele insgesamt zu verarbeiten sind.

6. **Ausgabe melden**: Teile dem Nutzer den Pfad zur fertigen RTF-Datei mit und weise
   auf MAXQDA-Import hin.

7. **Fehlerbehandlung**: Bei Fehlern (API-Key fehlt, ffmpeg nicht installiert, Datei nicht gefunden)
   diagnostiziere die Ursache und gib klare Handlungsanweisungen.

## Wichtige Hinweise

- Audiodateien in `interviews/audio/` werden NICHT ins Git eingecheckt (Datenschutz)
- Transkripte in `interviews/transcripts/` werden NICHT ins Git eingecheckt (Pseudonymisierung)
- Der Interviewleitfaden liegt unter `C_Inhalt/Anhang/Interviewleitfaden_Masterarbeit_Maerker.pdf`
- Bei mehreren Befragten in einem Interview: `--interview-id IP-01` (für B1:, B2: etc.)

## Transkriptionsstandard

Das Skript wendet alle 15 Regeln des einfachen Transkriptionssystems nach Dresing & Pehl (2017) an:
- Wörtliche Transkription (kein Zusammenfassen)
- Dialekt → Hochdeutsch
- I: / B: Sprecherkennzeichnung
- Zeitmarken #HH:MM:SS# am Absatzende
- VERSALIEN für Betonungen, ( …) für Pausen ≥3 Sek., (unv.) für Unverständliches
