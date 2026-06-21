# Literatur-Aktualitätsreview — Durcharbeitungsliste
> Erstellt: 2026-06-21 | Grundlage: VHB-JOURQUAL3-Filterung + Webrecherche A/A+-Journals 2024–2026

---

## Priorität 1 — Sofort umsetzbar (Open Access, bereits im Bib)

Diese Quellen sind **bereits in `B_Literatur/literatur.bib` vorhanden**, werden aber im Text noch nicht zitiert. Kein Zotero-Sync, kein Download nötig.

---

### ☐ Doshi, Bell, Mirzayev & Vanneste (2025)
**BibTeX-Key:** `doshiGenerativeArtificialIntelligence2025`
**Journal:** Strategic Management Journal (VHB **A+**, ABS 4*)
**Titel:** Generative Artificial Intelligence and Evaluating Strategic Decisions
**DOI:** [10.1002/smj.3677](https://sms.onlinelibrary.wiley.com/doi/10.1002/smj.3677) — Open Access ✅
**Kernaussage:** Einzelne GenAI-Bewertungen strategischer Alternativen sind inkonsistent und verzerrt; aggregierte LLM-Evaluierungen nähern sich jedoch menschlichem Expertenurteil an. Studie mit 60 Business-Modellen, zwei Settings (KI-generiert vs. Wettbewerb).

**Wo einbauen:**
- **Kap. 2.1 (Generative KI):** als empirischer Beleg, dass GenAI in strategischen Entscheidungsprozessen sowohl Potenzial als auch Grenzen hat → stärkt das Janus-Argument
- **Kap. 2.4 (Synthese):** neben `tongJanusFaceArtificial2021` als aktueller SMJ-Beleg für die doppelgesichtige Wirkung
- **Kap. 5 (Diskussion):** Einordnung der eigenen Befunde vor dem Hintergrund, dass KI-Unterstützung bei strategischen Entscheidungen qualitativ noch begrenzt ist

**Formulierungsidee:** „Während \textcite{tongJanusFaceArtificial2021} den Deployment-Disclosure-Konflikt für KI-Feedback zeigen, belegen \textcite{doshiGenerativeArtificialIntelligence2025} in einer SMJ-Studie, dass aggregierte GenAI-Bewertungen zwar menschlichen Urteilen ähneln, Einzelevaluierungen jedoch inkonsistent bleiben — ein Befund, der die kognitive Entlastungserwartung mittlerer Führungskräfte relativiert."

---

### ☐ Gagné & Hewett (2025)
**BibTeX-Key:** `gagneAssumptionsHumanMotivation2025`
**Journal:** Journal of Management Studies (VHB **A**, ABS 4)
**Titel:** Assumptions about Human Motivation Have Consequences for Practice
**DOI:** [10.1111/joms.13092](https://onlinelibrary.wiley.com/doi/10.1111/joms.13092) — Open Access ✅
**Kernaussage:** Managementpraxis wird von Agency-Theory-Annahmen (Eigennutz, externe Kontrolle) dominiert, obwohl SDT-Evidenz zeigt, dass Motivationsinternalisierung und Autonomieunterstützung bessere Ergebnisse liefern. Plädoyer für SDT-basierte Praxisgestaltung.

**Wo einbauen:**
- **Kap. 2.3 (SDT):** als jüngste JMS-Verortung der SDT gegenüber dominanten Agency-Annahmen — stärkt die Relevanz und Aktualität der SDT als Rahmentheorie
- **Kap. 5 (Diskussion / Implikationen):** Überleitung zu Praxisempfehlungen: Führungskräfteentwicklung sollte SDT-Prinzipien verfolgen, nicht Agency-Kontrolllogik — besonders im KI-Implementierungskontext relevant

**Formulierungsidee:** „\textcite{gagneAssumptionsHumanMotivation2025} zeigen, dass Managementpraxis trotz jahrzehntelanger SDT-Evidenz weiterhin von Agency-Annahmen geprägt ist — ein Spannungsfeld, das sich im Kontext algorithmischer HR-Systeme verschärft \parencite{edwardsManagerialControlFeedback2024}."

---

## Priorität 2 — Neu, Open Access, noch nicht im Bib

Diese Quellen müssen zunächst **in Zotero importiert** und dann mit `python3 services/zotero_sync.py` synchronisiert werden.

---

### ☐ Kadolkar, Kepes & Subramony (2025)
**Journal:** Journal of Organizational Behavior (VHB **A**, ABS 4)
**Titel:** Algorithmic Management in the Gig Economy: A Systematic Review and Research Integration
**DOI:** [10.1002/job.2831](https://onlinelibrary.wiley.com/doi/full/10.1002/job.2831) — Open Access ✅
**Vol/Nr:** 46(7), S. 1057–1080
**Kernaussage:** Systematischer Review algorithmischen Managements in Plattformarbeit: Autonomieparadox (formelle Flexibilität vs. faktische Kontrolle), Motivationsrisiken, SDT-Bezüge. Zeigt, wie algorithmische Steuerung Bedürfnisfrustration erzeugt.

**Wo einbauen:**
- **Kap. 2.1 (Generative KI / algorithmisches Management):** als aktuellster JOB-Review-Beleg für die Kontrollwirkung algorithmischer Systeme auf Autonomieerleben
- **Kap. 2.4 (Synthese):** Verbindung zwischen algorithmischer Steuerung und SDT-Bedürfnisfrustration, die auf GenAI übertragbar ist

**Zotero-Import:** URL direkt in Zotero (Add by URL/DOI), dann `python3 services/zotero_sync.py`

---

## Priorität 3 — Paywall, manuell zu prüfen

Volltext nicht zugänglich. Titel/Abstract sind verfügbar; Bewertung ist **vorläufig — Volltext nicht geprüft**.

---

### ☐ Kim, Khoreva & Vaiman (2025)
**Journal:** Human Resource Management (VHB **A**, ABS 4)
**Titel:** Strategic Human Resource Management in the Era of Algorithmic Technologies: Key Insights and Future Research Agenda
**DOI:** [10.1002/hrm.22268](https://onlinelibrary.wiley.com/doi/full/10.1002/hrm.22268) — **Paywall/Login erforderlich**
**Vol/Nr:** 64, S. 447–464
**Kernaussage (Abstract):** Review des Forschungsstands zu algorithmischen Technologien in HRM: (1) Arbeitsgestaltung, (2) HR-Delivery, (3) Management von Tech-Mitarbeitenden. Forschungsagenda für strategisches HRM.
**Bewertung:** Vorläufig ✅ aktuell — erweitert Edwards et al. (2024) um strategische HRM-Perspektive; kein Widerspruch erwartet
**Relevanz für Thesis:** Mittel — Kontextualisierung des Algorithmus-Motivation-Nexus auf strategischer Ebene

**Prüf-Workflow:**
1. Volltext über Bibliothekszugang oder Sci-Hub prüfen
2. Falls zugänglich: Abstract-Einschätzung verifizieren
3. Ggf. als Kontextquelle in Kap. 2.1 ergänzen

---

### ☐ Stollberger, Anand & Dick (2025)
**Journal:** Human Relations (VHB **A**, ABS 4)
**Titel:** Capturing a Moving Target: Developing Research on and with AI for Human Relations
**DOI:** [10.1177/00187267251332075](https://journals.sagepub.com/doi/full/10.1177/00187267251332075) — **Paywall/Login erforderlich (SAGE)**
**Vol/Nr:** 78(5), S. 499–516
**Kernaussage (Abstract):** Editorial/Forschungsagenda zu KI als Untersuchungsgegenstand und als Forschungswerkzeug in der OB-Forschung; Methodendiskussion.
**Bewertung:** Vorläufig ✅ aktuell — thematisch randständig für die Thesis (eher methodologisch)
**Relevanz für Thesis:** Gering-Mittel — für Methodendiskussion (Kap. 3) oder Forschungsausblick (Kap. 6) möglicherweise nützlich

**Prüf-Workflow:** Nur bei Bedarf prüfen, nicht zwingend für den Argumentationsgang notwendig.

---

## Priorität 4 — Theoretische Einordnung / Kein Handlungsbedarf

Diese Quellen sind im Bib vorhanden und weiterhin aktuell — kein Änderungsbedarf.

| Quelle | Status | Hinweis |
|---|---|---|
| Bankins et al. (2024) — JOB A | ✅ aktuell | Bleibt State-of-the-Art; Kadolkar 2025 ergänzt, widerspricht nicht |
| Edwards et al. (2024) — HRM A | ✅ aktuell | Kim 2025 (Paywall) ergänzt strategischen Kontext |
| Tong et al. (2021) — SMJ A+ | ✅ aktuell | Durch Doshi 2025 (Prio 1) aktualisiert |
| Brynjolfsson et al. (2025) — QJE A+ | ✅ aktuell | Neueste Publikation; VHB-Rating KI-bewertet — manuell verifizieren |
| Klonek & Parker (2025) — JOB A | ✅ aktuell | 2025, kein Handlungsbedarf |
| Koponen et al. (2025) — JSR A | ✅ aktuell | 2025, kein Handlungsbedarf |
| Smith et al. (2025) — JOB A | ✅ aktuell | 2025, kein Handlungsbedarf |
| Nikolova et al. (2024) — Research Policy A | ✅ aktuell | Direkt forschungsrelevant; kein A/A+-Widerspruch |
| Chirkov et al. (2003) — JPSP A | ✅ aktuell | Grundlagentheorie; VHB-Rating KI-bewertet — manuell verifizieren |

---

## Priorität 5 — Forschungslücke aktiv nutzen

### ☐ Floyd & Wooldridge (1997) als expliziter Gap benennen

**Befund:** Es existiert kein empirisches A/A+-Paper (2024–2026) zur strategischen Rolle mittlerer Führungskräfte im Kontext generativer KI. Die klassische Floyd/Wooldridge-Rahmung (strategischer Einfluss, Boundary-Spanning) ist theoretisch unangefochten, aber empirisch noch nicht auf den GenAI-Kontext übertragen.

**Handlung:** In Kap. 5.2 (Einordnung in Forschungsstand) explizit als Forschungslücke formulieren:

> „Während die Rollen mittlerer Führungskräfte in strategischen Prozessen seit Floyd und Wooldridge \parencite{floydManagingStrategicConsensus1997,floydMiddleManagementInvolvement1992} theoretisch gut beschrieben sind, fehlen bislang empirische Untersuchungen, die diese Rollen im Kontext generativer KI-Systeme spezifisch analysieren. Die vorliegende Arbeit leistet einen Beitrag zur Schließung dieser Lücke."

---

## Manuell zu verifizierende VHB-Ratings (KI-bewertet)

Diese Ratings wurden im Repo als KI-ermittelt markiert und sollten per VHB-JOURQUAL3-Website geprüft werden:

| Journal | Rating im Repo | Zu prüfen via |
|---|---|---|
| Quarterly Journal of Economics | A+ *(KI)* | [vhbonline.org/vhb4you/jourqual](https://www.vhbonline.org/vhb4you/jourqual) |
| Journal of Personality & Social Psychology | A *(KI)* | s.o. |
| Applied Psychology | B *(KI)* | s.o. (nicht A/A+, nur zur Vollständigkeit) |
| Motivation and Emotion | B *(KI)* | s.o. (nicht A/A+, nur zur Vollständigkeit) |

---

## Workflow-Zusammenfassung

```
Prio 1 — Kein Download nötig
  → doshiGenerativeArtificialIntelligence2025 zitieren (Kap. 2.1 / 2.4 / 5)
  → gagneAssumptionsHumanMotivation2025 zitieren (Kap. 2.3 / 5)

Prio 2 — Zotero-Import + Sync
  → Kadolkar 2025 importieren: DOI 10.1002/job.2831
  → python3 services/zotero_sync.py

Prio 3 — Volltext-Check
  → Kim 2025 HRM (Paywall) — bei Bedarf über Bibliothek
  → Stollberger 2025 HR (Paywall) — nachrangig

Prio 4 — Kein Handlungsbedarf

Prio 5 — Schreiben
  → Gap Floyd/Wooldridge in Kap. 5.2 benennen

VHB-Verifikation
  → QJE und JPSP manuell prüfen
```
