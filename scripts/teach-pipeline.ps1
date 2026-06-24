param(
    [Parameter(Mandatory=$true)][string]$InputFile,
    [int]$DurationPerSlide = 12,
    [string]$Theme = "tokyo-night",
    [string]$OutputDir = "D:\codex\teach-output",
    [switch]$NoTTS,
    [string]$Voice = "zh-CN-XiaoxiaoNeural"
)
$ErrorActionPreference = "Stop"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Test-Path $InputFile)) { Write-Error "Input file not found: $InputFile"; exit 1 }
$InputFile = (Resolve-Path $InputFile).Path

if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }

if ($env:CODEX_PYTHON) { $PYTHON = $env:CODEX_PYTHON }
else { $PYTHON = "python" }
try { $null = & $PYTHON --version 2>$null } catch { $PYTHON = "python3" }

Write-Host "=== AI Teaching Text -> PPT -> Video v2 ===" -ForegroundColor Cyan
Write-Host "Input:  $(Split-Path $InputFile -Leaf)" -ForegroundColor Gray
Write-Host "Theme:  $Theme"
Write-Host "TTS:    $(if($NoTTS){'disabled'}else{'enabled'})"
Write-Host "Voice:  $Voice"

Write-Host "`n[Step 1/2] Generating HTML PPT..." -ForegroundColor Yellow
$env:PYTHONIOENCODING = "utf-8"
& $PYTHON "$SCRIPT_DIR\generate_ppt.py" $InputFile --theme $Theme -o $OutputDir
if ($LASTEXITCODE -ne 0) { Write-Error "PPT generation failed!"; exit 1 }

$deckDir = Get-ChildItem -Path $OutputDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $deckDir) { Write-Error "Cannot find generated deck!"; exit 1 }
Write-Host "Deck: $($deckDir.FullName)" -ForegroundColor Green

Write-Host "`n[Step 2/2] Rendering video..." -ForegroundColor Yellow
if ($NoTTS) {
    & "$SCRIPT_DIR\render_video.ps1" -DeckDir $deckDir.FullName -DurationPerSlide $DurationPerSlide
} else {
    & "$SCRIPT_DIR\render_video.ps1" -DeckDir $deckDir.FullName -DurationPerSlide $DurationPerSlide -WithTTS -Voice $Voice
}
if ($LASTEXITCODE -ne 0) { Write-Error "Video rendering failed!"; exit 1 }

Write-Host "`n=== All Done! ===" -ForegroundColor Green
Write-Host "Video: $(Join-Path $deckDir.FullName 'teaching-video.mp4')"
Write-Host "HTML:  $(Join-Path $deckDir.FullName 'index.html')"
Write-Host "`nTip: Open the HTML in a browser and press T to cycle themes" -ForegroundColor Gray
