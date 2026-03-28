# check-prd skill 安装脚本（Windows PowerShell）

$target = "$env:USERPROFILE\.claude\skills"

Write-Host "正在安装 check-prd skill..."
Write-Host "目标目录：$target"

# 创建目标目录（如果不存在）
New-Item -ItemType Directory -Force -Path $target | Out-Null

# 复制所有 skill 文件
$files = Get-Item "check-prd*.md"
foreach ($file in $files) {
    Copy-Item $file.FullName $target
}

$count = $files.Count
Write-Host ""
Write-Host "√ 安装完成！共安装 $count 个文件到 $target"
Write-Host ""
Write-Host "使用方法："
Write-Host "  1. 打开 Claude Code"
Write-Host "  2. 切换到 Opus 模型：/model claude-opus-4-6"
Write-Host "  3. 执行检查：/check-prd 你的PRD文件路径.pdf"
