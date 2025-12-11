import requests
import time

AGENTS = {
    "US": "http://localhost:8001",
    "CRYPTO": "http://localhost:8002",
    "AI": "http://localhost:8004",
    "ORCHESTRATOR": "http://localhost:8005"
}

def check_agent(name, url):
    print(f"Testing {name} Agent at {url}...")
    try:
        # 1. Health Check
        try:
            health = requests.get(f"{url}/health", timeout=2).json()
            print(f"  ✅ Health: {health}")
        except:
             # Some agents might use root for health or have different endpoint
             try:
                 health = requests.get(f"{url}/", timeout=2).json()
                 print(f"  ✅ Health (Root): {health}")
             except:
                 print(f"  ⚠️ Health Check Failed")

        
        # 2. Data Check (Specific to agent type)
        if name in ["US", "CRYPTO"]:
            try:
                acct = requests.get(f"{url}/account/summary", timeout=2).json()
                print(f"  💰 Account: Equity=${acct.get('equity', 'N/A')}, Cash=${acct.get('cash', 'N/A')}")
            except Exception as e:
                print(f"  ❌ Account Check Failed: {e}")
            
            try:
                quote = requests.get(f"{url}/quote", timeout=2).json()
                print(f"  📈 Quote: {quote}")
            except Exception as e:
                print(f"  ❌ Quote Check Failed: {e}")
            
        if name == "AI":
            try:
                sigs = requests.get(f"{url}/signals", timeout=2).json()
                print(f"  🧠 Regime: {sigs.get('regime')}")
                scan = sigs.get('scan_results', [])
                print(f"  👀 Scanning: {len(scan)} assets")
                if scan:
                    print(f"     Sample: {scan[0]}")
            except Exception as e:
                print(f"  ❌ AI Signals Check Failed: {e}")

        if name == "ORCHESTRATOR":
            try:
                wallet = requests.get(f"{url}/api/v1/wallet/balance", timeout=2).json()
                print(f"  🏦 Wallet Balance: ${wallet.get('balance', 'N/A')}")
            except:
                 # Try without api/v1 prefix just in case
                try:
                    wallet = requests.get(f"{url}/wallet/balance", timeout=2).json()
                    print(f"  🏦 Wallet Balance: ${wallet.get('balance', 'N/A')}")
                except Exception as e:
                    print(f"  ❌ Wallet Check Failed: {e}")
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    print("-" * 40)

print("=== AMMTB SYSTEM DIAGNOSTIC ===")
for name, url in AGENTS.items():
    check_agent(name, url)
