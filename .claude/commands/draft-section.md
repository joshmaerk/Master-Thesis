# /draft-section — SDT-strukturiertes Kapitel-Drafting


## Gemeinsame Referenzen

Vor Ausführung bei Bedarf lesen:
- `.claudedocs/writing-style.md`
- `.claudedocs/terminology.md`
- `.claudedocs/citations-and-sources.md`

Erstelle einen fundierten Arbeitsdraft für einen spezifischen Abschnitt der
ausstehenden Kapitel 4, 5 oder 6. Der Draft orientiert sich an der SDT-Operationalisierung
aus Kapitel 2 und der Kuckartz-Methodik aus Kapitel 3.

## Anweisungen

$ARGUMENTS

Der erste Parameter in `$ARGUMENTS` gibt den Zielabschnitt an, z.B.:
- `4.1` → Darstellung der Interviewpartner:innen
- `4.2` → Autonomieerleben im Kontext generativer KI
- `4.3` → Kompetenzerleben im Kontext generativer KI
- `4.4` → Soziale Eingebundenheit im Kontext generativer KI
- `4.5` → Übergreifende Deutungsmuster und situative Bedingungen
- `5.1` → Interpretation der Ergebnisse vor dem Hintergrund der SDT
- `5.2` → Einordnung in den Forschungsstand
- `5.3` → Implikationen für die Gestaltung von KI in Führungskontexten
- `5.4` → Limitationen der Studie
- `6.1` → Zusammenfassung der zentralen Befunde
- `6.2` → Beitrag zur Forschung
- `6.3` → Praktische Handlungsempfehlungen
- `6.4` → Zukünftiger Forschungsbedarf

Falls kein Argument übergeben wird, frage nach dem gewünschten Abschnitt.

### Vorbereitung (immer ausführen)

1. Lies die relevante Theoriestelle aus Kapitel 2:
   - `C_Inhalt/02_Theorie/02 03 sdt.tex` — SDT-Operationalisierung, Grundbedürfnisse
   - `C_Inhalt/02_Theorie/02 04 synthese.tex` — Integratives Rahmenmodell
2. Lies die Methodikbeschreibung:
   - `C_Inhalt/03_Methodik/03 03 bis 06 methodik.tex` — Kuckartz-Kategorien HK0–HK3
3. Lies den Interviewleitfaden:
   - `C_Inhalt/Anhang/A1_Interviewleitfaden.tex`
4. Falls Kapitel 5 oder 6: Lies `utils/2026-01-29_18_46_29_export.csv` für
   Literaturbezüge (Spalten: `Research Gap`, `Relevanz`, `Conclusions`)

### Draft-Erstellung nach Kapitel

**Kapitel 4 (Ergebnisse)**:
- Phänomenologische Beschreibung der Erlebnismuster
- Struktur: Einleitung → Befunddarstellung → Subkategorie-Differenzierung
- Zitat-Platzhalter: `[Zitat IP-XX: „..." (#HH:MM:SS)]`
- Häufigkeitsangaben: `[N von M Interviewpartner:innen]`
- Keine Interpretation — nur Beschreibung
- Kuckartz-Terminologie: "Hauptkategorie", "Subkategorie", "Kategorie HK1"

**Kapitel 5 (Diskussion)**:
- SDT-Interpretationsrahmen explizit machen
- Verknüpfung zu Befunden aus Kapitel 4: `(vgl. Abschnitt~4.X)`
- Literaturbezüge aus dem CSV: `\parencite{key}` für passende Quellen
- Spannungsfelder und Widersprüche thematisieren
- Differenzierung: Bedürfnisbefriedigung vs. Bedürfnisfrustration

**Kapitel 6 (Fazit)**:
- Prägnante Zusammenfassung ohne neue Argumente
- Beitrag zur SDT-Forschung konkret benennen
- Handlungsempfehlungen: praktisch, umsetzbar, DACH-Bankensektor-spezifisch
- Forschungsbedarf: methodisch und inhaltlich

### Ausgabe-Anforderungen

- Sprache: Deutsch, formell-akademisch
- Keine Ich-Perspektive, keine Umgangssprache
- `\parencite{key}` für alle Belege
- `\gls{ki}`, `\gls{sdt}`, `\acrshort{dach}` etc. für Abkürzungen (erste Nennung)
- LaTeX-formatierter Text, direkt einfügbar
- Am Ende: Liste der verwendeten `\parencite{}`-Schlüssel zur Überprüfung

## Wichtige Hinweise

- Der Draft ist ein Arbeitsentwurf — empirische Befunde müssen mit echten
  Interviewdaten ersetzt/ergänzt werden
- Zitat-Platzhalter markieren, wo konkrete Belege aus MAXQDA einzufügen sind
- SDT-Terminologie konsistent mit Kapitel 2 halten
- Kuckartz: "strukturierende qualitative Inhaltsanalyse", nicht "Grounded Theory"
