# Script PowerShell — Crea tutti gli ZIP delle Lambda per il deploy su AWS
# Eseguire dalla cartella: GitHub/Shift-X/Progetto3/
# Uso: .\build-zips.ps1

$ErrorActionPreference = "Stop"

Write-Host "==> SHIFT-X Progetto 3 — Build ZIP Lambda" -ForegroundColor Cyan

# Crea cartella output
New-Item -ItemType Directory -Path "zips" -Force | Out-Null

# ── Funzione helper ────────────────────────────────────────────────────────────
function Build-LambdaZip {
    param(
        [string]$Name,
        [string[]]$Files
    )
    $dest = "zips\$Name.zip"
    if (Test-Path $dest) { Remove-Item $dest -Force }
    
    # Copia i file in una temp dir piatta (senza sottocartelle nello zip)
    $tmp = "tmp_$Name"
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    foreach ($f in $Files) {
        if (Test-Path $f) {
            Copy-Item $f -Destination $tmp
        } else {
            Write-Warning "File non trovato: $f"
        }
    }
    
    Compress-Archive -Path "$tmp\*" -DestinationPath $dest -Force
    Remove-Item $tmp -Recurse -Force
    Write-Host "  [OK] $dest" -ForegroundColor Green
}

# ── GetMacroCategory ───────────────────────────────────────────────────────────
Write-Host "`n=> GetMacroCategory (λ1)"
Build-LambdaZip -Name "GetMacroCategory" -Files @(
    "GetMacroCategory\handler.js",
    "GetMacroCategory\db.js",
    "GetMacroCategory\Talk.js",
    "GetMacroCategory\categories.js"
)

# ── GetRelevantTags ────────────────────────────────────────────────────────────
Write-Host "`n=> GetRelevantTags (λ2)"
Build-LambdaZip -Name "GetRelevantTags" -Files @(
    "GetRelevantTags\handler.js",
    "GetRelevantTags\db.js",
    "GetRelevantTags\Talk.js",
    "GetRelevantTags\categories.js"
)

# ── GetTalksAndPlaylist ────────────────────────────────────────────────────────
Write-Host "`n=> GetTalksAndPlaylist (λ3)"
Build-LambdaZip -Name "GetTalksAndPlaylist" -Files @(
    "GetTalksAndPlaylist\handler.js",
    "GetTalksAndPlaylist\db.js",
    "GetTalksAndPlaylist\Talk.js"
)

# ── GetWatchNext ───────────────────────────────────────────────────────────────
Write-Host "`n=> GetWatchNext"
Build-LambdaZip -Name "GetWatchNext" -Files @(
    "GetWatchNext\handler.js",
    "GetWatchNext\db.js",
    "GetWatchNext\Talk.js"
)

# ── CareerPathMaster ───────────────────────────────────────────────────────────
Write-Host "`n=> CareerPathMaster (Lambda Master)"
Build-LambdaZip -Name "CareerPathMaster" -Files @(
    "CareerPathMaster\handler.js"
)

Write-Host "`n==> Tutti gli ZIP creati in: zips\" -ForegroundColor Cyan
Write-Host "Contenuto cartella zips\:" -ForegroundColor Yellow
Get-ChildItem "zips\" | Format-Table Name, Length
