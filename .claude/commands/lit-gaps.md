# /lit-gaps — Research-Gaps aus Literatur extrahieren

Analysiere die kodierten Literaturmetadaten und erstelle ein strukturiertes Gerüst
der Research Gaps für Kapitel 5.2 (Einordnung in den Forschungsstand).

## Anweisungen

$ARGUMENTS

Führe folgende Schritte durch:

1. **CSV einlesen**: Lies `utils/2026-01-29_18_46_29_export.csv` vollständig ein.
   Relevante Spalten: `title`, `Research Gap`, `Theory`, `Relevanz`, `authors`.

2. **Gap-Extraktion**: Extrahiere aus der Spalte `Research Gap` alle identifizierten
   Forschungslücken. Ignoriere leere oder nichtssagende Einträge.

3. **Clustering nach SDT-Dimensionen**: Ordne jeden Gap einer oder mehreren der
   folgenden Kategorien zu:
   - **HK1 / Autonomie**: Gaps zu Selbstbestimmung, Entscheidungsspielraum,
     Kontrollwahrnehmung, Algorithmen und Volition
   - **HK2 / Kompetenz**: Gaps zu Expertise, Selbstwirksamkeit, beruflicher Identität,
     Zuschreibung von Leistung, Skill-Veränderung
   - **HK3 / Soziale Eingebundenheit**: Gaps zu Teamdynamik, Kommunikation,
     Führungsbeziehungen, Isolation, organisationaler Wertschätzung
   - **Übergreifend / Kontext**: Gaps zum Bankensektor, Regulierung, DACH-Raum,
     mittleres Management, qualitative Methoden

4. **Häufigkeit und Gewichtung**: Notiere, wie viele Einträge auf denselben Gap-Cluster
   hinweisen. Stark belegte Gaps (≥5 Nennungen) sind für Kapitel 5.2 besonders relevant.

5. **Positionierung der Thesis**: Beantworte für jeden Cluster: Adressiert diese Thesis
   den Gap direkt, indirekt oder gar nicht? Begründe kurz.

6. **Ausgabe — LaTeX-bereites Gerüst** für Kapitel 5.2:

   ```
   \section{Einordnung in den Forschungsstand}

   [Überblick: Was leistet diese Studie im Verhältnis zum Stand der Forschung?]

   \subsection*{Gaps zur Autonomiedimension}
   - Gap 1: [Beschreibung] → adressiert durch: [wie]
     Quellen: \parencite{key1, key2}
   ...

   \subsection*{Gaps zur Kompetenzdimension}
   ...

   \subsection*{Übergreifende und kontextuelle Lücken}
   ...

   \subsection*{Nicht adressierte Lücken (Limitationen)}
   ...
   ```

7. **Hinweis**: Falls `$ARGUMENTS` eine spezifische SDT-Dimension enthält
   (z.B. "autonomie" oder "hk2"), fokussiere die Ausgabe auf diese Dimension.

## Wichtige Hinweise

- Nur Quellen aus dem CSV verwenden, kein Hinzufügen externer Literatur
- Akademischer Stil, Deutsch, formell
- `\parencite{key}` für alle Zitationen — Schlüssel aus der `authors`-Spalte ableiten
  oder gegen `B_Literatur/literatur.bib` abgleichen
- Die Ausgabe ist ein Arbeitsdraft, der manuell überarbeitet werden soll
- Einträge mit hoher "Relevanz"-Bewertung priorisieren
