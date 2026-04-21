#!/bin/bash
# check-prd skill 安装脚本（Mac / Linux）

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude/skills/check-prd"

echo "正在安装 check-prd skill..."
echo "源目录：$ROOT"
echo "目标目录：$TARGET"

python3 "$ROOT/scripts/install_skill.py" --source "$ROOT" --target "$TARGET"

echo ""
echo "安装完成！"
echo "使用方式："
echo "  1. 打开 Claude Code"
echo "  2. 如需更深度的审查，可切换到 Opus：/model claude-opus-4-6"
echo "  3. 运行：/check-prd <你的 PRD 文件路径>"
