# /subcategory-suggest — Induktive Subkategorie-Findung (Kuckartz Phase 5)


## Gemeinsame Referenzen

Vor Ausführung bei Bedarf lesen:
- `.claudedocs/terminology.md`
- `.claudedocs/writing-style.md`

Analysiere kodierte Interviewpassagen einer Hauptkategorie und schlage induktiv
Subkategorien vor. Unterstützt Phase 5 der strukturierenden qualitativen
Inhaltsanalyse nach Kuckartz (2018).

## Anweisungen

$ARGUMENTS

Mögliche Argumente:
- `HK1` oder `autonomie` → Subkategorien für Autonomieerleben vorschlagen
- `HK2` oder `kompetenz` → Subkategorien für Kompetenzerleben
- `HK3` oder `eingebundenheit` → Subkategorien für Soziale Eingebundenheit
- `HK0` oder `kontext` → Subkategorien für Kontextfaktoren
- Pfad zu einer Textdatei mit Passagen → diese direkt analysieren

Falls kein Argument: Frage nach der Hauptkategorie und nach dem Eingabeformat.

### Eingabe-Optionen

Der Skill akzeptiert Passagen in verschiedenen Formaten:

**Option A — MAXQDA-Export (CSV)**:
Eine CSV-Exportdatei aus MAXQDA mit kodierten Passagen.
Format: `Zeitmarke, Kategorie, Zitat, Interview-ID`

**Option B — Pre-code-Ausgabe**:
Die strukturierte Ausgabe aus dem `/pre-code`-Skill (direkt einfügen oder als Dateipfad).

**Option C — Manuell eingefügte Passagen**:
Direkt eingefügte Zitatsammlung (eine Passage pro Absatz, mit `#Zeitmarke#`).

### Analyse-Vorgehen

1. **Passagen einlesen**: Alle kodierten Stellen der angegebenen Hauptkategorie erfassen.

2. **Semantisches Clustering**: Welche Passagen beschreiben phänomenologisch
   ähnliche Erlebnismuster? Gruppiere nach inhaltlicher Nähe.
   - Minimum: 2 Passagen pro Cluster (Einzelfälle separat aufführen)
   - Prüfe sowohl HK+ (Befriedigung) als auch HK- (Frustration) als mögliche Subkategorien

3. **Subkategorie-Vorschläge**:
   Für jeden Cluster:
   - **Label**: Kurzer, prägnanter Name (2–5 Wörter, substantivisch)
   - **Definition**: 1–2 Sätze — was kodiert diese Subkategorie, was nicht?
   - **Ankerbeispiel**: 1 repräsentatives Zitat
   - **Abgrenzung**: Wo endet diese Subkategorie, wo beginnt eine andere?
   - **Häufigkeit**: Anzahl Passagen, Anzahl Interviews

4. **Hierarchie prüfen**: Können Subkategorien weiter differenziert werden?
   (nur wenn >5 Passagen in einem Cluster)

### Ausgabe-Format

```
## Subkategorie-Vorschläge für [HK-Bezeichnung]

Basierend auf X Passagen aus Y Interviews.

---

### SK1: [Label]
**Definition**: [1-2 Sätze]
**Richtung**: [+ / - / ~]
**Ankerbeispiel** (IP-XX, #HH:MM:SS):
> „[Zitat]"
**Abgrenzung**: Nicht hierher: [...]. Stattdessen: [...]
**Häufigkeit**: X Passagen, Y Interviews

---

### SK2: [Label]
...

---

### Einzelfälle (nicht kategorisierbar)
- IP-XX, #HH:MM:SS: „[Zitat]" → Begründung warum kein Cluster

---

### Methodische Notizen
- [Auffälligkeiten, Überlappungen, Zweifelsfälle]
- [Empfehlung für zweiten Kodiergang]
- [Subkategorien, die sich über HK-Grenzen erstrecken könnten]
```

### Iterativer Dialog

Nach der Ausgabe: Reagiere auf Feedback des Forschers:
- "SK2 ist zu weit gefasst" → aufteilen
- "SK1 und SK3 zusammenführen" → mergen und neu definieren
- "Neues Zitat gehört in SK4" → einordnen und ggf. Definition anpassen

Führe die Diskussion so lange fort, bis ein stabiles Subkategorie-System entsteht.

## Wichtige Hinweise

- Subkategorien müssen im Material begründet sein, nicht in der Theorie
- SDT-Theorie darf die Benennung inspirieren, aber nicht erzwingen
- Kuckartz: Subkategorien entstehen durch "Verfeinerung am Material" (Phase 5)
- Ziel: 3–8 Subkategorien pro Hauptkategorie (weniger = zu grob, mehr = zu kleinteilig)
- Transkripte/Passagen nicht committen (Datenschutz)
