# /check-citations — Zitationsvollständigkeit prüfen

Prüfe alle Zitationen in den LaTeX-Kapiteln auf Vollständigkeit und identifiziere
unkitierte, aber relevante Literatur aus der Bibliographie.

## Anweisungen

$ARGUMENTS

Führe folgende Schritte durch:

1. **\parencite-Schlüssel extrahieren**: Lies alle .tex-Dateien unter `C_Inhalt/` ein.
   Extrahiere alle vorkommenden `\parencite{...}`-Schlüssel (auch `\textcite{...}`,
   `\cite{...}`, `\autocite{...}`). Entferne Duplikate, sortiere alphabetisch.

2. **BibTeX-Schlüssel einlesen**: Lies `B_Literatur/literatur.bib` und extrahiere
   alle `@article`, `@book`, `@incollection` etc. mit ihren Schlüsseln.

3. **Fehlende Schlüssel (Broken Citations)**:
   Gibt es `\parencite{key}`-Aufrufe, deren Schlüssel NICHT in der .bib-Datei
   vorkommen? → Liste diese als kritische Fehler auf (verhindern korrekte Kompilierung).

4. **Unkitierte Quellen (Unused References)**:
   Zeige alle BibTeX-Schlüssel, die im Text NICHT zitiert werden.
   Pro unkitierter Quelle:
   - Titel + Autor(en) aus der .bib-Datei
   - SDT-Bezug (Autonomie/Kompetenz/Eingebundenheit/Kontext)
   - Vorschlag: In welchem Kapitel oder Abschnitt wäre diese Quelle sinnvoll?

5. **Ausgabe-Format**:

   ```
   ## Kritische Fehler (broken citations)
   - \parencite{falscherKey} — in: C_Inhalt/04_Ergebnisse.tex, Zeile ~X
     Mögliche Korrektur: [ähnlicher Schlüssel aus .bib]

   ## Unkitierte Quellen (41 gefunden)
   | Schlüssel | Autor(en) | Thema | SDT-Bezug | Empfohlener Einsatzort |
   |---|---|---|---|---|
   | brynjolfsson2025 | Brynjolfsson et al. | GenAI Produktivität | HK2 | Kap. 5.1 |
   ...

   ## Abdeckungsstatistik
   - Zitierte Quellen: X / Y total (Z%)
   - Kapitel mit den meisten Zitationen: ...
   - Kapitel ohne Zitationen: ...
   ```

6. **Falls `$ARGUMENTS` einen Schlüssel enthält**: Überprüfe gezielt diesen einen
   Schlüssel und melde seinen Status (vorhanden / fehlt / unkitiert).

## Wichtige Hinweise

- Nicht die .bib-Datei manuell bearbeiten — Änderungen nur via Zotero-Sync
- Broken Citations verhindern die LaTeX-Kompilierung → höchste Priorität
- Die Empfehlungen für unkitierte Quellen sind Vorschläge, keine Pflicht
