# Transkriptions-Skill — Dresing & Pehl (2017)

Transkribiere eine Audio- oder Videodatei nach dem einfachen Transkriptionssystem von Dresing & Pehl (2017).
Videodateien (MP4, MOV, MKV) werden automatisch in Audio konvertiert.
Sprecher werden automatisch zugewiesen (I: = Interviewer, B: = Befragte Person).
Ausgabe als RTF-Datei in interviews/transcripts/.

## Aufruf

```
/transcribe <pfad-zur-datei> [--interview-id IP-01]
```

Beispiele:
```
/transcribe interviews/audio/interview_01.mp3 --interview-id IP-01
/transcribe interviews/audio/interview_01.mp4 --interview-id IP-01
```

## Anweisungen

$ARGUMENTS

Führe folgende Schritte durch:

1. **Argument prüfen**: Lies den Pfad zur Datei aus `$ARGUMENTS`. Falls kein Pfad angegeben,
   liste alle Dateien in `interviews/audio/` auf und frage den Nutzer, welche verarbeitet werden soll.

2. **Abhängigkeiten prüfen**: Stelle sicher, dass die Requirements installiert sind:
   ```
   pip install -r services/transcribe/requirements.txt
   ```

3. **API-Keys prüfen**: Stelle sicher, dass `services/.env` existiert und `OPENAI_API_KEY`
   sowie `ANTHROPIC_API_KEY` gesetzt sind. Falls nicht, weise den Nutzer auf `services/.env.example` hin.

4. **Transkription starten**:
   ```
   python3 services/transcribe/transcribe.py <datei> [--interview-id <id>]
   ```
   Bei MP4/MOV/MKV wird die Audiospur automatisch via ffmpeg extrahiert (Schritt 0/4).
   Das Videooriginal bleibt erhalten — nicht löschen (siehe Hinweise).

5. **Fortschritt verfolgen**: Zeige dem Nutzer an, welcher Chunk gerade verarbeitet wird
   und wie viele insgesamt zu verarbeiten sind.

6. **Ausgabe melden**: Teile dem Nutzer den Pfad zur fertigen RTF-Datei mit und weise
   auf MAXQDA-Import hin.

7. **Fehlerbehandlung**: Bei Fehlern (API-Key fehlt, ffmpeg nicht installiert, Datei nicht gefunden)
   diagnostiziere die Ursache und gib klare Handlungsanweisungen:
   - ffmpeg fehlt → `brew install ffmpeg` (macOS) oder `sudo apt install ffmpeg` (Ubuntu)
   - OpenAI-Key fehlt → platform.openai.com → API Keys
   - Anthropic-Key fehlt → console.anthropic.com → API Keys

## Wichtige Hinweise

- Audiodateien in `interviews/audio/` werden NICHT ins Git eingecheckt (Datenschutz)
- Transkripte in `interviews/transcripts/` werden NICHT ins Git eingecheckt (Pseudonymisierung)
- **MP4/Video-Originale NICHT löschen**: Das Video dient für manuelle Körpersprache-Überprüfung.
  Auffällige nonverbale Reaktionen (Zögern, Aufleuchten, Unbehagen) können als Forschungsmemo
  festgehalten werden — besonders relevant für die SDT-Grundbedürfnisse Autonomie/Kompetenzerleben.
  MAXQDA unterstützt Video-Dokumente für optionale manuelle Video-Kodierung.
- Der Interviewleitfaden liegt unter `C_Inhalt/Anhang/Interviewleitfaden_Masterarbeit_Maerker.pdf`
- Bei mehreren Befragten in einem Interview: `--interview-id IP-01` (für B1:, B2: etc.)
- Für verbesserte Sprecher-Erkennung (Phase 2): `--diarize` nutzt pyannote.audio (benötigt HF-Token)

## Transkriptionsstandard

Das Skript wendet alle 15 Regeln des einfachen Transkriptionssystems nach Dresing & Pehl (2017) an:
- Wörtliche Transkription (kein Zusammenfassen)
- Dialekt → Hochdeutsch
- I: / B: Sprecherkennzeichnung
- Zeitmarken #HH:MM:SS# am Absatzende
- VERSALIEN für Betonungen, ( …) für Pausen ≥3 Sek., (unv.) für Unverständliches
- (lacht), (seufzt), (räuspert sich) für hörbare nonverbale Signale (Regel 12)

## Post-Transkriptions-Checkliste

Nach erfolgreicher RTF-Ausgabe:
1. RTF-Datei in MAXQDA importieren
2. Transkript manuell gegen Aufnahme gegenhören
3. Speaker-Zuweisung (I:/B:) überprüfen und korrigieren
4. Pseudonymisierung prüfen (Namen → Interview-ID, z.B. IP-01)
5. Bei Video-Interviews: Video einmalig durchsehen, auffällige nonverbale Reaktionen in Protokollnotiz festhalten
6. Videooriginal archivieren (NICHT löschen)
