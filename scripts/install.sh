#!/bin/bash
# check-prd skill installer for Mac / Linux

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="$HOME/.claude/skills/check-prd"

echo "Installing check-prd skill..."
echo "Source: $ROOT"
echo "Target: $TARGET"

python3 "$SCRIPT_DIR/install_skill.py" --source "$ROOT" --target "$TARGET"

echo ""
echo "Done!"
echo "Usage:"
echo "  1. Open Claude Code"
echo "  2. Switch to Opus if you want deeper analysis: /model claude-opus-4-6"
echo "  3. Run: /check-prd your-prd-file.pdf"
