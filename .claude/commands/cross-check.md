# /cross-check — Theorie–Ergebnisse–Diskussion Konsistenzprüfung


## Gemeinsame Referenzen

Vor Ausführung bei Bedarf lesen:
- `.claudedocs/terminology.md`
- `.claudedocs/citations-and-sources.md`
- `.claudedocs/writing-style.md`

Prüfe die inhaltliche Konsistenz zwischen Kapitel 2 (Theorie), Kapitel 4 (Ergebnisse)
und Kapitel 5 (Diskussion). Identifiziere fehlende Verknüpfungen und nicht belegte
Interpretationen.

## Anweisungen

$ARGUMENTS

Optionale Argumente:
- Kein Argument → vollständige Prüfung aller drei Kapitelpaare
- `2-4` → Prüfe nur Theorie → Ergebnisse
- `4-5` → Prüfe nur Ergebnisse → Diskussion
- `2-5` → Prüfe Theorie → Diskussion (direkte Konsistenz ohne Ergebnisse)
- `hk1` / `hk2` / `hk3` → Fokussiere Prüfung auf eine SDT-Dimension

### Vorbereitung

Lies folgende Dateien:

**Theorie (Kap. 2)**:
- `C_Inhalt/02_Theorie/02 03 sdt.tex` — SDT-Grundbedürfnisse und Operationalisierung
- `C_Inhalt/02_Theorie/02 04 synthese.tex` — Integratives Rahmenmodell

**Ergebnisse (Kap. 4)**:
- `C_Inhalt/04_Ergebnisse.tex`

**Diskussion (Kap. 5)**:
- `C_Inhalt/05_diskussion.tex`

### Prüfschritt 1: Theorie → Ergebnisse

Für jedes in Kapitel 2 eingeführte SDT-Konstrukt:

| Konstrukt aus Kap. 2 | Belegt in Kap. 4? | Bewertung |
|---|---|---|
| Autonomie: Selbstbestimmung | ✓ / ✗ / teilweise | [Anmerkung] |
| Autonomie: Volition | ✓ / ✗ / teilweise | ... |
| Kompetenz: Wirksamkeitserleben | ... | ... |
| Kompetenz: Attributionsshift | ... | ... |
| Eingebundenheit: Teamdynamik | ... | ... |
| [Weitere Subfacetten] | ... | ... |

Konstrukte aus Kap. 2, die in Kap. 4 **nicht** auftauchen → als "Lücken" markieren.

### Prüfschritt 2: Ergebnisse → Diskussion

Für jede in Kapitel 4 präsentierte Befunddarstellung:

- Wird sie in Kapitel 5 interpretiert?
- Ist die Interpretation durch die SDT-Theorie aus Kap. 2 gedeckt?
- Gibt es Interpretationen in Kap. 5, die kein Fundament in Kap. 4 haben?

### Prüfschritt 3: Literaturankerpunkte

- Werden zentrale Literaturquellen aus Kap. 2 auch in Kap. 5 aufgegriffen?
- Gibt es in Kap. 5 Literaturbezüge, die in Kap. 2 nicht vorbereitet wurden?

### Ausgabe-Format

```
## Konsistenz-Report: Kapitel [X] ↔ Kapitel [Y]

### Konsistenz-Matrix

| SDT-Konstrukt | Kap. 2 | Kap. 4 | Kap. 5 | Status |
|---|---|---|---|---|
| Autonomie: Selbstbestimmung | ✓ | ✓ | ✓ | OK |
| Kompetenz: Attributionsshift | ✓ | ✗ | ✓ | ⚠️ Kap. 4 fehlt |
| Eingebundenheit: Isolation | ✓ | ✓ | ✗ | ⚠️ Kap. 5 fehlt |
| [Neue Kategorie aus Kap. 4] | ✗ | ✓ | ✓ | ⚠️ Kap. 2 nicht vorbereitet |

---

### Kritische Lücken

#### Theorie ohne Empirie (Kap. 2 → Kap. 4)
- [Konstrukt X]: In Kap. 2 ausführlich behandelt, in Kap. 4 nicht empirisch belegt.
  → Empfehlung: Entweder empirisches Material ergänzen oder Theoriestelle kürzen.

#### Empirie ohne Diskussion (Kap. 4 → Kap. 5)
- [Befund Y]: In Kap. 4 dargestellt, in Kap. 5 nicht interpretiert.
  → Empfehlung: In Kap. 5 aufgreifen oder als Limitierung erwähnen.

#### Interpretation ohne Fundament (Kap. 5 → Kap. 4)
- [Interpretation Z]: In Kap. 5 behauptet, aber kein Beleg in Kap. 4.
  → Empfehlung: Empirischen Beleg ergänzen oder Formulierung abschwächen.

---

### Gesamtbewertung
Konsistenzgrad: [hoch / mittel / niedrig]
Wichtigste Baustelle: [1 Satz]
```

## Wichtige Hinweise

- Bei Skelett-Kapiteln (Kap. 4–5 noch ohne Inhalt) ist eine Vollprüfung erst später sinnvoll
- Partial-Check (z.B. `2-4` nach Fertigstellung von Kap. 4) sinnvoller als Warten auf alles
- Nicht inhaltlich in die Argumentation eingreifen — nur strukturelle Inkonsistenzen aufzeigen
- Empfehlungen sind Vorschläge, keine Vorgaben
