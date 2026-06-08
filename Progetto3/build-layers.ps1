# Script PowerShell — Crea tutti i Layer npm per AWS Lambda
# Eseguire dalla cartella: GitHub/Shift-X/Progetto3/
# Uso: .\build-layers.ps1
# Prerequisito: Node.js e npm installati

$ErrorActionPreference = "Stop"

Write-Host "==> SHIFT-X Progetto 3 — Build Layer ZIP" -ForegroundColor Cyan

New-Item -ItemType Directory -Path "layers" -Force | Out-Null

# ── Funzione helper ────────────────────────────────────────────────────────────
function Build-Layer {
    param(
        [string]$Name,
        [string[]]$Packages
    )
    Write-Host "`n=> Layer: $Name" -ForegroundColor Yellow
    
    $layerPath = "layers\$Name\nodejs"
    New-Item -ItemType Directory -Path $layerPath -Force | Out-Null
    
    # Crea package.json minimo
    $pkgJson = '{"name":"layer","version":"1.0.0"}'
    $pkgJson | Out-File -FilePath "$layerPath\package.json" -Encoding UTF8
    
    # Installa i pacchetti
    $packagesStr = $Packages -join " "
    Write-Host "   npm install $packagesStr"
    Push-Location $layerPath
    npm install $Packages 2>&1 | Select-String -Pattern "added|warn|error"
    Pop-Location
    
    # Crea lo zip con struttura nodejs/node_modules/
    $dest = "layers\$Name-layer.zip"
    if (Test-Path $dest) { Remove-Item $dest -Force }
    Compress-Archive -Path "layers\$Name\nodejs" -DestinationPath $dest -Force
    
    $size = [math]::Round((Get-Item $dest).Length / 1MB, 1)
    Write-Host "  [OK] $dest ($size MB)" -ForegroundColor Green
}

# ── Layer 1: mongoose + dotenv ─────────────────────────────────────────────────
Build-Layer -Name "mongoose" -Packages @("mongoose", "dotenv")

# ── Layer 2: @aws-sdk/client-bedrock-runtime ───────────────────────────────────
Build-Layer -Name "bedrock" -Packages @("@aws-sdk/client-bedrock-runtime")

# ── Layer 3: @aws-sdk/client-lambda ───────────────────────────────────────────
Build-Layer -Name "lambda-sdk" -Packages @("@aws-sdk/client-lambda")

Write-Host "`n==> Layer creati in: layers\" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ora carica su AWS Lambda > Layers:" -ForegroundColor Yellow
Write-Host "  - layers\mongoose-layer.zip   → shiftx-mongoose-layer   (Node.js 18.x)"
Write-Host "  - layers\bedrock-layer.zip    → shiftx-bedrock-layer    (Node.js 18.x)"
Write-Host "  - layers\lambda-sdk-layer.zip → shiftx-lambda-layer     (Node.js 18.x)"
