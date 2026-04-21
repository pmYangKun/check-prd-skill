# check-prd skill 安装脚本（Windows PowerShell）

$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = Join-Path $env:USERPROFILE ".claude\skills\check-prd"
$python = Get-Command py -ErrorAction SilentlyContinue

if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Error "需要安装 Python 3 才能安装此 skill。"
    exit 1
}

Write-Host "正在安装 check-prd skill..."
Write-Host "源目录：$source"
Write-Host "目标目录：$target"

if ($python.Name -eq "py") {
    & py -3 (Join-Path $source "scripts\install_skill.py") --source $source --target $target
} else {
    & python (Join-Path $source "scripts\install_skill.py") --source $source --target $target
}

Write-Host ""
Write-Host "安装完成！"
Write-Host "使用方式："
Write-Host "  1. 打开 Claude Code"
Write-Host "  2. 如需更深度的审查，可切换到 Opus：/model claude-opus-4-6"
Write-Host "  3. 运行：/check-prd <你的 PRD 文件路径>"
