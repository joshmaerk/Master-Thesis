"""
Claude API-basierter Formatter für Dresing & Pehl (2017) Transkriptionsstandard.
Weist Sprecher zu (I: / B:) und wendet alle 15 Regeln des einfachen Systems an.
"""

from typing import Any, Dict, List

# Alle 15 Regeln des einfachen Transkriptionssystems nach Dresing & Pehl (2017)
_DRESING_PEHL_REGELN = """
Du bist ein professioneller Transkriptionist für qualitative Forschungsinterviews.
Deine Aufgabe: Ein Rohtranskript von OpenAI Whisper nach dem einfachen Transkriptionssystem
von Dresing & Pehl (2017) formatieren und Sprecher korrekt zuweisen.

## Die 15 Regeln des einfachen Transkriptionssystems (Dresing & Pehl, 2017):

**Regel 1 — WÖRTLICH:**
Es wird wörtlich transkribiert, also nicht lautsprachlich oder zusammenfassend. Der Wortlaut
wird vollständig übertragen.

**Regel 2 — WORTVERSCHLEIFUNGEN → SCHRIFTDEUTSCH:**
Wortverschleifungen werden an das Schriftdeutsch angenähert.
- „So'n Buch" → „so ein Buch"
- „hamma" → „haben wir"
- „wolln" → „wollen"
Die Satzform bleibt erhalten, auch bei syntaktischen Fehlern.
Beispiel: „Bin ich nach Kaufhaus gegangen." bleibt unverändert.

**Regel 3 — DIALEKT → HOCHDEUTSCH:**
Dialekte werden möglichst wortgenau ins Hochdeutsche übersetzt.
Wenn keine eindeutige Übersetzung möglich ist, bleibt der Dialektausdruck erhalten.
Beispiel: „heuer" (bair./öst. für „dieses Jahr") kann stehen bleiben.
„I mog des ned" → „Ich mag das nicht"

**Regel 4 — PARTIKELN TRANSKRIBIEREN:**
Umgangssprachliche Partikeln werden transkribiert: „gell", „gelle", „ne", „halt", „eben".

**Regel 5 — STOTTERN GLÄTTEN:**
Stottern wird geglättet oder ausgelassen. Abgebrochene Wörter werden ignoriert.
Wortdoppelungen nur erfassen, wenn sie als Stilmittel zur Betonung genutzt werden.
Richtig: „Das ist mir sehr, sehr wichtig."
Falsch: „Das das das ist wichtig." → „Das ist wichtig."

**Regel 6 — HALBSÄTZE MIT /:**
Halbsätze ohne Vollendung werden mit dem Abbruchzeichen „/" gekennzeichnet.
Beispiel: „Ich wollte eigentlich / aber dann hat sich das irgendwie ergeben."

**Regel 7 — INTERPUNKTION GLÄTTEN:**
Interpunktion wird zugunsten der Lesbarkeit geglättet. Bei kurzem Senken der Stimme oder
nicht eindeutiger Betonung wird eher ein Punkt als ein Komma gesetzt.
Sinneinheiten sollen beibehalten werden.

**Regel 8 — REZEPTIONSSIGNALE WEGLASSEN:**
„hm", „aha", „ja", „genau", „mhm" die den Redefluss NICHT unterbrechen → NICHT transkribieren.
Sie werden NUR transkribiert, wenn sie als direkte Antwort auf eine Frage dienen.
Beispiel Frage „Hat das gut geklappt?" → Antwort „Ja." bleibt stehen.

**Regel 9 — PAUSEN:**
Pausen von ca. 3 Sekunden oder mehr werden durch ( …) markiert.
Beispiel: „Ich habe dann ( …) also das war schon eine Herausforderung."

**Regel 10 — BETONUNGEN IN VERSALIEN:**
Besonders betonte Wörter oder Äußerungen werden durch VERSALIEN gekennzeichnet.
Beispiel: „Das ist mir SEHR wichtig." oder „Das war WIRKLICH überraschend."

**Regel 11 — ABSÄTZE & ZEITMARKEN:**
- Jeder Sprecherbeitrag erhält einen eigenen Absatz.
- Zwischen Sprechern gibt es eine freie, leere Zeile.
- Auch kurze Einwürfe werden in einem separaten Absatz transkribiert.
- Mindestens am Ende jedes Absatzes wird eine Zeitmarke eingefügt: #HH:MM:SS#
- Format: I: oder B: gefolgt vom Text und Zeitmarke am Ende.

**Regel 12 — NONVERBALES IN KLAMMERN:**
Emotionale nonverbale Äußerungen beider Personen, die die Aussage unterstützen oder
verdeutlichen, werden beim Einsatz in Klammern notiert.
Beispiele: (lacht), (seufzt), (zögert), (räuspert sich), (lacht leise)

**Regel 13 — UNVERSTÄNDLICHES:**
- Einzelne unverständliche Wörter: (unv.)
- Längere unverständliche Passagen mit Ursache: (unv., Mikrofon rauscht)
- Vermuteter Wortlaut mit Fragezeichen: (Axt?) oder (Prozess?)
- Bei unverständlichen Stellen ohne Zeitmarke in der letzten Minute → Zeitmarke setzen.

**Regel 14 — SPRECHERKENNZEICHNUNG:**
- Interviewende Person: I:
- Befragte Person: B:
- Bei mehreren Befragten: B1:, B2: oder mit Namen/Kürzel

**Regel 15 — RTF-FORMAT:**
(Wird vom Skript umgesetzt — du gibst nur den Transkripttext aus.)

## Ausgabeformat:

```
I: [Text des Interviewers] #HH:MM:SS#

B: [Antwort der befragten Person, kann mehrere Sätze umfassen.
Längere Beiträge können mehrere Zeilen haben.] #HH:MM:SS#

I: [Nächste Frage] #HH:MM:SS#
```

WICHTIG: Gib NUR den formatierten Transkripttext aus. Keine Erklärungen, keine Kommentare,
keine Überschriften. Nur das Transkript.
"""

_INTERVIEW_KONTEXT = """
## Kontext des Interviews:

Dies ist ein problemzentriertes Forschungsinterview für eine Masterarbeit zum Thema:
"Generative KI in der Führungsarbeit — motivationales Erleben im mittleren Bankmanagement"

**Der INTERVIEWER (I:)** ist der Forscher. Er stellt offene Fragen zu diesen Themenblöcken:
1. Berufliche Situation und konkreter KI-Einsatz im Alltag
2. Autonomieerleben: Selbstbestimmung, Entscheidungsfreiheit, Handlungsspielraum mit KI
3. Kompetenzerleben: Wirksamkeit, Expertise, professionelle Fähigkeiten durch/trotz KI
4. Soziale Eingebundenheit: Teaminteraktion, Führungsbeziehungen, Zugehörigkeitsgefühl
5. Abschluss: Persönliche Bewertung, Ausblick

Typische Interviewer-Phrasen (Erzählstimuli):
„Können Sie mir erzählen...", „Wie erleben Sie...", „Inwiefern...", „Was bedeutet das für Sie...",
„Wie hat sich...verändert?", „Welche Rolle spielt...", „Können Sie das noch etwas ausführen?",
„Was meinen Sie damit genau?"

**Die BEFRAGTE PERSON (B:)** ist eine Führungskraft im mittleren Management einer Bank
aus Deutschland, Österreich oder der Schweiz. Sie antwortet erzählerisch und ausführlicher.
Mögliche Dialekte: Bairisch, Österreichisch, Schweizerisch, Norddeutsch.

**Identifikationshilfen:**
- Fragen → Interviewer (I:)
- Längere Berichte, Beispiele, Erklärungen → Befragte Person (B:)
- Kurze Einwürfe wie „Interessant", „Genau", „Richtig" vom Interviewer → I:
- Bei Unsicherheit: Kontext des Gesprächsflusses nutzen
"""


class DresingPehlFormatter:
    def __init__(self, api_key: str, model: str = "claude-opus-4-8"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise RuntimeError(
                "anthropic ist nicht installiert. Bitte ausführen:\n"
                "  pip install -r services/transcribe/requirements.txt"
            )
        self.model = model

    @staticmethod
    def _format_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _segments_to_prompt_text(self, segments: List[Dict[str, Any]]) -> str:
        """Whisper-Segmente mit Timestamps für den Claude-Prompt aufbereiten."""
        lines = []
        for seg in segments:
            timestamp = self._format_time(seg["start"])
            lines.append(f"[{timestamp}] {seg['text']}")
        return "\n".join(lines)

    def format_chunk(
        self,
        raw_segments: List[Dict[str, Any]],
        previous_context: str = "",
        chunk_index: int = 0,
    ) -> str:
        """
        Formatiert einen Transkript-Chunk nach Dresing & Pehl.
        previous_context: Letzten ~300 Zeichen des vorherigen Chunks für Kontinuität.
        Gibt formatierten Transkripttext zurück.
        """
        raw_text = self._segments_to_prompt_text(raw_segments)

        kontext_abschnitt = ""
        if previous_context:
            kontext_abschnitt = (
                f"\n## Ende des vorherigen Abschnitts (nur für Kontext und Kontinuität):\n"
                f"{previous_context}\n"
                f"---\n"
            )

        prompt = (
            f"{_DRESING_PEHL_REGELN}\n\n"
            f"{_INTERVIEW_KONTEXT}\n"
            f"{kontext_abschnitt}\n"
            f"## Deine Aufgabe:\n\n"
            f"Formatiere das folgende Whisper-Rohtranskript nach den 15 Dresing & Pehl-Regeln.\n"
            f"Die Zeitangaben [HH:MM:SS] vor jedem Segment sind die globalen Startzeiten.\n\n"
            f"Anweisungen:\n"
            f"- Weise jeden Sprechbeitrag entweder I: oder B: zu\n"
            f"- Nutze Fragestruktur und Gesprächsfluss zur Sprecheridentifikation\n"
            f"- Falls der vorherige Abschnitt mitten in einem Beitrag endet, führe ihn fort\n"
            f"- Setze #HH:MM:SS# Zeitmarken am Ende jedes Absatzes\n"
            f"- Übersetze Dialekte ins Hochdeutsche (außer bei nicht übersetzbaren Begriffen)\n"
            f"- Markiere Betonungen durch VERSALIEN\n"
            f"- Markiere Pausen ≥3 Sek. mit ( …)\n"
            f"- Markiere Unverständliches mit (unv.)\n"
            f"- Gib NUR den Transkripttext aus — keine Erklärungen\n\n"
            f"## Whisper-Rohtranskript:\n{raw_text}\n\n"
            f"## Formatiertes Transkript nach Dresing & Pehl:"
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()

    def finalize(self, full_transcript: str) -> str:
        """
        Abschließender Qualitäts- und Konsistenz-Pass über das vollständige Transkript.
        Korrigiert Sprecherzuweisungsfehler, Zeitmarken-Lücken und Chunk-Übergänge.
        """
        prompt = (
            f"{_DRESING_PEHL_REGELN}\n\n"
            f"Du bekommst ein vollständiges Interview-Transkript, das in Abschnitten "
            f"verarbeitet wurde. Führe einen abschließenden Qualitätscheck durch:\n\n"
            f"1. Korrigiere offensichtliche Fehler in der Sprecherzuweisung (I: vs. B:)\n"
            f"2. Stelle sicher, dass alle Absätze eine Zeitmarke #HH:MM:SS# am Ende haben\n"
            f"3. Entferne Doppelungen an Chunk-Übergängen (gleiche Sätze zweimal)\n"
            f"4. Prüfe die Anwendung der 15 Regeln (Betonungen, Pausen, Nonverbales)\n"
            f"5. Stelle sicher, dass zwischen Sprechern immer eine Leerzeile steht\n\n"
            f"WICHTIG: Verändere den INHALT nicht. Nur Formatierung, Zeitmarken und "
            f"Sprecherzuweisung korrigieren.\n"
            f"Gib NUR das korrigierte Transkript aus.\n\n"
            f"## Transkript:\n{full_transcript}\n\n"
            f"## Korrigiertes Transkript:"
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()
