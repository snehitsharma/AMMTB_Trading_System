import requests
import json

def test_risk():
    url = "http://localhost:8004/api/v1/risk"
    try:
        print(f"🛡️ Checking Risk Desk at {url}...")
        res = requests.get(url)
        
        if res.status_code == 200:
            data = res.json()
            print("✅ Risk Desk Online!")
            print(json.dumps(data, indent=2))
            
            # Verify Rules
            rules = data.get("rules", {})
            if rules.get("pos_size") == 0.05 and rules.get("max_exposure") == 0.25:
                print("✅ Strict Rules Verified (5% Size, 25% Exposure)")
            else:
                print("❌ Rule Mismatch! Check PortfolioManager.")
        else:
            print(f"❌ HTTP Error {res.status_code}: {res.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_risk()
