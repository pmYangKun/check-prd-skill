#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


IGNORE_PARTS = {
    ".git",
    "dist",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".DS_Store",
}


def ignore(_: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORE_PARTS}


def sync_skill(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=ignore)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the check-prd skill into a Claude skills directory.")
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--target", type=Path, default=Path.home() / ".claude" / "skills" / "check-prd")
    args = parser.parse_args()

    sync_skill(args.source.resolve(), args.target.resolve())
    print(f"Installed skill to: {args.target.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
