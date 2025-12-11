Write-Host "AMMTB LAUNCHER STARTING..." -ForegroundColor Cyan

# 1. Security Check
if (-not (Test-Path ".\.env")) {
    Write-Host "ERROR: .env file missing! Create it first." -ForegroundColor Red
    exit
}

# 2. Dependency Check (Simple)
function Install-Deps {
    param($path, $name)
    Write-Host "Checking $name..." -NoNewline
    
    if (-not (Test-Path "$path\venv")) {
        Write-Host " [Installing]..." -ForegroundColor Yellow
        Start-Process "python" -ArgumentList "-m venv $path\venv" -Wait -NoNewWindow
        
        $pip = "$path\venv\Scripts\python"
        Start-Process $pip -ArgumentList "-m pip install -r $path\requirements.txt -q" -Wait -NoNewWindow
        Write-Host " Done." -ForegroundColor Green
    }
    else {
        Write-Host " Ready." -ForegroundColor Gray
    }
}

Install-Deps -path "us_backend" -name "US Agent"
Install-Deps -path "india_backend" -name "India Agent"
Install-Deps -path "crypto_backend" -name "Crypto Agent"
Install-Deps -path "hodl_backend" -name "HODL Agent"
Install-Deps -path "orchestrator" -name "Orchestrator"

# 3. Launch Services
function Start-Service {
    param($path, $port, $title)
    
    # Get Absolute Paths to avoid relative path errors after CD
    if (Test-Path "$path\run.py") {
        # Check for venv python
        if (Test-Path "$path\venv\Scripts\python.exe") {
            # Use absolute path to python
            $python = (Convert-Path "$path\venv\Scripts\python.exe")
            # Use & operator to execute
            $cmd = "cd $path; & '$python' run.py; Read-Host 'Stopped'"
        }
        else {
            $cmd = "cd $path; python run.py; Read-Host 'Stopped'"
        }
    }
    else {
        # Fallback to uvicorn if run.py missing
        $cmd = "cd $path; .\venv\Scripts\activate; uvicorn main:app --port $port --reload; Read-Host 'Stopped'"
    }
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
}

Start-Service -path "us_backend" -port 8001 -title "US Agent"
Start-Service -path "crypto_backend" -port 8002 -title "Crypto Agent"
Start-Service -path "india_backend" -port 8003 -title "India Agent"
Start-Service -path "orchestrator" -port 8005 -title "Orchestrator"
# Create run.py for HODL locally or share logic? HODL will likely crash too.
# I'll create run.py for HODL in next step. For now US Agent is patched.
Start-Service -path "hodl_backend" -port 8006 -title "HODL Agent"

# 4. Launch Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"
