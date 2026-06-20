"""
RTF-Writer für MAXQDA-kompatible Transkriptdateien.
Erzeugt einfaches RTF mit Unicode-Kodierung nach Regel 15 von Dresing & Pehl (2017).
"""

from datetime import datetime
from pathlib import Path


class RTFWriter:
    def write(
        self,
        transcript: str,
        output_path: Path,
        interview_name: str,
        date_str: str = "",
    ) -> None:
        """
        Schreibt das formatierte Transkript als RTF-Datei.
        output_path: Zieldatei (wird angelegt falls nötig).
        interview_name: Dateiname ohne Endung (z.B. 'Interview_IP01').
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not date_str:
            date_str = datetime.now().strftime("%d.%m.%Y")

        rtf_body = self._build_rtf(transcript, interview_name, date_str)

        # RTF-Dateien werden in Windows-1252 kodiert; Unicode-Escape für Nicht-ASCII
        with open(output_path, "w", encoding="ascii", errors="replace") as f:
            f.write(rtf_body)

    @staticmethod
    def _rtf_unicode(text: str) -> str:
        """
        Wandelt Unicode-Zeichen in RTF-Escape-Sequenzen um.
        \\uN? = Unicode-Codepoint N, ? als Fallback-Zeichen.
        """
        result = []
        for char in text:
            code = ord(char)
            if code < 128:
                # Standard-ASCII
                if char == "\\":
                    result.append("\\\\")
                elif char == "{":
                    result.append("\\{")
                elif char == "}":
                    result.append("\\}")
                elif char == "\n":
                    result.append("\\line\n")
                else:
                    result.append(char)
            elif 128 <= code <= 255:
                # Latin-1: direkt als RTF-Unicode
                result.append(f"\\u{code}?")
            else:
                result.append(f"\\u{code}?")
        return "".join(result)

    def _build_rtf(self, transcript: str, interview_name: str, date_str: str) -> str:
        lines = []

        # RTF-Header — MAXQDA-kompatibel
        lines.append(r"{\rtf1\ansi\ansicpg1252\uc1\deff0")
        lines.append(r"{\fonttbl{\f0\fswiss\fcharset0 Arial;}{\f1\froman\fcharset0 Times New Roman;}}")
        lines.append(r"{\colortbl;\red0\green0\blue0;}")
        lines.append(r"\f0\fs24\sl360\slmult1")
        lines.append("")

        # Titelblock
        name_rtf = self._rtf_unicode(interview_name)
        lines.append(f"\\b\\fs28 {name_rtf}\\b0\\fs24\\line")
        lines.append(f"Datum: {date_str}\\line")
        lines.append("\\line")

        # Transkripttext zeilenweise verarbeiten
        for line in transcript.split("\n"):
            stripped = line.strip()
            if not stripped:
                lines.append("\\line")
                continue

            # Zeitmarken #HH:MM:SS# bleiben als Plain Text (MAXQDA erkennt sie)
            rtf_line = self._rtf_unicode(stripped)
            lines.append(f"{rtf_line}\\line")

        lines.append("}")

        return "\n".join(lines)
