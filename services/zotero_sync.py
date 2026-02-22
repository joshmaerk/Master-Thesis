#!/usr/bin/env python3
"""
Zotero → BibTeX Sync
====================
Lädt alle Einträge aus einer Zotero-Bibliothek über die Zotero Web API v3
und schreibt sie in die Datei B_Literatur/literatur.bib.

Konfiguration: Umgebungsvariablen (oder .env-Datei)
  ZOTERO_API_KEY   – privater API-Schlüssel (Zotero → Einstellungen → Feeds/API)
  ZOTERO_USER_ID   – numerische User-ID  (Zotero → Einstellungen → Feeds/API)
  ZOTERO_LIBRARY_TYPE – "user" (Standard) oder "group"
  ZOTERO_GROUP_ID  – Gruppen-ID, nur bei ZOTERO_LIBRARY_TYPE=group

Verwendung:
  python3 services/zotero_sync.py [--dry-run] [--no-backup] [--output PATH]
"""

import argparse
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Fehler: 'requests' ist nicht installiert.")
    print("  pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "B_Literatur" / "literatur.bib"
ZOTERO_API_BASE = "https://api.zotero.org"
PAGE_SIZE = 100          # Zotero-Maximum pro Anfrage


def load_env_file(path: Path) -> None:
    """Liest KEY=VALUE-Paare aus einer .env-Datei und setzt Umgebungsvariablen."""
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key not in os.environ:          # env-Vars haben Vorrang
                os.environ[key] = value


def get_config() -> dict:
    """Liest Konfiguration aus Umgebungsvariablen."""
    load_env_file(Path(__file__).parent / ".env")
    load_env_file(REPO_ROOT / ".env")

    api_key = os.environ.get("ZOTERO_API_KEY", "").strip()
    user_id = os.environ.get("ZOTERO_USER_ID", "").strip()
    library_type = os.environ.get("ZOTERO_LIBRARY_TYPE", "user").strip().lower()
    group_id = os.environ.get("ZOTERO_GROUP_ID", "").strip()

    errors = []
    if not api_key:
        errors.append("ZOTERO_API_KEY ist nicht gesetzt.")
    if not user_id:
        errors.append("ZOTERO_USER_ID ist nicht gesetzt.")
    if library_type == "group" and not group_id:
        errors.append("ZOTERO_GROUP_ID ist erforderlich wenn ZOTERO_LIBRARY_TYPE=group.")
    if library_type not in ("user", "group"):
        errors.append("ZOTERO_LIBRARY_TYPE muss 'user' oder 'group' sein.")

    if errors:
        print("Konfigurationsfehler:")
        for e in errors:
            print(f"  • {e}")
        print("\nHinweis: Kopiere services/.env.example nach services/.env und fülle die Werte aus.")
        sys.exit(1)

    return {
        "api_key": api_key,
        "user_id": user_id,
        "library_type": library_type,
        "group_id": group_id,
    }


# ---------------------------------------------------------------------------
# Zotero API
# ---------------------------------------------------------------------------

def build_library_url(cfg: dict) -> str:
    if cfg["library_type"] == "group":
        return f"{ZOTERO_API_BASE}/groups/{cfg['group_id']}/items"
    return f"{ZOTERO_API_BASE}/users/{cfg['user_id']}/items"


def fetch_bibtex(cfg: dict) -> str:
    """
    Lädt alle Bibliotheks-Einträge als BibTeX-String.
    Paginiert automatisch bis alle Einträge geholt sind.
    """
    headers = {
        "Zot-API-Key": cfg["api_key"],
        "User-Agent": "MasterThesis-ZoteroSync/1.0",
    }
    url = build_library_url(cfg)

    all_chunks: list[str] = []
    start = 0
    total: int | None = None

    print("Verbinde mit Zotero API …")

    while True:
        params = {
            "format": "bibtex",
            "limit": PAGE_SIZE,
            "start": start,
            "sort": "creator",
            "direction": "asc",
        }

        for attempt in range(4):
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=30)
                resp.raise_for_status()
                break
            except requests.exceptions.RequestException as exc:
                if attempt == 3:
                    print(f"\nFehler nach 4 Versuchen: {exc}")
                    sys.exit(1)
                wait = 2 ** attempt
                print(f"  Wiederhole in {wait}s … ({exc})")
                time.sleep(wait)

        if total is None:
            total = int(resp.headers.get("Total-Results", 0))
            print(f"Gefunden: {total} Einträge in der Bibliothek")

        chunk = resp.text.strip()
        if chunk:
            all_chunks.append(chunk)

        fetched_so_far = min(start + PAGE_SIZE, total)
        print(f"  Geladen: {fetched_so_far}/{total}", end="\r")

        start += PAGE_SIZE
        if start >= total:
            break

        time.sleep(0.1)   # API-Rate-Limit schonen

    print()   # newline nach dem \r
    return "\n\n".join(all_chunks) + "\n"


# ---------------------------------------------------------------------------
# Datei-Operationen
# ---------------------------------------------------------------------------

def backup_bib(bib_path: Path) -> Path | None:
    """Erstellt ein Backup der bestehenden .bib-Datei. Gibt den Pfad zurück."""
    if not bib_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = bib_path.with_name(f"{bib_path.stem}_backup_{ts}.bib")
    shutil.copy2(bib_path, backup_path)
    print(f"Backup erstellt: {backup_path.relative_to(REPO_ROOT)}")
    return backup_path


def count_entries(bibtex: str) -> int:
    """Zählt die Anzahl der @-Einträge in einem BibTeX-String."""
    return bibtex.count("\n@") + (1 if bibtex.startswith("@") else 0)


# ---------------------------------------------------------------------------
# Hauptprogramm
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronisiert Zotero-Bibliothek → B_Literatur/literatur.bib"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur herunterladen, keine Datei schreiben.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Kein Backup der bestehenden .bib-Datei erstellen.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        metavar="PFAD",
        help=f"Ausgabedatei (Standard: {DEFAULT_OUTPUT.relative_to(REPO_ROOT)})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = get_config()

    bibtex = fetch_bibtex(cfg)
    entry_count = count_entries(bibtex)
    print(f"BibTeX-Einträge empfangen: {entry_count}")

    if args.dry_run:
        print("--dry-run aktiv: Keine Datei geschrieben.")
        return

    output: Path = args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    if not args.no_backup:
        backup_bib(output)

    output.write_text(bibtex, encoding="utf-8")
    print(f"Gespeichert: {output.relative_to(REPO_ROOT)}")
    print("Sync abgeschlossen.")


if __name__ == "__main__":
    main()
