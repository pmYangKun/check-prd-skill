# check-prd skill installer for Windows (PowerShell)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Split-Path -Parent $scriptDir
$target = Join-Path $env:USERPROFILE ".claude\skills\check-prd"
$python = Get-Command py -ErrorAction SilentlyContinue

if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Error "Python 3 is required to install this skill."
    exit 1
}

Write-Host "Installing check-prd skill..."
Write-Host "Source: $source"
Write-Host "Target: $target"

if ($python.Name -eq "py") {
    & py -3 (Join-Path $scriptDir "install_skill.py") --source $source --target $target
} else {
    & python (Join-Path $scriptDir "install_skill.py") --source $source --target $target
}

Write-Host ""
Write-Host "Done!"
Write-Host "Usage:"
Write-Host "  1. Open Claude Code"
Write-Host "  2. Switch to Opus if you want deeper analysis: /model claude-opus-4-6"
Write-Host "  3. Run: /check-prd your-prd-file.pdf"
