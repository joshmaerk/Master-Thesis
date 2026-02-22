"""
GitHub Issue Manager für APA7-Konformitätsprobleme.

Kein AI/GenAI — verwendet ausschließlich die GitHub REST API v3.
Authentifizierung via GITHUB_TOKEN (automatisch in GitHub Actions verfügbar).
"""

from __future__ import annotations

import os
import time
from typing import Optional

import requests

from apa7_checker import EntryResult

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

LABEL_NAME = "apa7-compliance"
LABEL_COLOR = "e4e669"          # Gelb
LABEL_DESCRIPTION = "APA7-Konformitätsproblem in BibTeX-Eintrag"
ISSUE_TITLE_PREFIX = "[APA7]"

_GITHUB_API = "https://api.github.com"
_HEADERS_BASE = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _get_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN ist nicht gesetzt. "
            "In GitHub Actions wird es automatisch bereitgestellt. "
            "Lokal: export GITHUB_TOKEN=<dein_token>"
        )
    return token


def _get_repo() -> str:
    """Gibt 'owner/repo' zurück — aus Umgebungsvariable oder git remote."""
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if repo:
        return repo
    # Fallback: aus git remote origin ermitteln
    import subprocess
    try:
        out = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], text=True
        ).strip()
        # https://github.com/owner/repo.git  oder  git@github.com:owner/repo.git
        out = out.removesuffix(".git")
        if "github.com/" in out:
            return out.split("github.com/")[-1]
        if "github.com:" in out:
            return out.split("github.com:")[-1]
    except Exception:
        pass
    raise RuntimeError(
        "GITHUB_REPOSITORY nicht gesetzt und konnte nicht aus git remote ermittelt werden."
    )


def _headers(token: str) -> dict:
    return {**_HEADERS_BASE, "Authorization": f"Bearer {token}"}


def _api_get(url: str, token: str, params: dict | None = None) -> requests.Response:
    for attempt in range(4):
        resp = requests.get(url, headers=_headers(token), params=params, timeout=20)
        if resp.status_code == 429 or resp.status_code >= 500:
            wait = 2 ** attempt
            print(f"  API-Fehler {resp.status_code}, warte {wait}s …")
            time.sleep(wait)
            continue
        return resp
    resp.raise_for_status()
    return resp


def _api_post(url: str, token: str, payload: dict) -> requests.Response:
    for attempt in range(4):
        resp = requests.post(
            url, json=payload, headers=_headers(token), timeout=20
        )
        if resp.status_code == 429 or resp.status_code >= 500:
            wait = 2 ** attempt
            print(f"  API-Fehler {resp.status_code}, warte {wait}s …")
            time.sleep(wait)
            continue
        return resp
    resp.raise_for_status()
    return resp


# ---------------------------------------------------------------------------
# Label-Management
# ---------------------------------------------------------------------------

def ensure_label(token: str, repo: str) -> None:
    """Erstellt das APA7-Label falls es nicht existiert."""
    url = f"{_GITHUB_API}/repos/{repo}/labels/{LABEL_NAME}"
    resp = _api_get(url, token)
    if resp.status_code == 404:
        _api_post(
            f"{_GITHUB_API}/repos/{repo}/labels",
            token,
            {"name": LABEL_NAME, "color": LABEL_COLOR, "description": LABEL_DESCRIPTION},
        )
        print(f"Label '{LABEL_NAME}' erstellt.")


# ---------------------------------------------------------------------------
# Bestehende Issues laden
# ---------------------------------------------------------------------------

def _load_existing_issues(token: str, repo: str) -> set[str]:
    """Gibt alle Issue-Titel zurück (offen + geschlossen) mit APA7-Label."""
    titles: set[str] = set()
    page = 1
    while True:
        resp = _api_get(
            f"{_GITHUB_API}/repos/{repo}/issues",
            token,
            params={
                "labels": LABEL_NAME,
                "state": "all",
                "per_page": 100,
                "page": page,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        for issue in data:
            titles.add(issue["title"])
        if len(data) < 100:
            break
        page += 1
    return titles


# ---------------------------------------------------------------------------
# Issue-Inhalt generieren
# ---------------------------------------------------------------------------

def _format_entry_fields(entry: dict) -> str:
    """Formatiert einen BibTeX-Eintrag als Codeblock für das Issue."""
    key = entry.get("ID", "")
    etype = entry.get("ENTRYTYPE", "misc")
    fields = {k: v for k, v in entry.items() if k not in ("ID", "ENTRYTYPE")}
    lines = [f"@{etype}{{{key},"]
    for k, v in sorted(fields.items()):
        lines.append(f"  {k} = {{{v}}},")
    lines.append("}")
    return "\n".join(lines)


def _build_issue_body(result: EntryResult) -> str:
    errors = [i for i in result.issues if i.severity == "error"]
    warnings = [i for i in result.issues if i.severity == "warning"]

    lines = [
        f"## APA7-Konformitätsprüfung: `{result.key}`",
        "",
        f"**Entry-Typ:** `@{result.entry_type}`",
        "",
    ]

    if errors:
        lines += ["### Fehler (Error)", ""]
        for e in errors:
            lines.append(f"- ❌ {e.message}")
        lines.append("")

    if warnings:
        lines += ["### Warnungen (Warning)", ""]
        for w in warnings:
            lines.append(f"- ⚠️ {w.message}")
        lines.append("")

    lines += [
        "### Aktueller BibTeX-Eintrag",
        "",
        "```bibtex",
        _format_entry_fields(result.entry_raw),
        "```",
        "",
        "---",
        "*Erstellt automatisch durch den Literature-Review-Service.*  ",
        "*Zum Beheben: Eintrag in Zotero korrigieren und `zotero_sync.py` ausführen.*",
        "*Zum Ausschließen: BibTeX-Schlüssel in `.literatureignore` eintragen.*",
    ]
    return "\n".join(lines)


def _build_issue_title(result: EntryResult) -> str:
    error_count = sum(1 for i in result.issues if i.severity == "error")
    warn_count = sum(1 for i in result.issues if i.severity == "warning")
    parts = []
    if error_count:
        parts.append(f"{error_count} Fehler")
    if warn_count:
        parts.append(f"{warn_count} Warnung{'en' if warn_count > 1 else ''}")
    summary = ", ".join(parts)
    return f"{ISSUE_TITLE_PREFIX} `{result.key}` — {summary}"


# ---------------------------------------------------------------------------
# Haupt-API
# ---------------------------------------------------------------------------

def process_issues(
    results: list[EntryResult],
    dry_run: bool = False,
    verbose: bool = True,
) -> dict[str, str]:
    """
    Erstellt GitHub Issues für APA7-Probleme.

    Returns:
        Dict mapping BibTeX-Key → Issue-URL (oder "skipped"/"dry-run")
    """
    token = _get_token()
    repo = _get_repo()

    if verbose:
        print(f"Repository: {repo}")

    ensure_label(token, repo)
    existing_titles = _load_existing_issues(token, repo)

    if verbose:
        print(f"Bestehende APA7-Issues: {len(existing_titles)}")

    outcome: dict[str, str] = {}

    for result in results:
        title = _build_issue_title(result)

        if title in existing_titles:
            if verbose:
                print(f"  [SKIP] Issue existiert bereits: {result.key}")
            outcome[result.key] = "skipped"
            continue

        if dry_run:
            print(f"  [DRY-RUN] Würde Issue erstellen: {title}")
            outcome[result.key] = "dry-run"
            continue

        body = _build_issue_body(result)
        payload = {
            "title": title,
            "body": body,
            "labels": [LABEL_NAME],
        }

        resp = _api_post(f"{_GITHUB_API}/repos/{repo}/issues", token, payload)
        if resp.status_code in (200, 201):
            url = resp.json().get("html_url", "")
            if verbose:
                print(f"  [CREATE] {result.key}: {url}")
            outcome[result.key] = url
        else:
            print(f"  [ERROR] {result.key}: HTTP {resp.status_code} — {resp.text[:200]}")
            outcome[result.key] = f"error:{resp.status_code}"

        time.sleep(0.5)   # Rate-Limit schonen

    return outcome
