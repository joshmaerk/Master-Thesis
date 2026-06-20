#!/usr/bin/env python3
"""
KI-Nutzungs-Log: Einträge verwalten und LaTeX-Tabelle rendern.

Verwendung (vom Repo-Root):
    python3 services/ki_log/ki_log.py add \\
        --kapitel "Kapitel 3, Methodik" \\
        --tool "Claude Code (claude-sonnet-4-6)" \\
        --zweck "Erstellung Methodikabschnitt" \\
        --pruefung "Manuell überprüft und angepasst" \\
        --einfluss "Strukturentwurf übernommen, Formulierungen überarbeitet"

    python3 services/ki_log/ki_log.py render
"""

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
CSV_PATH = REPO_ROOT / "utils" / "ki_nutzung.csv"
TEX_PATH = REPO_ROOT / "KI Einsatz.tex"

FIELDNAMES = ["Kapitel", "Datum", "KI_Tool_Version", "Verwendungszweck", "Pruefungsprozess", "Einfluss"]

_TEX_HEADER = r"""\documentclass[a4paper]{report}

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[ngerman]{babel}

\usepackage{booktabs}
\usepackage{array}
\usepackage{geometry}
\usepackage{ragged2e}

\geometry{margin=1.5cm, landscape}

\begin{document}

\chapter{Dokumentation der KI-Nutzung}

\begin{table}[ht]
\centering
\footnotesize
\renewcommand{\arraystretch}{1.4}
\begin{tabular}{
  >{\RaggedRight\bfseries}p{3cm}
  >{\RaggedRight}p{1.6cm}
  >{\RaggedRight}p{2.8cm}
  >{\RaggedRight}p{4.5cm}
  >{\RaggedRight}p{4.5cm}
  >{\RaggedRight}p{4cm}
}
\toprule
\textbf{Kapitel} & \textbf{Datum} & \textbf{KI Tool \& Version} & \textbf{KI Verwendungszweck} & \textbf{Überprüfungsprozess} & \textbf{Einfluss auf Ergebnis} \\
\midrule
"""

_TEX_FOOTER = r"""
\bottomrule
\end{tabular}
\caption{KI-Nutzungsprotokoll nach Kapitel}
\label{tab:ki-protokoll}
\end{table}

\end{document}
"""

_LATEX_ESCAPE = str.maketrans({
    "&":  r"\&",
    "%":  r"\%",
    "$":  r"\$",
    "#":  r"\#",
    "_":  r"\_",
    "{":  r"\{",
    "}":  r"\}",
    "~":  r"\textasciitilde{}",
    "^":  r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
})


def _escape(text: str) -> str:
    return text.translate(_LATEX_ESCAPE)


def _build_row(row: dict) -> str:
    return (
        f"  {_escape(row['Kapitel'])}\n"
        f"    & {_escape(row['Datum'])}\n"
        f"    & {_escape(row['KI_Tool_Version'])}\n"
        f"    & {_escape(row['Verwendungszweck'])}\n"
        f"    & {_escape(row['Pruefungsprozess'])}\n"
        f"    & {_escape(row['Einfluss'])} \\\\"
    )


def cmd_add(args: argparse.Namespace) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_header = not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0

    row = {
        "Kapitel":         args.kapitel,
        "Datum":           args.datum or date.today().isoformat(),
        "KI_Tool_Version": args.tool,
        "Verwendungszweck": args.zweck,
        "Pruefungsprozess": args.pruefung,
        "Einfluss":        args.einfluss,
    }

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    print(f"KI-Log: Eintrag hinzugefügt — {row['Kapitel']} | {row['Datum']} | {row['KI_Tool_Version']}")


def cmd_render() -> None:
    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
        print(f"KI-Log: Keine Einträge in {CSV_PATH} — KI Einsatz.tex wird nicht verändert.")
        return

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if any(r.values())]

    if not rows:
        print("KI-Log: CSV ist leer — KI Einsatz.tex wird nicht verändert.")
        return

    table_body = "\n\\midrule\n".join(_build_row(r) for r in rows)
    TEX_PATH.write_text(_TEX_HEADER + table_body + _TEX_FOOTER, encoding="utf-8")
    print(f"KI-Log: KI Einsatz.tex aktualisiert ({len(rows)} Eintrag/Einträge).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="KI-Nutzungs-Log verwalten und LaTeX-Tabelle rendern."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Neuen Eintrag hinzufügen.")
    add_p.add_argument("--kapitel",  required=True, help='z.B. "Kapitel 3, Methodik"')
    add_p.add_argument("--tool",     required=True, help='z.B. "Claude Code (claude-sonnet-4-6)"')
    add_p.add_argument("--zweck",    required=True, help="Beschreibung des Verwendungszwecks")
    add_p.add_argument("--pruefung", required=True, help="Beschreibung des Überprüfungsprozesses")
    add_p.add_argument("--einfluss", required=True, help="Einfluss auf das Ergebnis")
    add_p.add_argument("--datum",    default=None,  help="Datum (YYYY-MM-DD). Standard: heute.")

    sub.add_parser("render", help="CSV → KI Einsatz.tex rendern.")

    args = parser.parse_args()
    if args.command == "add":
        cmd_add(args)
    elif args.command == "render":
        cmd_render()


if __name__ == "__main__":
    main()
