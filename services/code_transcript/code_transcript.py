#!/usr/bin/env python3
"""
Code-Transcript-Service für Masterarbeit-Interviews.
Führt den Ersten Codierdurchgang (Phase 3) der inhaltlich-strukturierenden
qualitativen Inhaltsanalyse nach Kuckartz (2018) durch.

Verwendung (vom Repo-Root):
    python3 services/code_transcript/code_transcript.py interviews/transcripts/IP-01.rtf
    python3 services/code_transcript/code_transcript.py interviews/transcripts/IP-01.rtf --interview-id IP-01
    python3 services/code_transcript/code_transcript.py interviews/transcripts/IP-01.rtf --dry-run

Umgebungsvariablen (in services/.env):
    ANTHROPIC_API_KEY  — Anthropic API-Schlüssel (Claude)
    ANTHROPIC_MODEL    — Claude-Modell (optional, Standard: claude-sonnet-4-6)
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


# ── Kategoriensystem (aus Kapitel 3, Methodikteil) ────────────────────────────

_SYSTEM_PROMPT = """Du bist ein qualitativ-wissenschaftlicher Kodierer für eine Masterarbeit über \
motivationales Erleben von Führungskräften im mittleren Bankmanagement beim Einsatz \
generativer KI. Forschungsrahmen: Self-Determination Theory (SDT) nach Deci & Ryan.

Du führst den ERSTEN CODIERDURCHGANG (Phase 3) der inhaltlich-strukturierenden qualitativen \
Inhaltsanalyse nach Kuckartz (2018) durch.

## Kategoriensystem (deduktive Hauptkategorien)

**HK0 – Übergreifende Kontextfaktoren**
Textstellen, die für das Verständnis der motivationalen Dynamik relevant sind, aber keiner \
der drei Grundbedürfniskategorien eindeutig zugeordnet werden können — etwa organisationale \
Rahmenbedingungen, regulatorische Kontexte oder biografische Einbettungen. Beispiele: \
Beschreibungen des institutionellen KI-Einführungsprozesses, regulatorischer Vorgaben im \
Bankensektor, eigener Berufsbiografie oder des allgemeinen Veränderungsdrucks.

**HK1 – Autonomieerleben**
Textstellen, in denen Interviewpartner:innen beschreiben, wie der Einsatz generativer KI \
ihr Erleben von Selbstbestimmung, Entscheidungsfreiheit und Handlungsspielraum beeinflusst. \
Dazu zählen sowohl autonomieförderliche Erfahrungen (erweiterte Gestaltungsspielräume, \
Entlastung von fremdbestimmten Aufgaben) als auch autonomiefrustrierende Erfahrungen \
(algorithmische Kontrolle, Einengung von Entscheidungskorridoren, erlebter Zwang zur \
KI-Nutzung).

**HK2 – Kompetenzerleben**
Textstellen, in denen Interviewpartner:innen beschreiben, wie generative KI ihr Erleben \
von Wirksamkeit, Expertise und professioneller Kompetenz beeinflusst. Dies umfasst \
kompetenzförderliche Erfahrungen (erweiterte Fähigkeiten, neue Kompetenzdomänen, verbesserte \
Ergebnisqualität) und kompetenzfrustrierende Erfahrungen (Expertiseentwertung, \
Attributionsverschiebung, Überforderung durch neue Anforderungen).

**HK3 – Soziale Eingebundenheit**
Textstellen, in denen Interviewpartner:innen beschreiben, wie generative KI ihr Erleben \
von Zugehörigkeit, Beziehungsqualität und Wertschätzung im organisationalen Kontext \
beeinflusst. Dies umfasst Erfahrungen von veränderter Teaminteraktion, Rollenverschiebungen \
in der Führungsbeziehung, organisationaler Wertschätzung sowie neue Formen der Zusammenarbeit \
oder Isolation.

## Codierregeln

1. Codiere AUSSCHLIESSLICH Passagen der befragten Person (B:) — niemals Interviewer-Fragen (I:).
2. Mehrfachcodierungen sind AUSDRÜCKLICH erlaubt: Eine Sinneinheit kann HK1 UND HK2 erhalten.
3. Vergib NUR dann eine Kategorie, wenn die Textstelle inhaltlich eindeutig auf das \
jeweilige Grundbedürfnis oder den Kontextfaktor verweist. Sei konservativ: lieber keine \
Zuweisung als eine zweifelhafte.
4. HK0 wird nur vergeben, wenn die Passage motivational kontextuell relevant ist, aber \
keiner spezifischeren Kategorie zugeordnet werden kann.
5. Wenn keine Kategorie zutrifft (rein faktische Beschreibung ohne motivationalen Bezug, \
Gesprächsorganisation, Begrüßung), gib ein leeres Array zurück.
6. Begründe jede Kategorienzuweisung mit 1–2 präzisen deutschen Sätzen, die die Verbindung \
zwischen Textstelle und Kategoriendefinition explizit benennen.

## Ausgabeformat (strikt JSON, kein Markdown, keine Erklärung außerhalb des JSON)

{
  "kodierungen": [
    {
      "hk": "HK1",
      "bezeichnung": "Autonomieerleben",
      "begründung": "Die Passage beschreibt, wie die Interviewperson..."
    }
  ],
  "memo": "Optionale kurze Anmerkung zur Textstelle (Ambiguität, Querverbindung, Auffälligkeit)."
}

Wenn keine Kategorie zutrifft:
{"kodierungen": [], "memo": "Keine kodierrelevante Passage (Begründung)."}"""

_USER_TEMPLATE = """## Interview-ID: {interview_id}
## Zeitmarke: {timestamp}
## Sinneinheit Nr. {unit_index}:

{text}

Kodiere diese Sinneinheit nach den definierten Hauptkategorien. Antworte ausschließlich mit validem JSON."""

_HK_LABELS = {
    "HK0": "Übergreifende Kontextfaktoren",
    "HK1": "Autonomieerleben",
    "HK2": "Kompetenzerleben",
    "HK3": "Soziale Eingebundenheit",
}

_TIMESTAMP_RE = re.compile(r"#(\d{2}:\d{2}:\d{2})#")
_SPEAKER_RE = re.compile(r"^(I|B\d*):\s*", re.IGNORECASE)


# ── Datenstrukturen ────────────────────────────────────────────────────────────

@dataclass
class Sinneinheit:
    index: int
    text: str
    timestamp: str
    raw_lines: List[str] = field(default_factory=list)


@dataclass
class Kodierung:
    hk: str
    bezeichnung: str
    begründung: str


@dataclass
class KodierErgebnis:
    sinneinheit: Sinneinheit
    kodierungen: List[Kodierung]
    memo: str
    fehler: Optional[str] = None


# ── Umgebungsvariablen ─────────────────────────────────────────────────────────

def _load_env() -> None:
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    candidates = [
        script_dir.parent / ".env",
        repo_root / ".env",
    ]
    for env_file in candidates:
        if env_file.exists():
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and key not in os.environ:
                            os.environ[key] = value
            print(f"  Umgebungsvariablen geladen aus: {env_file}")
            return
    print("  Hinweis: Keine .env-Datei gefunden. Nutze System-Umgebungsvariablen.")


def _require_env(key: str, hint: str = "") -> str:
    value = os.environ.get(key, "").strip()
    if not value:
        msg = f"\nFehler: Umgebungsvariable '{key}' ist nicht gesetzt."
        if hint:
            msg += f"\n{hint}"
        msg += "\nBitte services/.env nach dem Vorbild von services/.env.example befüllen."
        print(msg)
        sys.exit(1)
    return value


# ── RTF-Parser ─────────────────────────────────────────────────────────────────

class RTFParser:
    """Extrahiert B:-Sinneinheiten aus MAXQDA-kompatiblen RTF-Transkripten."""

    def parse(self, rtf_path: Path) -> List[Sinneinheit]:
        try:
            from striprtf.striprtf import rtf_to_text
        except ImportError:
            raise RuntimeError(
                "striprtf ist nicht installiert. Bitte ausführen:\n"
                "  pip install -r services/code_transcript/requirements.txt"
            )

        with open(rtf_path, "rb") as f:
            rtf_bytes = f.read()
        # Kodierung aus RTF-Header ableiten (\ansicpgNNNN), Fallback: cp1252
        cpg_match = re.search(rb'\\ansicpg(\d+)', rtf_bytes[:512])
        encoding = f"cp{cpg_match.group(1).decode()}" if cpg_match else "cp1252"
        rtf_content = rtf_bytes.decode(encoding, errors="replace")

        plain_text = rtf_to_text(rtf_content)
        lines = plain_text.splitlines()

        return self._segment(lines)

    def _segment(self, lines: List[str]) -> List[Sinneinheit]:
        units: List[Sinneinheit] = []
        current_speaker: Optional[str] = None
        current_lines: List[str] = []
        current_timestamp = ""
        unit_index = 0

        def flush(speaker: str, text_lines: List[str], ts: str) -> None:
            nonlocal unit_index
            if speaker and speaker.upper().startswith("B"):
                text = " ".join(t.strip() for t in text_lines if t.strip())
                if not text:
                    return
                for chunk in self._split_sinneinheiten(text):
                    unit_index += 1
                    units.append(Sinneinheit(
                        index=unit_index,
                        text=chunk,
                        timestamp=ts,
                        raw_lines=text_lines[:],
                    ))

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            speaker_match = _SPEAKER_RE.match(stripped)
            if speaker_match:
                flush(current_speaker, current_lines, current_timestamp)
                current_speaker = speaker_match.group(1)
                rest = stripped[speaker_match.end():]
                ts_match = _TIMESTAMP_RE.search(rest)
                current_timestamp = ts_match.group(1) if ts_match else ""
                clean = _TIMESTAMP_RE.sub("", rest).strip()
                current_lines = [clean] if clean else []
            else:
                ts_match = _TIMESTAMP_RE.search(stripped)
                if ts_match:
                    current_timestamp = ts_match.group(1)
                    clean = _TIMESTAMP_RE.sub("", stripped).strip()
                    if clean:
                        current_lines.append(clean)
                else:
                    current_lines.append(stripped)

        flush(current_speaker, current_lines, current_timestamp)
        return units

    @staticmethod
    def _split_sinneinheiten(text: str, max_chars: int = 900) -> List[str]:
        if len(text) <= max_chars:
            return [text]

        sentence_end = re.compile(r"(?<=[.!?])\s+")
        sentences = sentence_end.split(text)
        chunks: List[str] = []
        current = ""
        for sent in sentences:
            if current and len(current) + len(sent) + 1 > max_chars:
                chunks.append(current.strip())
                current = sent
            else:
                current = (current + " " + sent).strip() if current else sent
        if current:
            chunks.append(current.strip())
        return chunks if chunks else [text]


# ── Kuckartz-Kodierer (Claude API) ────────────────────────────────────────────

class KuckartzCoder:
    """Codiert Sinneinheiten nach HK0–HK3 via Anthropic Claude API."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise RuntimeError(
                "anthropic ist nicht installiert. Bitte ausführen:\n"
                "  pip install -r services/code_transcript/requirements.txt"
            )
        self.model = model

    def code(self, unit: Sinneinheit, interview_id: str, dry_run: bool = False) -> KodierErgebnis:
        user_prompt = _USER_TEMPLATE.format(
            interview_id=interview_id,
            timestamp=unit.timestamp or "unbekannt",
            unit_index=unit.index,
            text=unit.text,
        )

        if dry_run:
            print(f"\n{'─'*60}")
            print("  [DRY-RUN] System-Prompt:")
            print(_SYSTEM_PROMPT[:300] + "...")
            print(f"\n  [DRY-RUN] User-Prompt für Sinneinheit {unit.index}:")
            print(user_prompt)
            return KodierErgebnis(
                sinneinheit=unit,
                kodierungen=[Kodierung("HK1", "Autonomieerleben", "[DRY-RUN — kein API-Aufruf]")],
                memo="DRY-RUN",
            )

        raw = ""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw = response.content[0].text.strip()
            # Markdown-Fences entfernen (Claude gibt trotz Anweisung gelegentlich ```json...``` aus)
            if raw.startswith("```"):
                raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw, flags=re.DOTALL).strip()
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            return KodierErgebnis(
                sinneinheit=unit,
                kodierungen=[],
                memo="",
                fehler=f"JSON-Parsing fehlgeschlagen: {exc}\nAntwort: {raw[:200]}",
            )
        except Exception as exc:
            return KodierErgebnis(
                sinneinheit=unit,
                kodierungen=[],
                memo="",
                fehler=f"API-Fehler: {exc}",
            )

        kodierungen = []
        for k in data.get("kodierungen", []):
            hk = k.get("hk", "").upper()
            if hk in _HK_LABELS:
                kodierungen.append(Kodierung(
                    hk=hk,
                    bezeichnung=k.get("bezeichnung", _HK_LABELS.get(hk, "")),
                    begründung=k.get("begründung", ""),
                ))

        return KodierErgebnis(
            sinneinheit=unit,
            kodierungen=kodierungen,
            memo=data.get("memo", ""),
        )


# ── LaTeX-Writer ──────────────────────────────────────────────────────────────

class LaTeXWriter:
    """Schreibt kodierte Transkriptstellen als LaTeX-Codebuch-Fragment."""

    _SPECIAL = str.maketrans({
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    })

    def escape(self, text: str) -> str:
        return text.translate(self._SPECIAL)

    def write(
        self,
        results: List[KodierErgebnis],
        output_path: Path,
        interview_id: str,
        model: str,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        by_hk: dict[str, List[KodierErgebnis]] = {k: [] for k in _HK_LABELS}
        uncoded: List[KodierErgebnis] = []
        errors: List[KodierErgebnis] = []
        multi: List[KodierErgebnis] = []

        for r in results:
            if r.fehler:
                errors.append(r)
                continue
            if not r.kodierungen:
                uncoded.append(r)
                continue
            for k in r.kodierungen:
                by_hk[k.hk].append(r)
            if len(r.kodierungen) > 1:
                multi.append(r)

        total_kodierungen = sum(len(r.kodierungen) for r in results if not r.fehler)
        counts = {hk: len(items) for hk, items in by_hk.items()}

        lines: List[str] = []
        a = lines.append

        date_str = datetime.now().strftime("%d.%m.%Y")
        a(f"% ============================================================")
        a(f"% Erster Codierdurchgang (Phase 3 nach Kuckartz, 2018)")
        a(f"% Interview: {interview_id} | Erstellt: {date_str} | Modell: {model}")
        a(f"% Sinneinheiten: {len(results)} | Kodierungen: {total_kodierungen}")
        a(f"% HK0:{counts['HK0']} HK1:{counts['HK1']} HK2:{counts['HK2']} HK3:{counts['HK3']}")
        a(f"% HINWEIS: Diese Datei ist nicht git-versioniert (Datenschutz).")
        a(f"% Alle Kodierungen sind KI-generierte Arbeitshypothesen")
        a(f"% und muessen vor Verwendung manuell geprueft werden.")
        a(f"% ============================================================")
        a("")
        a(f"\\section*{{Interview \\texttt{{{self.escape(interview_id)}}} -- Erster Codierdurchgang}}")
        a("")
        a(f"\\noindent\\textit{{Erstellt am {date_str} | Sinneinheiten: {len(results)} |")
        a(f"Kodierungen: {total_kodierungen} (HK0: {counts['HK0']}, HK1: {counts['HK1']},")
        a(f"HK2: {counts['HK2']}, HK3: {counts['HK3']})}}\\\\[0.5em]")
        a("")
        a("\\noindent\\textbf{Hinweis:} Diese Kodierungen wurden KI-gest\\\"utzt erstellt und")
        a("sind als Arbeitshypothesen f\\\"ur den ersten Codierdurchgang zu verstehen.")
        a("Alle Zuweisungen m\\\"ussen manuell gepr\\\"uft und ggf. korrigiert werden")
        a("\\parencite{kuckartzQualitativeInhaltsanalyseMethoden2018}.")
        a("")

        for hk, label in _HK_LABELS.items():
            a(f"% ── {hk}: {label} ──────────────────────────────────────────────")
            a(f"\\subsection*{{{hk} -- {self.escape(label)}}}")
            a("")

            hk_results = by_hk[hk]
            if not hk_results:
                a("\\noindent\\textit{Keine Textstellen im ersten Codierdurchgang zugeordnet.}")
                a("")
                continue

            seen: set[int] = set()
            for r in hk_results:
                if r.sinneinheit.index in seen:
                    continue
                seen.add(r.sinneinheit.index)
                ts = self.escape(r.sinneinheit.timestamp or "---")
                text = self.escape(r.sinneinheit.text)
                this_hk_codes = [k for k in r.kodierungen if k.hk == hk]
                begründung = self.escape(this_hk_codes[0].begründung) if this_hk_codes else ""
                other_codes = [k.hk for k in r.kodierungen if k.hk != hk]
                a(f"\\begin{{description}}")
                a(f"  \\item[\\texttt{{\\#}}\\textbf{{{ts}}}\\texttt{{\\#}} "
                  f"(Sinneinheit {r.sinneinheit.index})]")
                a(f"  \\begin{{quote}}")
                a(f"  {text}")
                a(f"  \\end{{quote}}")
                a(f"  \\textbf{{Kategorie:}} {hk} -- {self.escape(label)}\\\\")
                if other_codes:
                    a(f"  \\textbf{{Weitere Kategorien:}} {', '.join(self.escape(c) for c in other_codes)}\\\\")
                if begründung:
                    a(f"  \\textbf{{Begr\\\"undung:}} {begründung}")
                if r.memo:
                    a(f"  \\\\\\textit{{Memo: {self.escape(r.memo)}}}")
                a(f"\\end{{description}}")
                a(f"\\medskip")
                a("")

        if errors:
            a("% ── Kodierungsfehler ────────────────────────────────────────────")
            a("\\subsection*{Kodierungsfehler}")
            a("")
            a("\\noindent Die folgenden Sinneinheiten konnten nicht verarbeitet werden:")
            a("\\begin{itemize}")
            for r in errors:
                ts = self.escape(r.sinneinheit.timestamp or "---")
                a(f"  \\item Sinneinheit {r.sinneinheit.index} (\\texttt{{\\#{ts}\\#}}): "
                  f"\\textit{{{self.escape(str(r.fehler)[:150])}}}")
            a("\\end{itemize}")
            a("")

        if uncoded:
            a("% ── Unkodierte Passagen ─────────────────────────────────────────")
            a("\\subsection*{Unkodierte Passagen}")
            a("")
            a("{\\small\\color{gray}")
            a("\\noindent Die folgenden Sinneinheiten wurden im ersten Codierdurchgang")
            a("keiner Hauptkategorie zugeordnet (kein motivationaler Bezug zum")
            a("Untersuchungsgegenstand):")
            a("\\begin{itemize}")
            for r in uncoded:
                ts = self.escape(r.sinneinheit.timestamp or "---")
                memo = f" -- {self.escape(r.memo)}" if r.memo else ""
                preview = self.escape(r.sinneinheit.text[:80])
                a(f"  \\item \\texttt{{\\#{ts}\\#}} (SE {r.sinneinheit.index}): "
                  f"\\textit{{{preview}\\ldots}}{memo}")
            a("\\end{itemize}")
            a("}")
            a("")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


# ── Hauptprogramm ─────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Erster Codierdurchgang nach Kuckartz (2018) via Claude API."
    )
    parser.add_argument(
        "rtf_file",
        help="Pfad zur RTF-Transkriptdatei (aus interviews/transcripts/)",
    )
    parser.add_argument(
        "--interview-id",
        default="B",
        help="Kürzel der befragten Person (z.B. IP-01). Standard: B",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Ausgabeverzeichnis für LaTeX-Datei. Standard: interviews/coded/",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Anthropic-Modell. Standard: ANTHROPIC_MODEL-Env oder claude-sonnet-4-6",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prompt anzeigen, aber keinen API-Aufruf durchführen.",
    )
    args = parser.parse_args()

    rtf_path = Path(args.rtf_file)
    if not rtf_path.exists():
        print(f"\nFehler: RTF-Datei nicht gefunden: {rtf_path}")
        sys.exit(1)

    repo_root = Path(__file__).parent.parent.parent
    output_dir = Path(args.output_dir) if args.output_dir else repo_root / "interviews" / "coded"
    safe_id = args.interview_id.replace("/", "-").replace("\\", "-")
    output_path = output_dir / f"{safe_id}_kodierung.tex"

    print(f"\n{'='*60}")
    print(f"  Code-Transcript-Service — Kuckartz (2018), Phase 3")
    print(f"{'='*60}")
    print(f"  RTF-Datei   : {rtf_path}")
    print(f"  Interview-ID: {args.interview_id}")
    print(f"  Ausgabe     : {output_path}")
    if args.dry_run:
        print(f"  Modus       : DRY-RUN (kein API-Aufruf)")
    print(f"{'='*60}\n")

    _load_env()

    if not args.dry_run:
        anthropic_key = _require_env(
            "ANTHROPIC_API_KEY",
            "  Hinweis: Anthropic API-Key erstellen unter: console.anthropic.com → API Keys"
        )
    else:
        anthropic_key = "dry-run"

    model = args.model or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    print("[1/3] RTF einlesen und Sinneinheiten extrahieren...")
    rtf_parser = RTFParser()
    try:
        units = rtf_parser.parse(rtf_path)
    except Exception as exc:
        print(f"  FEHLER beim RTF-Parsing: {exc}")
        sys.exit(1)

    if not units:
        print("  WARNUNG: Keine B:-Sinneinheiten gefunden.")
        print("  Mögliche Ursachen:")
        print("  - Transkript enthält keine 'B:' Sprechermarkierungen")
        print("  - RTF-Datei ist leer oder nicht im erwarteten Format")
        print("  - Überprüfe, ob die Datei aus dem /transcribe-Skill stammt")
        sys.exit(1)

    print(f"  → {len(units)} Sinneinheit(en) extrahiert.\n")

    if args.dry_run:
        print("[2/3] DRY-RUN: Zeige Prompt für erste Sinneinheit...")
    else:
        print(f"[2/3] Codierung ({len(units)} Sinneinheiten, Modell: {model})...")

    coder = KuckartzCoder(api_key=anthropic_key, model=model)
    results: List[KodierErgebnis] = []
    total = len(units)

    for unit in units:
        label = unit.text[:50].replace("\n", " ")
        print(f"  Sinneinheit {unit.index:3d}/{total}  #{unit.timestamp}#  {label}…")

        result = coder.code(unit, args.interview_id, dry_run=args.dry_run)
        results.append(result)

        if result.fehler:
            print(f"    → FEHLER: {result.fehler[:80]}")
        elif result.kodierungen:
            codes = ", ".join(k.hk for k in result.kodierungen)
            print(f"    → {codes} ({len(result.kodierungen)} Kodierung(en))")
        else:
            print(f"    → keine Kodierung")

        if args.dry_run:
            print("\n  (DRY-RUN beendet nach erster Sinneinheit)")
            break

    print()
    print("[3/3] LaTeX-Datei schreiben...")
    writer = LaTeXWriter()
    writer.write(results, output_path, args.interview_id, model)

    total_k = sum(len(r.kodierungen) for r in results if not r.fehler)
    counts = {"HK0": 0, "HK1": 0, "HK2": 0, "HK3": 0}
    for r in results:
        for k in r.kodierungen:
            if k.hk in counts:
                counts[k.hk] += 1
    fehler = sum(1 for r in results if r.fehler)

    print(f"\n{'='*60}")
    print(f"  Codierung abgeschlossen!")
    print(f"  Ausgabe: {output_path}")
    print(f"  Statistik: {len(results)} Sinneinheiten | {total_k} Kodierungen")
    print(f"  (HK0: {counts['HK0']} | HK1: {counts['HK1']} | "
          f"HK2: {counts['HK2']} | HK3: {counts['HK3']})")
    if fehler:
        print(f"  WARNUNG: {fehler} Sinneinheit(en) mit Fehlern (siehe LaTeX-Datei)")
    print(f"{'='*60}")
    print(f"\n  Nächste Schritte:")
    print(f"  1. LaTeX-Datei manuell prüfen und alle Kodierungen validieren")
    print(f"     (konsensuelle Kodierung nach Kuckartz, 2018)")
    print(f"  2. \\input{{interviews/coded/{safe_id}_kodierung}}")
    print(f"     in C_Inhalt/Anhang/A2_Kategoriensystem.tex einfügen")
    print(f"  3. Nach Abschluss aller Interviews: induktive Subkategorien")
    print(f"     bilden (Phase 5 nach Kuckartz, 2018)")
    print()

    # KI-Nutzung protokollieren (nur bei echtem API-Aufruf, nicht im Dry-Run)
    if not args.dry_run:
        import subprocess
        ki_log = repo_root / "services" / "ki_log" / "ki_log.py"
        if ki_log.exists():
            subprocess.run(
                [
                    sys.executable, str(ki_log), "add",
                    "--kapitel",  "Kapitel 3, Methodik / Datenauswertung / Erstkodierung",
                    "--tool",     f"Anthropic Claude ({model})",
                    "--zweck",    f"Erster Codierdurchgang (Phase 3) nach Kuckartz (2018); {len(results)} Sinneinheiten, Interview-ID: {args.interview_id}",
                    "--pruefung", "Manuelle Validierung aller KI-generierten Kodierungen (konsensuelle Kodierung nach Kuckartz, 2018)",
                    "--einfluss", f"KI-Arbeitshypothesen für Erstkodierung; endgültige Kodierungen manuell bestätigt und ggf. korrigiert",
                ],
                check=False,
            )


if __name__ == "__main__":
    main()
