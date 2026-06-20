# /review-section — Akademische Schreibqualität prüfen

Prüfe einen übergebenen Textabschnitt auf akademische Schreibqualität, SDT-Terminologie-
Konsistenz, korrekte Kuckartz-Terminologie und LaTeX-Konventionen.

## Anweisungen

$ARGUMENTS

Der Input ist entweder:
- Ein Dateipfad (z.B. `C_Inhalt/01_introduction.tex`) → gesamte Datei prüfen
- Ein Abschnitts-Identifikator (z.B. "4.2") → entsprechenden Abschnitt aus dem Dokument lesen
- Direkt eingefügter LaTeX-Text → sofort prüfen

Falls kein Argument, frage nach dem zu prüfenden Text.

### Prüfkriterien

**1. Akademischer Stil (Deutsch)**
- Keine Ich-Perspektive (`ich`, `wir`, `meiner Meinung`)
- Keine Umgangssprache oder Anglizismen ohne Markierung
- Keine Floskeln (`es ist wichtig zu betonen`, `wie oben erwähnt`)
- Korrekte Satzstruktur (kein Telegrammstil)
- Kein Konjunktiv bei empirischen Aussagen ohne explizite Unsicherheitsmarkierung

**2. SDT-Terminologie (konsistent mit Kap. 2)**
- "Erleben" statt "Gefühl" oder "Empfinden"
- "Grundbedürfnis" statt "Bedürfnis"
- "Autonomie" = Selbstbestimmung, NICHT Unabhängigkeit — bei Verwechslung markieren
- "Kompetenzerleben" statt "Kompetenz" (SDT betont Erleben, nicht Fähigkeit)
- "Bedürfnisbefriedigung" vs. "Bedürfnisfrustration" — klar unterscheiden
- "Soziale Eingebundenheit" statt "soziale Verbundenheit" oder "Zugehörigkeit"

**3. Kuckartz-Terminologie**
- "Hauptkategorie" (HK1–HK3), nicht "Code" oder "Theme"
- "Subkategorie", nicht "Unterkategorie" oder "Subcode"
- "Strukturierende qualitative Inhaltsanalyse", nicht "Inhaltsanalyse" allein
- "Kodierung", nicht "Codierung"
- "Interviewpartner:in" (geschlechtsneutral) statt "Befragte/r"
- Ergebnisdarstellung: phänomenologisch, keine Bewertung

**4. Zitationsformat (LaTeX/APA)**
- Alle empirischen Aussagen und Theoriezuschreibungen brauchen `\parencite{key}`
- Kein Satz endet mit Zitation ohne Punkt dahinter: `\parencite{key}.`
- Mehrere Quellen: `\parencite{key1, key2}` — alphabetisch
- Abkürzungen: erste Nennung via `\gls{sdt}`, danach `\acrshort{sdt}`

**5. LaTeX-Konventionen (Repo-spezifisch)**
- Doppelte Anführungszeichen: `\enquote{...}` statt `"..."` oder `„..."`
- Gedankenstrich: `--` (en-dash) statt `-`
- Thin Space bei Abkürzungen: `z.\,B.`, `d.\,h.`, `u.\,a.`
- Paragraf-Verweise: `(vgl. Abschnitt~\ref{...})`

### Ausgabe-Format

```
## Schreibqualitäts-Review: [Abschnittsbezeichnung]

### Kritische Probleme (müssen behoben werden)
1. [Zitat aus Text] → Problem: [Erklärung] → Vorschlag: [korrigierte Formulierung]
...

### Stilistische Empfehlungen (sollten behoben werden)
1. ...

### Terminologische Präzisierungen
1. ...

### Positiv: Was gut gelungen ist
- ...

### Gesamteinschätzung
[1-2 Sätze: Schreibreife, wichtigste Baustellen]
```

## Wichtige Hinweise

- Keine inhaltlichen Änderungen an wissenschaftlichen Aussagen vorschlagen
- Nur sprachlich-formale und terminologische Korrekturen
- Originalzitate aus Interviews (in Anführungszeichen) nicht bewerten
- Immer Begründung für jeden Hinweis angeben
