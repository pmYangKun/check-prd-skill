#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "SKILL.md"
BUILD_SCRIPT = ROOT / "scripts" / "build.py"
DIST_PROMPT = ROOT / "dist" / "check-prd-universal-prompt.md"
DIST_SKILL = ROOT / "dist" / "check-prd.skill"

LEGACY_PATTERNS = [
    "~/.claude/skills/check-prd-",
    "~/.claude/skills/prd-quality-framework/",
    "~/.agents/skills/check-prd/",
]
LINK_PATTERN = re.compile(r"\((references/[^)#]+)\)")


def iter_text_files() -> list[Path]:
    paths = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts or "dist" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix in {".md", ".py", ".sh", ".ps1", ".json"}:
            paths.append(path)
    return paths


def validate_links() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    missing = []
    for relative in LINK_PATTERN.findall(skill_text):
        candidate = ROOT / relative
        if not candidate.exists():
            missing.append(relative)
    if missing:
        raise SystemExit(f"Missing supporting files referenced from SKILL.md: {missing}")


def validate_legacy_paths() -> None:
    offenders = []
    for path in iter_text_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8")
        if any(pattern in text for pattern in LEGACY_PATTERNS):
            offenders.append(str(path.relative_to(ROOT)))
    if offenders:
        raise SystemExit(f"Found legacy hard-coded skill paths in: {offenders}")


def validate_build() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=ROOT, check=True)
    if not DIST_PROMPT.exists():
        raise SystemExit("Missing generated universal prompt in dist/")
    if not DIST_SKILL.exists():
        raise SystemExit("Missing generated .skill package in dist/")


def main() -> int:
    validate_links()
    validate_legacy_paths()
    validate_build()
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
