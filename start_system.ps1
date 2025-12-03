Write-Host "🚀 AMMTB MASTER LAUNCH SEQUENCE INITIALIZED..." -ForegroundColor Cyan

# --- STEP 1: SECURITY AUDIT ---
$envFile = ".\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "❌ CRITICAL ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "   Please create the .env file with your Alpaca Keys before launching."
    Write-Host "   System Halted."
    Read-Host "Press Enter to Exit"
    exit
}
else {
    Write-Host "✅ Security Vault (.env) Detected." -ForegroundColor Green
}

# --- STEP 2: DEPENDENCY CHECK & REPAIR ---
Write-Host "🛠️  Checking & Installing Dependencies (This may take a moment)..." -ForegroundColor Yellow

function Install-Deps {
    param($path, $name)
    Write-Host "   > Checking $name..." -NoNewline
    # Quietly install dependencies. If they exist, this is fast.
    Start-Process powershell -ArgumentList "-Command", "cd $path; if (Test-Path 'venv') { .\venv\Scripts\activate; pip install -r requirements.txt -q } else { Write-Host 'No venv found for $name' }" -Wait -WindowStyle Hidden
    Write-Host " Done." -ForegroundColor Green
}

# We run a quick install check on all backends to ensure 'alpaca-py' is there
Install-Deps -path "us_backend" -name "US Agent"
Install-Deps -path "crypto_backend" -name "Crypto Agent"
Install-Deps -path "orchestrator" -name "Orchestrator"
Install-Deps -path "ai_engine" -name "AI Brain"

# --- STEP 3: LAUNCH MISSION CONTROL ---
Write-Host "🚦 All Systems Go. Initiating Launch..." -ForegroundColor Cyan

function Start-Service {
    param($path, $port, $title)
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $path; .\venv\Scripts\activate; uvicorn main:app --port $port --reload; Write-Host '$title Running on Port $port'"
}

# 1. Backends
Start-Service -path "us_backend" -port 8001 -title "US Agent"
Start-Service -path "crypto_backend" -port 8002 -title "Crypto Agent"
# Start-Service -path "india_backend" -port 8003 -title "India Agent" # Disabled

# 2. Intelligence & Safety
Start-Service -path "ai_engine" -port 8004 -title "AI Brain"
Start-Service -path "orchestrator" -port 8005 -title "Orchestrator"

# 3. Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

# 4. Vital Signs Monitor
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python watch_brain.py"

Write-Host "✅ System Starting... Go to http://localhost:5173" -ForegroundColor Cyan
