<#
.SYNOPSIS
    Render HTML PPT to MP4 video - v3
#>
param(
    [Parameter(Mandatory=$true)][string]$DeckDir,
    [int]$DurationPerSlide = 12,
    [switch]$WithTTS,
    [string]$Voice = "zh-CN-XiaoxiaoNeural"
)
$ErrorActionPreference = "Continue"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

function Find-Python {
    if ($env:CODEX_PYTHON) { return $env:CODEX_PYTHON }
    $which = Get-Command python -ErrorAction SilentlyContinue
    if ($which) { return "python" }
    $which = Get-Command python3 -ErrorAction SilentlyContinue
    if ($which) { return "python3" }
    $paths = @("F:\ComfyUI-aki-v1.4\ComfyUI-aki-v1.4\python\python.exe")
    foreach ($p in $paths) { if (Test-Path $p) { return $p } }
    throw "Python not found!"
}
function Find-FFmpeg {
    $paths = @((Get-Command ffmpeg.exe -ErrorAction SilentlyContinue).Source,
               "F:\ComfyUI-aki-v1.4\ComfyUI-aki-v1.4\python\Scripts\ffmpeg.exe")
    foreach ($p in $paths) { if ($p -and (Test-Path $p)) { return $p } }
    throw "FFmpeg not found!"
}

try { $PYTHON = Find-Python; $FFMPEG = Find-FFmpeg }
catch { Write-Error $_.Exception.Message; exit 1 }

Write-Host "=== Render Video v3 ===" -ForegroundColor Cyan
Write-Host "DeckDir: $DeckDir"
Write-Host "TTS: $(if($WithTTS){'enabled'}else{'disabled'})"

$htmlPath = Join-Path $DeckDir "index.html"
if (-not (Test-Path $htmlPath)) { Write-Error "index.html not found!"; exit 1 }
$htmlContent = Get-Content $htmlPath -Raw
$slideCount = ([regex]::Matches($htmlContent, '<section class="slide[ >]')).Count
Write-Host "Slides: $slideCount" -ForegroundColor Green

$pngDir = Join-Path $DeckDir "png"
if (Test-Path $pngDir) { Remove-Item -Recurse -Force $pngDir -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Path $pngDir -Force | Out-Null

$videoFile = Join-Path $DeckDir "teaching-video.mp4"
$workDir = Join-Path $DeckDir "work"
$audioDir = Join-Path $DeckDir "audio"

if (Test-Path $workDir) { Remove-Item -Recurse -Force $workDir -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Path $workDir -Force | Out-Null

# Step 1: Screenshots
Write-Host "`n[1/4] Screenshots (Playwright)..." -ForegroundColor Yellow
$env:PYTHONIOENCODING = "utf-8"
$screenshotScript = Join-Path $SCRIPT_DIR "screenshot_slides.py"
$output = & $PYTHON $screenshotScript $DeckDir 2>&1
$output | ForEach-Object { Write-Host "  $_" }
$rendered = @(Get-ChildItem $pngDir -Filter "slide_*.png").Count
Write-Host "Done: $rendered slides captured" -ForegroundColor Green
if ($rendered -eq 0) { Write-Error "No slides captured!"; exit 1 }

# Step 2: TTS
if ($WithTTS) {
    Write-Host "`n[2/4] TTS generation..." -ForegroundColor Yellow
    if (Test-Path $audioDir) { Remove-Item -Recurse -Force $audioDir -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Path $audioDir -Force | Out-Null
    
    $slidesJson = Join-Path $DeckDir "slides.json"
    $extractScript = Join-Path $SCRIPT_DIR "text_extract.py"
    
    if ((Test-Path $slidesJson) -and (Test-Path $extractScript)) {
        $env:PYTHONIOENCODING = "utf-8"
        $paragraphs = & $PYTHON $extractScript $slidesJson 2>$null
        $paraList = $paragraphs -split "`r`n|`n" | Where-Object { $_.Trim() -ne "" }
        
        for ($i = 0; $i -lt $paraList.Count; $i++) {
            $num = "{0:D3}" -f ($i+1)
            $audioFile = Join-Path $audioDir ("slide_" + $num + ".mp3")
            $tempFile = Join-Path $audioDir ("text_" + $num + ".txt")
            $text = $paraList[$i] -replace '^page \d+: ', ''
            $text | Out-File -FilePath $tempFile -Encoding UTF8
            Write-Host ("  [" + ($i+1) + "/" + $paraList.Count + "] TTS...") -NoNewline
            & $PYTHON -m edge_tts --voice $Voice --rate +0% --pitch +0Hz --file "$tempFile" --write-media "$audioFile" 2>&1 | Out-Null
            if (Test-Path $audioFile) {
                Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
                $sz = (Get-Item $audioFile).Length / 1KB
                Write-Host (" OK (" + ("{0:N0}" -f $sz) + " KB)") -ForegroundColor Green
            } else {
                Write-Host " FAILED" -ForegroundColor Red
            }
        }
    }
}

# Step 3: Build video segments
Write-Host "`n[3/4] Building video segments..." -ForegroundColor Yellow
$pngFiles = Get-ChildItem $pngDir -Filter "slide_*.png" | Sort-Object Name
$concatFile = Join-Path $workDir "concat.txt"

for ($i = 0; $i -lt $pngFiles.Count; $i++) {
    $png = $pngFiles[$i].FullName
    $num = $i + 1
    $numStr = "{0:D3}" -f $num
    $segVideo = Join-Path $workDir ("seg_" + $numStr + ".mp4")
    
    $audioFile = Join-Path $audioDir ("slide_" + $numStr + ".mp3")
    $dur = $DurationPerSlide
    
    if ($WithTTS -and (Test-Path $audioFile)) {
        $durInfo = & $FFMPEG -i "$audioFile" -f null - 2>&1 | Select-String "Duration"
        if ($durInfo) {
            $m = [regex]::Match($durInfo, 'Duration: (\d+):(\d+):(\d+\.\d+)')
            if ($m.Success) {
                $dur = [double]$m.Groups[1].Value * 3600.0 + [double]$m.Groups[2].Value * 60.0 + [double]$m.Groups[3].Value
                $dur = [math]::Max($dur + 1.5, $dur + 0.5)
            }
        }
        & $FFMPEG -y -loop 1 -i "$png" -i "$audioFile" -c:v libx264 -t $dur -pix_fmt yuv420p -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p" -c:a aac -b:a 128k -shortest "$segVideo" 2>$null
    } else {
        & $FFMPEG -y -loop 1 -i "$png" -c:v libx264 -t $dur -pix_fmt yuv420p -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p" "$segVideo" 2>$null
    }
    
    if ((Get-Item $segVideo -ErrorAction SilentlyContinue).Length -gt 0) {
        $line = "file 'seg_" + $numStr + ".mp4'"
        $line | Out-File $concatFile -Append -Encoding ASCII
        $segSize = (Get-Item $segVideo).Length / 1MB
        Write-Host ("  Seg " + $numStr + ": " + ("{0:N1}" -f $segSize) + " MB | dur=" + ("{0:N1}" -f $dur) + "s")
    } else {
        Write-Host ("  Seg " + $numStr + ": FAILED") -ForegroundColor Yellow
    }
}

# Step 4: Concatenate
Write-Host "`n[4/4] Concatenating segments..." -ForegroundColor Yellow
if (Test-Path $concatFile) {
    Push-Location $workDir
    & $FFMPEG -y -f concat -safe 0 -i "$concatFile" -c copy "$videoFile" 2>$null
    Pop-Location
}

if ((Test-Path $videoFile) -and ((Get-Item $videoFile).Length -gt 0)) {
    $size = (Get-Item $videoFile).Length / 1MB
    Write-Host ("Video: " + $videoFile + " (" + ("{0:N1}" -f $size) + " MB)") -ForegroundColor Green
    Remove-Item -Recurse -Force $pngDir -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $audioDir -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $workDir -ErrorAction SilentlyContinue
    Write-Host "`n=== DONE ===" -ForegroundColor Green
} else {
    Write-Error "Video composition failed!"
    if (Test-Path $workDir) { Get-ChildItem $workDir | Select-Object Name, Length | Format-Table }
    exit 1
}
