
import os
import requests
import json
import time
import datetime
from pathlib import Path

# CONFIG
AGENTS = [
    {"name": "US Agent", "port": 8001, "url": "http://localhost:8001"},
    {"name": "Crypto Agent", "port": 8002, "url": "http://localhost:8002"},
    {"name": "India Agent", "port": 8003, "url": "http://localhost:8003"},
    {"name": "Orchestrator", "port": 8005, "url": "http://localhost:8005"},
    {"name": "HODL Agent", "port": 8006, "url": "http://localhost:8006"}
]

REPORT_PATH = r"d:\aamtb\AMMTB_Trading_System\antigravity\audit_report.json"
SUMMARY_PATH = r"d:\aamtb\AMMTB_Trading_System\antigravity\docs\AUDIT_SUMMARY.md"

final_report = {
    "generated_at": datetime.datetime.now().isoformat(),
    "services": [],
    "data_sources": [],
    "signals": [],
    "executions": [],
    "mismatches": [],
    "risk_controls": [],
    "logs": {},
    "tests": {"unit_passed": 0, "unit_failed": 0, "integration_passed": 0, "integration_failed": 0},
    "action_items": []
}

def check_services():
    print("--- Checking Services ---")
    for agent in AGENTS:
        service_data = {
            "name": agent["name"],
            "port": agent["port"],
            "status": "DEAD",
            "last_poll_ts": None,
            "auto_execute": False, # Default
            "paper_mode": True, # Default safety
            "placeholders_found": [],
            "last_errors": []
        }
        
        try:
            # Health Check
            try:
                if agent["name"] == "Orchestrator":
                     r = requests.get(f"{agent['url']}/")
                else: 
                     r = requests.get(f"{agent['url']}/")

                if r.status_code == 200:
                    service_data["status"] = "ALIVE"
                    service_data["last_poll_ts"] = datetime.datetime.now().isoformat()
                    print(f"✅ {agent['name']} is ALIVE")
                else:
                    print(f"⚠️ {agent['name']} returned {r.status_code}")
            except Exception as e:
                print(f"❌ {agent['name']} is DEAD: {e}")

            # Specific Checks if Alive
            if service_data["status"] == "ALIVE":
                # Check Configuration if available (assuming root returns status/mode)
                try:
                    r_root = requests.get(f"{agent['url']}/")
                    data = r_root.json()
                    # Infer mode from response or default
                    # Most agents verify connection at startup and print "ONLINE"
                except: pass

        except Exception as e:
             service_data["last_errors"].append(str(e))
        
        final_report["services"].append(service_data)

def check_env():
    print("--- Checking Environment ---")
    env_path = r"d:\aamtb\AMMTB_Trading_System\.env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
            keys_found = []
            for line in lines:
                if "=" in line and not line.startswith("#"):
                    key = line.split("=")[0].strip()
                    keys_found.append(key)
            
            # Identify missing critical keys
            required_keys = ["ALPACA_API_KEY", "ALPACA_SECRET_KEY", "SOLANA_PRIVATE_KEY"]
            missing = [k for k in required_keys if k not in keys_found]
            
            if missing:
                final_report["action_items"].append({
                    "priority": "HIGH",
                    "difficulty": "LOW",
                    "description": f"Missing critical .env keys: {', '.join(missing)}",
                    "location": ".env"
                })
            else:
                 print("✅ Critical .env keys present")
    else:
        final_report["action_items"].append({
            "priority": "CRITICAL",
            "difficulty": "LOW",
            "description": ".env file missing",
            "location": "Root Directory"
        })

def analyze_codebase():
    # Helper to check files for placeholders
    print("--- Analyzing Codebase ---")
    root_dir = r"d:\aamtb\AMMTB_Trading_System"
    
    # Check for "mock" or "placeholder" or "TODO" in key files
    files_to_check = [
        r"us_backend\main.py",
        r"crypto_backend\main.py",
        r"hodl_backend\hodl_scanner.py",
        r"orchestrator\main.py"
    ]
    
    for rel_path in files_to_check:
        full_path = os.path.join(root_dir, rel_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if "TODO" in line or "Placeholder" in line or "mock" in line.lower():
                        # Exclude some known benign comments if needed
                        final_report["services"][0]["placeholders_found"].append(f"{rel_path}:{i+1}:{line.strip()}")
                        
    # Check Ledger
    ledger_path = os.path.join(root_dir, "orchestrator", "ledger.db")
    if os.path.exists(ledger_path):
        print(f"✅ Ledger DB found at {ledger_path}")
    else:
        print("⚠️ Ledger DB not found")
        final_report["action_items"].append({
            "priority": "MEDIUM",
            "difficulty": "LOW",
            "description": "Ledger DB file missing (Orchestrator may not have run yet)",
            "location": "orchestrator/ledger.db"
        })

def save_reports():
    with open(REPORT_PATH, "w", encoding='utf-8') as f:
        json.dump(final_report, f, indent=2)
    
    # Generate Summary
    with open(SUMMARY_PATH, "w", encoding='utf-8') as f:
        f.write("# AMMTB System Audit Summary\n\n")
        f.write(f"**Generated At:** {final_report['generated_at']}\n\n")
        
        f.write("## Service Status\n")
        for s in final_report["services"]:
            status_icon = "✅" if s["status"] == "ALIVE" else "❌"
            f.write(f"- {status_icon} **{s['name']}** (Port {s['port']})\n")
        
        f.write("\n## Top Action Items\n")
        if not final_report["action_items"]:
            f.write("No critical issues found.\n")
        else:
            for item in final_report["action_items"]:
                prio_icon = "🔴" if item['priority'] == "CRITICAL" else "🟠" if item['priority'] == "HIGH" else "🟡"
                f.write(f"- {prio_icon} **[{item['priority']}]** {item['description']} *(Loc: {item['location']})*\n")

if __name__ == "__main__":
    check_env()
    check_services()
    analyze_codebase()
    save_reports()
    print("Audit Complete.")
