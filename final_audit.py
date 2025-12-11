import os

ROOT_DIR = r"d:\aamtb\AMMTB_Trading_System"

def audit():
    print("🏥 STARTING FINAL SYSTEM HEALTH SCAN...", flush=True)
    warnings = []
    errors = []

    # 1. Scan for Legacy Imports
    print("\n🔍 Scanning for Legacy Code...", flush=True)
    legacy_patterns = ["alpaca_trade_api"]
    exclude_dirs = [".git", "node_modules", "venv", "__pycache__", "dist"]
    
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(".py") and file != "final_audit.py":
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        for pattern in legacy_patterns:
                            if pattern in content:
                                warnings.append(f"Legacy string '{pattern}' found in {os.path.relpath(path, ROOT_DIR)}")
                except Exception as e:
                    errors.append(f"Could not read {path}: {e}")

    # 2. Verify Service Structure
    print("\n🏗️ Verifying Service Structure...", flush=True)
    services = ["us_backend", "crypto_backend", "hodl_backend", "orchestrator"]
    for svc in services:
        svc_path = os.path.join(ROOT_DIR, svc)
        if not os.path.exists(svc_path):
            errors.append(f"Service Missing: {svc}")
        else:
            if not os.path.exists(os.path.join(svc_path, "main.py")):
                errors.append(f"Missing main.py in {svc}")
            if not os.path.exists(os.path.join(svc_path, "requirements.txt")):
                warnings.append(f"Missing requirements.txt in {svc}")

    # 3. Validate Requirements
    print("\n📦 Validating Dependencies...", flush=True)
    
    # US Agent
    us_req = os.path.join(ROOT_DIR, "us_backend", "requirements.txt")
    if os.path.exists(us_req):
        with open(us_req, "r") as f:
            content = f.read()
            if "alpaca-py" not in content:
                errors.append("US Agent missing 'alpaca-py' in requirements.txt")
            if "alpaca_trade_api" in content:
                errors.append("US Agent has LEGACY 'alpaca_trade_api' in requirements.txt")

    # Crypto Agent
    crypto_req = os.path.join(ROOT_DIR, "crypto_backend", "requirements.txt")
    if os.path.exists(crypto_req):
        with open(crypto_req, "r") as f:
            content = f.read()
            if "alpaca-py" not in content:
                errors.append("Crypto Agent missing 'alpaca-py' in requirements.txt")
    
    # HODL Agent
    hodl_req = os.path.join(ROOT_DIR, "hodl_backend", "requirements.txt")
    if os.path.exists(hodl_req):
        with open(hodl_req, "r") as f:
            content = f.read()
            if "solana" not in content:
                warnings.append("HODL Agent missing 'solana' in requirements.txt (Check if intended)")

    # 4. Check Port Configuration
    print("\n🔌 Checking Ports...", flush=True)
    launcher = os.path.join(ROOT_DIR, "start_system.ps1")
    if os.path.exists(launcher):
        with open(launcher, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if "8001" not in content: errors.append("Launcher missing Port 8001 (US)")
            if "8002" not in content: errors.append("Launcher missing Port 8002 (Crypto)")
            if "8005" not in content: errors.append("Launcher missing Port 8005 (Orchestrator)")
            if "8006" not in content: errors.append("Launcher missing Port 8006 (HODL)")
    else:
        errors.append("start_system.ps1 MISSING")

    # Frontend Proxy
    vite = os.path.join(ROOT_DIR, "frontend", "vite.config.ts")
    if os.path.exists(vite):
        with open(vite, "r") as f:
            content = f.read()
            if "8001" not in content: errors.append("Frontend Proxy missing Port 8001")
            if "8002" not in content: errors.append("Frontend Proxy missing Port 8002")
            if "8006" not in content: errors.append("Frontend Proxy missing Port 8006")
    else:
        errors.append("frontend/vite.config.ts MISSING")

    print("\n" + "="*30)
    print("📊 HEALTH REPORT SUMMARY")
    print("="*30)
    
    if not errors and not warnings:
        print("✅ SYSTEM CLEAN. READY FOR PRODUCTION.")
    else:
        if errors:
            print(f"\n❌ ERRORS FOUND ({len(errors)}):")
            for e in errors: print(f" - {e}")
        if warnings:
            print(f"\n⚠️ WARNINGS ({len(warnings)}):")
            for w in warnings: print(f" - {w}")

if __name__ == "__main__":
    audit()
