"""
Claude-basierte Pseudonymisierung von Interview-Transkripten.

Erkennt Personennamen und identifizierende Informationen, ersetzt sie durch
systematische Codes und speichert eine Zuordnungstabelle (.mapping.json).
Die Zuordnungstabelle bleibt lokal und wird nicht ins Git eingecheckt.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

_DETECT_PROMPT = """Du bist Datenschutzexperte für qualitative Forschungsinterviews.
Analysiere das folgende Transkript und identifiziere ALLE personenbezogenen Daten,
die pseudonymisiert werden müssen.

## Pseudonymisierungs-Regeln:

**Zu pseudonymisieren:**
- Vorname, Nachname oder Spitzname der befragten Person → Pseudonym: {interview_id}
- Vorname, Nachname anderer genannter Personen → KP-01, KP-02, KP-03, ...
- Name des Interviewers (falls im Transkript erwähnt) → (Interviewer)
- Spezifische Institutionsnamen, die die Person identifizierbar machen → Org-A, Org-B, ...

**NICHT pseudonymisieren:**
- Allgemeine Begriffe: "die Bank", "das Unternehmen", "die Abteilung"
- Produktnamen: ChatGPT, Copilot, M365, Teams, SharePoint, Notebook LM
- Allgemeine Regionen: Wien, Steiermark, Österreich, Deutschland, DACH
- Berufsbezeichnungen: Vorstand, Abteilungsleiter, Kundenberater
- Branchentypen: Raiffeisenbank (als Typ, nicht als spezifisches Institut)

## Ausgabe — NUR dieses JSON, ohne Erklärungen:
{
  "mappings": [
    {"original": "Max", "pseudonym": "IP-01", "type": "person_interviewee"},
    {"original": "Florian Brugger", "pseudonym": "KP-01", "type": "person_other"},
    {"original": "Joshua", "pseudonym": "(Interviewer)", "type": "person_interviewer"}
  ]
}

Typen: person_interviewee | person_other | person_interviewer | organization | location

Regeln für das JSON:
- Führe jede Eigennennung separat auf (Vorname allein UND vollständiger Name, falls beides vorkommt)
- Sortiere nach Häufigkeit des Vorkommens (häufigste zuerst)
- Falls nichts zu pseudonymisieren → {"mappings": []}

## Transkript:
{transcript}

## JSON-Ausgabe:"""


class Pseudonymizer:
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

    def pseudonymize(
        self,
        transcript: str,
        interview_id: str,
        mapping_output_path: Path,
    ) -> str:
        """
        Erkennt Namen im Transkript, ersetzt sie durch Codes und speichert die Zuordnung.
        Gibt das pseudonymisierte Transkript zurück.
        """
        mappings = self._detect_names(transcript, interview_id)

        if not mappings:
            print("      Keine pseudonymisierungspflichtigen Daten gefunden.")
            self._save_mapping(mappings, interview_id, mapping_output_path)
            return transcript

        print(f"      {len(mappings)} Einträge erkannt:")
        for m in mappings:
            print(f"        {m['original']!r} → {m['pseudonym']!r}  ({m['type']})")

        pseudonymized = self._apply_mappings(transcript, mappings)
        self._save_mapping(mappings, interview_id, mapping_output_path)
        return pseudonymized

    def _detect_names(self, transcript: str, interview_id: str) -> List[Dict[str, str]]:
        prompt = _DETECT_PROMPT.replace("{interview_id}", interview_id).replace("{transcript}", transcript)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()

        # Strip markdown code fences if present
        if "```json" in raw:
            raw = raw.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in raw:
            raw = raw.split("```", 1)[1].split("```", 1)[0].strip()

        try:
            data = json.loads(raw)
            return data.get("mappings", [])
        except json.JSONDecodeError as exc:
            print(f"      Warnung: JSON-Parsing fehlgeschlagen ({exc}). Pseudonymisierung übersprungen.")
            return []

    @staticmethod
    def _apply_mappings(text: str, mappings: List[Dict[str, str]]) -> str:
        # Sort longest first to avoid partial replacements (e.g. "Max Müller" before "Max")
        sorted_mappings = sorted(mappings, key=lambda m: len(m.get("original", "")), reverse=True)
        for mapping in sorted_mappings:
            original = mapping.get("original", "").strip()
            pseudonym = mapping.get("pseudonym", "").strip()
            if not original or not pseudonym:
                continue
            # Word-boundary replacement, case-insensitive
            pattern = r'(?<!\w)' + re.escape(original) + r'(?!\w)'
            text = re.sub(pattern, pseudonym, text, flags=re.IGNORECASE)
        return text

    def _save_mapping(
        self,
        mappings: List[Dict[str, str]],
        interview_id: str,
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "interview_id": interview_id,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "note": "VERTRAULICH — nicht ins Git einchecken. Enthält Klarnamen-Pseudonym-Zuordnung.",
            "mappings": mappings,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"      Zuordnungstabelle: {output_path}")
