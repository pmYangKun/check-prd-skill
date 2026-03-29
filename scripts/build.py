#!/usr/bin/env python3
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
UNIVERSAL_PROMPT = DIST_DIR / "check-prd-universal-prompt.md"
SKILL_PACKAGE = DIST_DIR / "check-prd.skill"

SECTION_ORDER = [
    ROOT / "references" / "universal-prompt-intro.md",
    ROOT / "references" / "dimensions" / "check-prd-01-business.md",
    ROOT / "references" / "dimensions" / "check-prd-02-product-type.md",
    ROOT / "references" / "dimensions" / "check-prd-03-positioning.md",
    ROOT / "references" / "dimensions" / "check-prd-04-scenario.md",
    ROOT / "references" / "dimensions" / "check-prd-05-structure.md",
    ROOT / "references" / "dimensions" / "check-prd-06-architecture.md",
    ROOT / "references" / "dimensions" / "check-prd-07-data.md",
    ROOT / "references" / "dimensions" / "check-prd-08-process.md",
    ROOT / "references" / "dimensions" / "check-prd-09-ux.md",
    ROOT / "references" / "dimensions" / "check-prd-10-commercial.md",
    ROOT / "references" / "dimensions" / "check-prd-11-mvp.md",
    ROOT / "references" / "dimensions" / "check-prd-14-operations.md",
    ROOT / "references" / "dimensions" / "check-prd-12-exception.md",
    ROOT / "references" / "dimensions" / "check-prd-13-ai.md",
    ROOT / "references" / "appendices" / "check-prd-appendix-veto.md",
    ROOT / "references" / "appendices" / "check-prd-appendix-guide.md",
]

IGNORE_PARTS = {
    ".git",
    "dist",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".DS_Store",
}


def clean_section(text: str) -> str:
    lines = text.strip().splitlines()
    if len(lines) > 1 and lines[1].startswith("> Supporting reference"):
        lines.pop(1)
        if len(lines) > 1 and not lines[1].strip():
            lines.pop(1)
    return "\n".join(lines).strip() + "\n"


def build_universal_prompt(output_path: Path = UNIVERSAL_PROMPT) -> Path:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    parts = []
    for section in SECTION_ORDER:
        parts.append(clean_section(section.read_text(encoding="utf-8")))
    output_path.write_text("\n\n---\n\n".join(parts) + "\n", encoding="utf-8")
    return output_path


def should_package(path: Path) -> bool:
    if any(part in IGNORE_PARTS for part in path.parts):
        return False
    return path.is_file()


def build_skill_package(output_path: Path = SKILL_PACKAGE) -> Path:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob("*")):
            if not should_package(path):
                continue
            archive.write(path, arcname=path.relative_to(ROOT))
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build generated artifacts for the check-prd skill.")
    parser.add_argument("--skip-package", action="store_true", help="Build the universal prompt only.")
    args = parser.parse_args()

    prompt_path = build_universal_prompt()
    print(f"Built universal prompt: {prompt_path}")

    if not args.skip_package:
        package_path = build_skill_package()
        print(f"Built skill package: {package_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
