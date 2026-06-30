<#
.SYNOPSIS
    AI教学文本 -> 精美HTML PPT -> 教学视频 全自动流水线 v8
#>
param(
    [Parameter(Mandatory=$true)][string]$InputFile,
    [int]$DurationPerSlide = 12,
    [string]$Theme = "slate",
    [string]$OutputDir = "D:\codex\teach-output",
    [switch]$NoTTS,
    [string]$Voice = "zh-CN-XiaoxiaoNeural"
)
$ErrorActionPreference = "Stop"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Test-Path $InputFile)) { Write-Error "Input file not found: $InputFile"; exit 1 }
$InputFile = (Resolve-Path $InputFile).Path

if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }

function Find-Python {
    if ($env:CODEX_PYTHON) { return $env:CODEX_PYTHON }
    $p = "F:\ComfyUI-aki-v1.4\ComfyUI-aki-v1.4\python\python.exe"
    if (Test-Path $p) { return $p }
    return "python"
}
$PYTHON = Find-Python

Write-Host "=== AI Teaching Text -> PPT -> Video v8 ===" -ForegroundColor Cyan
Write-Host "Input:  $(Split-Path $InputFile -Leaf)" -ForegroundColor Gray
Write-Host "Theme:  $Theme"
Write-Host "TTS:    $(if($NoTTS.IsPresent){'disabled'}else{'enabled'})"

Write-Host "`n[Step 1/4] Generating HTML PPT..." -ForegroundColor Yellow
$env:PYTHONIOENCODING = "utf-8"
& $PYTHON "$SCRIPT_DIR\generate_ppt.py" $InputFile --theme $Theme -o $OutputDir
if ($LASTEXITCODE -ne 0) { Write-Error "PPT generation failed!"; exit 1 }

$baseName = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
$slug = $baseName -replace '[^\w\u4e00-\u9fff]+', '-' -replace '^-+|-+$', ''
if (-not $slug) { $slug = "teaching-deck" }
if ($slug.Length -gt 40) { $slug = $slug.Substring(0,40).TrimEnd('-') }
$deckDir = Join-Path $OutputDir $slug

if (-not (Test-Path $deckDir)) {
    $deckDir = Get-ChildItem -Path $OutputDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $deckDir) { Write-Error "Cannot find generated deck!"; exit 1 }
}

Write-Host "Deck: $deckDir" -ForegroundColor Green

Write-Host "`n[Step 2/4] Screenshots..." -ForegroundColor Yellow
& $PYTHON "$SCRIPT_DIR\screenshot_slides.py" "$deckDir"
if ($LASTEXITCODE -ne 0) { Write-Error "Screenshots failed!"; exit 1 }

Write-Host "`n[Step 3/4] Rendering video..." -ForegroundColor Yellow
if ($NoTTS.IsPresent) {
    & "$SCRIPT_DIR\render_video.ps1" -DeckDir "$deckDir" -DurationPerSlide $DurationPerSlide
} else {
    & "$SCRIPT_DIR\render_video.ps1" -DeckDir "$deckDir" -DurationPerSlide $DurationPerSlide -WithTTS -Voice $Voice
}
if ($LASTEXITCODE -ne 0) { Write-Error "Video rendering failed!"; exit 1 }

Write-Host "`n=== All Done! ===" -ForegroundColor Green
Write-Host "Video: $(Join-Path $deckDir 'teaching-video.mp4')"
Write-Host "HTML:  $(Join-Path $deckDir 'index.html')"
