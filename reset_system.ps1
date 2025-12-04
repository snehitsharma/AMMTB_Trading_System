Write-Host "⚠️  INITIATING SYSTEM RESET..." -ForegroundColor Yellow

# 1. Stop Processes (Optional, but good practice)
# taskkill /F /IM python.exe /T 2>$null

# 2. Delete Databases
If (Test-Path "orchestrator/ledger.db") {
    Remove-Item "orchestrator/ledger.db" -Force
    Write-Host "Deleted ledger.db" -ForegroundColor Red
}
If (Test-Path "ai_engine/insider.db") {
    Remove-Item "ai_engine/insider.db" -Force
    Write-Host "Deleted insider.db" -ForegroundColor Red
}

# 3. Delete Logs
Get-ChildItem -Path . -Recurse -Filter *.log | Remove-Item -Force
Write-Host "Deleted all .log files" -ForegroundColor Red

# 4. Clear PyCache (Optional)
# Get-ChildItem -Path . -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force

Write-Host "`n✅ SYSTEM RESET COMPLETE." -ForegroundColor Green
Write-Host "Restart the system to initialize fresh databases." -ForegroundColor Cyan
