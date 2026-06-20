#!/usr/bin/env python3
"""
Zotero-Tagging fuer die Collection "92_Abstract".

Ziel:
- Qualitaetstags (Journal-Ratings, Peer-Review, Quellentyp)
- Thementags (z. B. SDT, Fuehrung, Entscheidung, GenAI)
- Methodentags (z. B. Experiment, Review, Interview, Survey)

Standardverhalten:
- Dry-Run (kein Schreiben in Zotero)
- Optionales Schreiben mit --apply
- Vorhandene Tags bleiben erhalten
- Von diesem Skript verwaltete Praefix-Tags werden standardmaessig ersetzt
  (qual:, thema:, methode:), damit wiederholte Laeufe konsistent bleiben.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest


REPO_ROOT = Path(__file__).resolve().parent.parent
ZOTERO_API_BASE = "https://api.zotero.org"
DEFAULT_COLLECTION_NAME = "92_Abstract"
DEFAULT_JOURNAL_DB = REPO_ROOT / "services" / "literature_review" / "journal_scores.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "utils" / "zotero_tagging_92_abstract_report.json"
PAGE_SIZE = 100

MANAGED_PREFIXES = ("qual:", "thema:", "methode:")


TOPIC_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(self[-\s]?determination|sdt)\b", re.I), "thema:sdt"),
    (re.compile(r"\bautonomy\b|\bautonomie\b|\bvolition\b", re.I), "thema:autonomie"),
    (re.compile(r"\bcompetence\b|\bkompetenz\b|\bself[-\s]?efficacy\b", re.I), "thema:kompetenz"),
    (
        re.compile(r"\brelatedness\b|\bsoziale(?:\s|-)?eingebundenheit\b|\bdehumani[sz]ation\b", re.I),
        "thema:soziale_eingebundenheit",
    ),
    (re.compile(r"\bmotivation\b|\bintrinsic\b|\bextrinsic\b|\bamotivation\b", re.I), "thema:motivation"),
    (re.compile(r"\bleadership\b|\bfuehrung\b|\bmanager\b", re.I), "thema:fuehrung"),
    (re.compile(r"\bmiddle manager\b|\bmittler(?:e|es|er)\b", re.I), "thema:middle_management"),
    (re.compile(r"\bbank\b|\bbanking\b|\bfinance\b|\bfinancial\b|\bfintech\b", re.I), "thema:bankensektor"),
    (re.compile(r"\bdecision[-\s]?making\b|\bentscheidung\b|\bentscheidungs", re.I), "thema:entscheidung"),
    (re.compile(r"\bgenai\b|\bgenerative ai\b|\bllm\b|\blarge language model", re.I), "thema:genai"),
    (re.compile(r"\balgorithmic management\b|\balgorithmic\b", re.I), "thema:algorithmic_management"),
    (re.compile(r"\bdigital transformation\b|\bdigitalisierung\b", re.I), "thema:digitale_transformation"),
    (re.compile(r"\bhuman[-\s]?ai\b|\bmensch[-\s]?ki\b", re.I), "thema:mensch_ki_interaktion"),
    (re.compile(r"\borganizational behavior\b|\borganisational behavior\b|\bob\b", re.I), "thema:organizational_behavior"),
    (re.compile(r"\bwell[-\s]?being\b|\bwohlbefinden\b|\bburnout\b|\bstress\b", re.I), "thema:wohlbefinden"),
    (re.compile(r"\bjob demands[-\s]?resources\b|\bj[-\s]?d[-\s]?r\b", re.I), "thema:jdr"),
    (re.compile(r"\bmethod(?:ik|ology)\b|\bqualitative sozialforschung\b", re.I), "thema:methodik"),
]

METHOD_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bmeta[-\s]?analy", re.I), "methode:meta_analyse"),
    (re.compile(r"\bsystematic review\b|\bintegrative review\b|\bliterature review\b", re.I), "methode:review"),
    (re.compile(r"\bconceptual\b|\bopinion piece\b|\btheoretical\b|\bframework\b", re.I), "methode:konzeptionell"),
    (re.compile(r"\bmixed[-\s]?methods?\b", re.I), "methode:mixed_methods"),
    (re.compile(r"\bqualitative\b|\binterview\b|\bgioia\b|\bgrounded theory\b|\binhaltsanalyse\b", re.I), "methode:qualitativ"),
    (re.compile(r"\bcase study\b|\bfallstudie\b", re.I), "methode:fallstudie"),
    (re.compile(r"\bexperiment(?:al)?\b|\bfield experiment\b|\brandomi[sz]ed\b", re.I), "methode:experiment"),
    (re.compile(r"\bsurvey\b|\bquestionnaire\b|\bregression\b|\bpanel data\b|\btime[-\s]?lagged\b", re.I), "methode:quantitativ"),
]


@dataclass
class Config:
    api_key: str
    user_id: str
    library_type: str
    group_id: str
    collection_name: str
    collection_key: str
    include_subcollections: bool
    apply_changes: bool
    keep_managed_tags: bool
    report_path: Path
    journal_db_path: Path
    max_items: int
    print_taxonomy: bool


@dataclass
class HttpResponse:
    status_code: int
    headers: dict[str, str]
    text: str

    def json(self) -> Any:
        if not self.text:
            return None
        return json.loads(self.text)


def load_env_file(path: Path) -> None:
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
            if key and key not in os.environ:
                os.environ[key] = value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Taggt Zotero-Eintraege in einer Collection nach Qualitaet, Thema und Methode."
    )
    parser.add_argument("--api-key", default="", help="Zotero API Key (optional, sonst aus ENV).")
    parser.add_argument("--user-id", default="", help="Zotero User-ID (optional, sonst aus ENV).")
    parser.add_argument(
        "--library-type",
        default="",
        choices=["", "user", "group"],
        help="Bibliothekstyp (user/group).",
    )
    parser.add_argument("--group-id", default="", help="Group-ID (nur fuer library-type=group).")
    parser.add_argument(
        "--collection-name",
        default=DEFAULT_COLLECTION_NAME,
        help=f"Collection-Name (Standard: {DEFAULT_COLLECTION_NAME})",
    )
    parser.add_argument(
        "--collection-key",
        default="",
        help="Collection-Key statt Name verwenden (hat Vorrang).",
    )
    parser.add_argument(
        "--include-subcollections",
        action="store_true",
        help="Untercollections in den Lauf einschliessen.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Schreibt Tags in Zotero. Ohne dieses Flag nur Dry-Run.",
    )
    parser.add_argument(
        "--keep-managed-tags",
        action="store_true",
        help="Vorhandene qual:/thema:/methode:-Tags behalten (nicht ersetzen).",
    )
    parser.add_argument(
        "--journal-db",
        type=Path,
        default=DEFAULT_JOURNAL_DB,
        help=f"Pfad zu journal_scores.json (Standard: {DEFAULT_JOURNAL_DB.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Pfad fuer JSON-Report (Standard: {DEFAULT_REPORT_PATH.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=0,
        help="Optionales Limit an Items (0 = kein Limit).",
    )
    parser.add_argument(
        "--print-taxonomy",
        action="store_true",
        help="Gibt das Kategoriensystem aus und beendet das Skript ohne API-Zugriff.",
    )
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> Config:
    load_env_file(REPO_ROOT / ".env")
    load_env_file(REPO_ROOT / "services" / ".env")

    api_key = args.api_key or os.environ.get("ZOTERO_API_KEY", "").strip()
    user_id = args.user_id or os.environ.get("ZOTERO_USER_ID", "").strip()
    library_type = (args.library_type or os.environ.get("ZOTERO_LIBRARY_TYPE", "user")).strip().lower()
    group_id = args.group_id or os.environ.get("ZOTERO_GROUP_ID", "").strip()

    errors: list[str] = []
    if not args.print_taxonomy:
        if not api_key:
            errors.append("ZOTERO_API_KEY fehlt (ENV oder --api-key).")
        if not user_id and library_type == "user":
            errors.append("ZOTERO_USER_ID fehlt (ENV oder --user-id).")
        if library_type not in ("user", "group"):
            errors.append("library-type muss 'user' oder 'group' sein.")
        if library_type == "group" and not group_id:
            errors.append("group-id fehlt fuer library-type=group.")

    if errors:
        print("Konfigurationsfehler:")
        for err in errors:
            print(f"  - {err}")
        print("\nTipp: services/.env verwenden oder Flags setzen.")
        sys.exit(1)

    return Config(
        api_key=api_key,
        user_id=user_id,
        library_type=library_type,
        group_id=group_id,
        collection_name=args.collection_name.strip(),
        collection_key=args.collection_key.strip(),
        include_subcollections=args.include_subcollections,
        apply_changes=args.apply,
        keep_managed_tags=args.keep_managed_tags,
        report_path=args.report_path,
        journal_db_path=args.journal_db,
        max_items=max(0, args.max_items),
        print_taxonomy=args.print_taxonomy,
    )


def print_taxonomy() -> None:
    quality_tags = [
        "qual:type:{journal|book|report|thesis|conference|working_paper|web|other}",
        "qual:peer:{yes|no|unknown}",
        "qual:impact:{high|medium|low|unknown}",
        "qual:vhb:{a_plus|a|b|c|d|unrated}",
        "qual:abs:{4_star|4|3|2|1|unrated}",
        "qual:evidence:{empirical|review|mixed|practitioner|unknown}",
    ]
    topic_tags = sorted({tag for _, tag in TOPIC_RULES})
    method_tags = sorted({tag for _, tag in METHOD_RULES})

    print("KATEGORIENSYSTEM")
    print("\n1) Qualitaetstags")
    for tag in quality_tags:
        print(f"- {tag}")

    print("\n2) Thementags")
    for tag in topic_tags:
        print(f"- {tag}")

    print("\n3) Methodentags")
    for tag in method_tags:
        print(f"- {tag}")


def slugify_rating(value: str, fallback: str = "unknown") -> str:
    if not value:
        return fallback
    text = value.strip().lower()
    text = text.replace("+", "_plus")
    text = text.replace("*", "_star")
    text = text.replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or fallback


def normalize_journal_name(name: str) -> str:
    value = name.lower().replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def load_journal_db(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        print(f"Hinweis: Journal-DB nicht gefunden: {path}")
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_meta", None)

    normalized: dict[str, dict[str, Any]] = {}
    for journal_name, details in data.items():
        normalized[normalize_journal_name(journal_name)] = details
    return normalized


class ZoteroClient:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.base_headers = {
            "Zotero-API-Key": cfg.api_key,
            "Zotero-API-Version": "3",
            "User-Agent": "MasterThesis-ZoteroTagging/1.0",
        }

    def _library_prefix(self) -> str:
        if self.cfg.library_type == "group":
            return f"/groups/{self.cfg.group_id}"
        return f"/users/{self.cfg.user_id}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        expected: tuple[int, ...] = (200,),
    ) -> HttpResponse:
        url = f"{ZOTERO_API_BASE}{path}"
        last_error: Exception | None = None

        for attempt in range(4):
            try:
                resp = self._request_once(
                    method=method,
                    url=url,
                    params=params,
                    json_body=json_body,
                )
            except Exception as exc:
                last_error = exc
                time.sleep(2**attempt)
                continue

            if resp.status_code in expected:
                return resp

            if resp.status_code in (429, 500, 502, 503, 504):
                wait = int(resp.headers.get("Retry-After", 0)) or (2**attempt)
                time.sleep(wait)
                continue

            raise RuntimeError(f"{method} {url} -> HTTP {resp.status_code}: {resp.text[:400]}")

        if last_error:
            raise RuntimeError(f"{method} {url} fehlgeschlagen: {last_error}") from last_error
        raise RuntimeError(f"{method} {url} fehlgeschlagen (unerwarteter Zustand).")

    def _request_once(
        self,
        *,
        method: str,
        url: str,
        params: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
    ) -> HttpResponse:
        query = urlparse.urlencode(params or {}, doseq=True)
        full_url = f"{url}?{query}" if query else url
        payload = json.dumps(json_body).encode("utf-8") if json_body is not None else None

        headers = dict(self.base_headers)
        if payload is not None:
            headers["Content-Type"] = "application/json"

        req = urlrequest.Request(
            full_url,
            data=payload,
            headers=headers,
            method=method.upper(),
        )

        try:
            with urlrequest.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return HttpResponse(
                    status_code=int(resp.getcode()),
                    headers={k: v for k, v in resp.headers.items()},
                    text=body,
                )
        except urlerror.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return HttpResponse(
                status_code=int(exc.code),
                headers={k: v for k, v in (exc.headers.items() if exc.headers else [])},
                text=body,
            )
        except urlerror.URLError as exc:
            raise RuntimeError(f"Netzwerkfehler bei {full_url}: {exc}") from exc

    def get_all_collections(self) -> list[dict[str, Any]]:
        path = f"{self._library_prefix()}/collections"
        collections: list[dict[str, Any]] = []
        start = 0

        while True:
            resp = self._request(
                "GET",
                path,
                params={"format": "json", "limit": PAGE_SIZE, "start": start},
                expected=(200,),
            )
            batch = resp.json()
            collections.extend(batch)
            total = int(resp.headers.get("Total-Results", len(collections)))
            start += len(batch)
            if start >= total or not batch:
                break

        return collections

    def get_collection_items(self, collection_key: str) -> list[dict[str, Any]]:
        path = f"{self._library_prefix()}/collections/{collection_key}/items"
        items: list[dict[str, Any]] = []
        start = 0

        while True:
            resp = self._request(
                "GET",
                path,
                params={"format": "json", "limit": PAGE_SIZE, "start": start},
                expected=(200,),
            )
            batch = resp.json()
            items.extend(batch)
            total = int(resp.headers.get("Total-Results", len(items)))
            start += len(batch)
            if start >= total or not batch:
                break

        return items

    def get_item(self, item_key: str) -> dict[str, Any]:
        path = f"{self._library_prefix()}/items/{item_key}"
        resp = self._request("GET", path, params={"format": "json"}, expected=(200,))
        return resp.json()

    def patch_item_tags(self, item_key: str, version: int, tags: list[dict[str, Any]]) -> int:
        path = f"{self._library_prefix()}/items/{item_key}"
        resp = self._request(
            "PATCH",
            path,
            params={"v": 3},
            json_body={"version": version, "tags": tags},
            expected=(200, 204, 412),
        )
        return resp.status_code


def resolve_collection_keys(
    collections: list[dict[str, Any]],
    collection_name: str,
    collection_key: str,
    include_subcollections: bool,
) -> list[str]:
    by_key = {c["key"]: c for c in collections}

    if collection_key:
        if collection_key not in by_key:
            raise RuntimeError(f"Collection-Key '{collection_key}' wurde nicht gefunden.")
        root_key = collection_key
    else:
        matches = [
            c for c in collections if c.get("data", {}).get("name", "").strip().casefold() == collection_name.casefold()
        ]
        if not matches:
            raise RuntimeError(f"Collection '{collection_name}' wurde nicht gefunden.")
        if len(matches) > 1:
            keys = ", ".join(c["key"] for c in matches[:10])
            raise RuntimeError(
                f"Collection-Name '{collection_name}' ist nicht eindeutig ({len(matches)} Treffer). "
                f"Bitte --collection-key verwenden. Treffer: {keys}"
            )
        root_key = matches[0]["key"]

    if not include_subcollections:
        return [root_key]

    result: list[str] = []
    queue = [root_key]
    while queue:
        cur = queue.pop(0)
        result.append(cur)
        for c in collections:
            parent = c.get("data", {}).get("parentCollection", "")
            if parent == cur:
                queue.append(c["key"])
    return result


def get_text_blob(item_data: dict[str, Any]) -> str:
    fields = [
        "title",
        "shortTitle",
        "publicationTitle",
        "proceedingsTitle",
        "bookTitle",
        "abstractNote",
        "extra",
    ]
    values = [str(item_data.get(f, "")) for f in fields if item_data.get(f)]
    creator_names: list[str] = []
    for creator in item_data.get("creators", []):
        name = creator.get("name") or f"{creator.get('firstName', '')} {creator.get('lastName', '')}".strip()
        if name:
            creator_names.append(name)
    values.extend(creator_names)
    values.extend(tag.get("tag", "") for tag in item_data.get("tags", []))
    return " ".join(values).lower()


def source_type_from_item(item_type: str, publication_title: str) -> str:
    t = (item_type or "").strip()
    if t == "journalArticle":
        return "journal"
    if t in {"book", "bookSection"}:
        return "book"
    if t in {"report"}:
        return "report"
    if t in {"thesis"}:
        return "thesis"
    if t in {"conferencePaper"}:
        return "conference"
    if t in {"preprint", "manuscript"}:
        return "working_paper"
    pub = (publication_title or "").lower()
    if "ssrn" in pub or "arxiv" in pub:
        return "working_paper"
    if t in {"webpage", "blogPost", "forumPost"}:
        return "web"
    return "other"


def extract_publication_title(item_data: dict[str, Any]) -> str:
    for field in ("publicationTitle", "proceedingsTitle", "bookTitle", "seriesTitle"):
        value = str(item_data.get(field, "")).strip()
        if value:
            return value
    return ""


def infer_quality_tags(item_data: dict[str, Any], journal_db: dict[str, dict[str, Any]]) -> set[str]:
    tags: set[str] = set()
    item_type = str(item_data.get("itemType", "")).strip()
    publication_title = extract_publication_title(item_data)

    source_type = source_type_from_item(item_type, publication_title)
    tags.add(f"qual:type:{source_type}")

    if source_type != "journal":
        return tags

    journal_meta = journal_db.get(normalize_journal_name(publication_title), {})
    peer = journal_meta.get("peer_reviewed")
    impact = slugify_rating(str(journal_meta.get("impact_level", "")), "unknown")
    vhb = slugify_rating(str(journal_meta.get("vhb_rating", "")), "unrated")
    abs_rating = slugify_rating(str(journal_meta.get("abs_rating", "")), "unrated")
    evidence = slugify_rating(str(journal_meta.get("journal_type", "")), "unknown")

    if peer is True:
        tags.add("qual:peer:yes")
    elif peer is False:
        tags.add("qual:peer:no")
    else:
        tags.add("qual:peer:unknown")

    tags.add(f"qual:impact:{impact}")
    tags.add(f"qual:vhb:{vhb}")
    tags.add(f"qual:abs:{abs_rating}")
    tags.add(f"qual:evidence:{evidence}")
    return tags


def infer_topic_tags(item_data: dict[str, Any]) -> set[str]:
    blob = get_text_blob(item_data)
    tags: set[str] = set()
    for pattern, tag in TOPIC_RULES:
        if pattern.search(blob):
            tags.add(tag)
    return tags


def infer_method_tags(item_data: dict[str, Any]) -> set[str]:
    blob = get_text_blob(item_data)
    tags: set[str] = set()
    for pattern, tag in METHOD_RULES:
        if pattern.search(blob):
            tags.add(tag)
    return tags


def merge_tags(
    existing_tag_objs: list[dict[str, Any]],
    inferred_tags: set[str],
    keep_managed_tags: bool,
) -> tuple[list[dict[str, Any]], set[str], set[str], set[str]]:
    existing_map: dict[str, dict[str, Any]] = {}
    for obj in existing_tag_objs:
        tag_text = str(obj.get("tag", "")).strip()
        if tag_text:
            existing_map[tag_text] = obj

    existing_set = set(existing_map.keys())

    if keep_managed_tags:
        base_tags = set(existing_set)
    else:
        base_tags = {
            t for t in existing_set if not any(t.startswith(prefix) for prefix in MANAGED_PREFIXES)
        }

    target_set = base_tags | inferred_tags
    added = target_set - existing_set
    removed = existing_set - target_set

    merged_objs: list[dict[str, Any]] = []
    for tag in sorted(target_set):
        if tag in existing_map and "type" in existing_map[tag]:
            merged_objs.append({"tag": tag, "type": existing_map[tag]["type"]})
        else:
            merged_objs.append({"tag": tag})

    return merged_objs, added, removed, target_set


def is_regular_item(item_data: dict[str, Any]) -> bool:
    return item_data.get("itemType") not in {"attachment", "note", "annotation"}


def main() -> None:
    args = parse_args()
    cfg = build_config(args)
    if cfg.print_taxonomy:
        print_taxonomy()
        return

    journal_db = load_journal_db(cfg.journal_db_path)
    client = ZoteroClient(cfg)

    print("Lese Collections aus Zotero …")
    collections = client.get_all_collections()
    collection_keys = resolve_collection_keys(
        collections,
        cfg.collection_name,
        cfg.collection_key,
        cfg.include_subcollections,
    )
    print(f"Collections im Lauf: {', '.join(collection_keys)}")

    all_items: dict[str, dict[str, Any]] = {}
    for ckey in collection_keys:
        items = client.get_collection_items(ckey)
        for item in items:
            key = item.get("key")
            if key:
                all_items[key] = item

    items = list(all_items.values())
    items = [it for it in items if is_regular_item(it.get("data", {}))]
    if cfg.max_items:
        items = items[: cfg.max_items]

    print(f"Items in Scope: {len(items)}")
    if not items:
        print("Keine bearbeitbaren Items gefunden.")
        return

    changed = 0
    unchanged = 0
    failed = 0
    added_counter: Counter[str] = Counter()
    report_rows: list[dict[str, Any]] = []

    for idx, item in enumerate(items, start=1):
        item_key = item["key"]
        data = item.get("data", {})
        title = str(data.get("title", "")).strip() or f"(ohne Titel: {item_key})"
        version = int(item.get("version", data.get("version", 0)))
        existing_tags = list(data.get("tags", []))

        inferred = set()
        inferred |= infer_quality_tags(data, journal_db)
        inferred |= infer_topic_tags(data)
        inferred |= infer_method_tags(data)

        merged_objs, added, removed, target_set = merge_tags(
            existing_tags,
            inferred,
            keep_managed_tags=cfg.keep_managed_tags,
        )

        current_set = {str(t.get("tag", "")).strip() for t in existing_tags if str(t.get("tag", "")).strip()}
        if target_set == current_set:
            unchanged += 1
            status = "unchanged"
        else:
            changed += 1
            status = "planned"
            added_counter.update(added)

            if cfg.apply_changes:
                code = client.patch_item_tags(item_key, version, merged_objs)
                if code in (200, 204):
                    status = "updated"
                elif code == 412:
                    # Konflikt: Item erneut laden und einmal wiederholen
                    latest = client.get_item(item_key)
                    latest_data = latest.get("data", {})
                    latest_version = int(latest.get("version", latest_data.get("version", 0)))
                    latest_existing = list(latest_data.get("tags", []))
                    merged_retry, added_retry, removed_retry, target_retry = merge_tags(
                        latest_existing,
                        inferred,
                        keep_managed_tags=cfg.keep_managed_tags,
                    )
                    code_retry = client.patch_item_tags(item_key, latest_version, merged_retry)
                    if code_retry in (200, 204):
                        status = "updated_after_retry"
                        added = added_retry
                        removed = removed_retry
                    else:
                        status = f"failed_http_{code_retry}"
                        failed += 1
                else:
                    status = f"failed_http_{code}"
                    failed += 1

        report_rows.append(
            {
                "item_key": item_key,
                "title": title,
                "status": status,
                "added_tags": sorted(added),
                "removed_tags": sorted(removed),
            }
        )
        print(f"[{idx:03d}/{len(items)}] {status:18} {title[:110]}")

    cfg.report_path.parent.mkdir(parents=True, exist_ok=True)
    report_payload = {
        "collection_keys": collection_keys,
        "apply_changes": cfg.apply_changes,
        "items_total": len(items),
        "items_changed": changed,
        "items_unchanged": unchanged,
        "items_failed": failed,
        "top_added_tags": added_counter.most_common(30),
        "rows": report_rows,
    }
    cfg.report_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\nZusammenfassung")
    print(f"  Geaendert/geplant: {changed}")
    print(f"  Unveraendert:      {unchanged}")
    print(f"  Fehler:            {failed}")
    print(f"  Report:            {cfg.report_path}")
    if not cfg.apply_changes:
        print("  Modus:             Dry-Run (keine Zotero-Aenderung)")
    else:
        print("  Modus:             Apply (Tags in Zotero geschrieben)")


if __name__ == "__main__":
    main()
