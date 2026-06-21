#!/usr/bin/env python3
"""Validate shared agent documentation references and frontmatter."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATHS = [
    Path("CLAUDE.md"),
    Path("AGENTS.md"),
    Path("README.md"),
    *Path(".claudedocs").glob("*.md"),
    *Path(".claude/commands").glob("*.md"),
    *Path(".claude/rules").glob("*.md"),
    *Path(".claude/agents").glob("*.md"),
]
REFERENCE_RE = re.compile(r"`([^`]+)`")
REPO_PATH_PREFIXES = (
    ".claudedocs/",
    ".claude/",
    "scripts/",
    "services/",
    "B_Literatur/",
    "C_Inhalt/",
    "A_Template/",
    "D_Extended Abstract/",
    "main.tex",
    "variables.tex",
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
)


def error(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path}: {message}")


def has_frontmatter(text: str) -> bool:
    return text.startswith("---\n") and "\n---\n" in text[4:]


def frontmatter(text: str) -> str:
    if not has_frontmatter(text):
        return ""
    return text.split("\n---\n", 1)[0][4:]


def should_check_reference(ref: str) -> bool:
    if any(ch in ref for ch in "*{}"):
        return False
    if ref.endswith(".env") or ref == ".env":
        return False
    if ref.startswith(("http://", "https://", "mailto:")):
        return False
    if " " in ref and not ref.startswith("D_Extended Abstract/"):
        return False
    return ref.startswith(REPO_PATH_PREFIXES)


def main() -> int:
    errors: list[str] = []

    for rel in DOC_PATHS:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")

        if "/workspace/" in text:
            error(errors, rel, "contains an absolute workspace path")

        for ref in REFERENCE_RE.findall(text):
            if not should_check_reference(ref):
                continue
            target = ROOT / ref
            if not target.exists():
                error(errors, rel, f"references missing path `{ref}`")

    for rel in Path(".claude/rules").glob("*.md"):
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        fm = frontmatter(text)
        if not fm:
            error(errors, rel, "missing YAML frontmatter")
        elif "paths:" not in fm:
            error(errors, rel, "frontmatter missing `paths:`")

    for rel in Path(".claude/agents").glob("*.md"):
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        fm = frontmatter(text)
        if not fm:
            error(errors, rel, "missing YAML frontmatter")
            continue
        for key in ("name:", "description:"):
            if key not in fm:
                error(errors, rel, f"frontmatter missing `{key}`")

    if errors:
        print("Agent documentation check failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Agent documentation check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
