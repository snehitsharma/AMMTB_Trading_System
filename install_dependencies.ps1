$root = $PSScriptRoot
Write-Host "STARTING LINEAR INSTALL..."

Write-Host "1. US AGENT"
Set-Location "$root\us_backend"
if (-not (Test-Path "venv")) { python -m venv venv }
.\venv\Scripts\python -m pip install -r requirements.txt

Write-Host "2. CRYPTO AGENT"
Set-Location "$root\crypto_backend"
if (-not (Test-Path "venv")) { python -m venv venv }
.\venv\Scripts\python -m pip install -r requirements.txt

Write-Host "3. HODL AGENT"
Set-Location "$root\hodl_backend"
if (-not (Test-Path "venv")) { python -m venv venv }
.\venv\Scripts\python -m pip install -r requirements.txt

Write-Host "4. ORCHESTRATOR"
Set-Location "$root\orchestrator"
if (-not (Test-Path "venv")) { python -m venv venv }
.\venv\Scripts\python -m pip install -r requirements.txt

Write-Host "ALL DONE. READY TO START."
