# /pre-code — KI-gestützte Erst-Kodierung von Interviewtranskripten


## Gemeinsame Referenzen

Vor Ausführung bei Bedarf lesen:
- `.claudedocs/terminology.md`
- `.claudedocs/services.md`

Analysiere ein Interviewtranskript und erstelle eine Erstkodierung nach den
Hauptkategorien (HK0–HK3) der strukturierenden qualitativen Inhaltsanalyse (Kuckartz 2018).
Die Kodierung dient als Ausgangspunkt für die manuelle Vertiefung in MAXQDA.

## Anweisungen

$ARGUMENTS

Der Input ist der Pfad zum RTF-Transkript (z.B. `interviews/transcripts/interview_01.rtf`)
oder der Interview-ID (z.B. `IP-01`). Falls kein Argument angegeben, liste alle
verfügbaren Transkripte in `interviews/transcripts/` auf.

### Vorbereitung

1. Lies die Kategoriendefinitionen:
   - `C_Inhalt/03_Methodik/03 03 bis 06 methodik.tex` — Definitionen HK0–HK3
   - `C_Inhalt/02_Theorie/02 03 sdt.tex` — SDT-Operationalisierung

2. Lies das Transkript vollständig. Fokus ausschließlich auf `B:`-Zeilen
   (Aussagen der befragten Person). `I:`-Zeilen (Interviewer) nur für Kontext.

### Kodierungsschema

Wende folgende Hauptkategorien an (Mehrfachkodierung erlaubt):

| Code | Kategorie | Kodieren wenn... |
|---|---|---|
| **HK1** | Autonomieerleben | Aussagen über Selbstbestimmung, Entscheidungsfreiheit, Handlungsspielraum, KI als einengend oder erweiternd für eigene Entscheidungen |
| **HK2** | Kompetenzerleben | Aussagen über Wirksamkeit, Expertise, Über-/Unterforderung, Zuschreibung von Leistung (an KI oder an sich selbst), berufliche Identität |
| **HK3** | Soziale Eingebundenheit | Aussagen über Teamdynamik, Führungsbeziehungen, Kommunikation, Zusammenarbeit, Zugehörigkeitsgefühl, Isolation |
| **HK0** | Kontextfaktoren | Aussagen über Org-Struktur, Regulierung (BaFin, DSGVO), Unternehmenskultur, biografische Hintergründe, die HK1–HK3 moderieren |

**Richtung der Kodierung (immer angeben)**:
- `+` = Bedürfnisbefriedigung (erleichternd, unterstützend, positiv)
- `-` = Bedürfnisfrustration (erschwerend, einschränkend, negativ)
- `~` = Ambivalent oder neutral

### Ausgabe-Format

```
## Erstkodierung: [Interview-ID] — [Datum des Transkripts]

### Übersicht
- Gesamt kodierte Passagen: X
- HK1 (Autonomie): X Passagen (Y+ / Z-)
- HK2 (Kompetenz): X Passagen (Y+ / Z-)
- HK3 (Eingebundenheit): X Passagen (Y+ / Z-)
- HK0 (Kontext): X Passagen

---

### Kodierte Passagen

[HK1+] #00:04:32#
> „[Originalzitat — max. 3 Sätze]"
Begründung: [1 Satz warum HK1+]

[HK2-] #00:09:17#
> „[Originalzitat]"
Begründung: [...]

[HK1-, HK2~] #00:15:44#  ← Mehrfachkodierung
> „[Originalzitat]"
Begründung: [...]

---

### Auffälligkeiten für MAXQDA-Folgekodierung
- [Passage X könnte auch HK3 sein — unklar ob Teamdynamik gemeint]
- [Starke Häufung von HK2- im Zeitfenster 20–35 Min]
- [Subkategorie-Hypothese: "Zuschreibungsambiguität" in HK2]
```

### MAXQDA-Export (optional)

Falls `$ARGUMENTS` `--maxqda` enthält: Zusätzlich eine komma-separierte
Exportdatei für den MAXQDA-Import ausgeben:

```
Zeitmarke,Kategorie,Richtung,Zitat
00:04:32,HK1,+,"[Zitat]"
...
```

## Wichtige Hinweise

- Transkripte liegen in `interviews/transcripts/` (git-ignoriert, lokal)
- Nur kodieren, nicht interpretieren — keine SDT-Schlussfolgerungen in dieser Phase
- Borderline-Fälle mit `?` markieren und in "Auffälligkeiten" erläutern
- Die KI-Kodierung ersetzt NICHT die menschliche Prüfung (Intersubjektivität!)
- Pseudonymisierung prüfen: Kein echter Name darf im Zitat vorkommen → IP-XX
- Ergebnis nicht committen (Datenschutz)
