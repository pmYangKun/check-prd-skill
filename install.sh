#!/bin/bash
# check-prd skill 安装脚本（Mac / Linux）

set -e

TARGET="$HOME/.claude/skills"

echo "正在安装 check-prd skill..."
echo "目标目录：$TARGET"

# 创建目标目录（如果不存在）
mkdir -p "$TARGET"

# 复制所有 skill 文件
cp check-prd.md "$TARGET/"
cp check-prd-0*.md "$TARGET/"
cp check-prd-1*.md "$TARGET/"
cp check-prd-appendix-*.md "$TARGET/"

echo ""
echo "✓ 安装完成！共安装 $(ls check-prd*.md | wc -l | tr -d ' ') 个文件到 $TARGET"
echo ""
echo "使用方法："
echo "  1. 打开 Claude Code"
echo "  2. 切换到 Opus 模型：/model claude-opus-4-6"
echo "  3. 执行检查：/check-prd 你的PRD文件路径.pdf"
