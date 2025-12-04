import requests
import json
import time

def test_us_agent():
    url = "http://localhost:8001/api/v1/trade"
    print(f"🧪 Testing US Agent Direct: {url}")
    payload = {
        "symbol": "AAPL",
        "side": "buy",
        "qty": 1,
        "type": "market",
        "take_profit": 200.0,
        "stop_loss": 100.0
    }
    try:
        res = requests.post(url, json=payload)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_see():
    url = "http://localhost:8004/api/v1/trade"
    
    # 1. Test Buy (Should Pass Risk & Execute)
    payload = {
        "symbol": "AAPL",
        "action": "BUY",
        "price": 150.0
    }
    
    try:
        print(f"\n🚀 Sending Trade Request to {url}...")
        res = requests.post(url, json=payload)
        
        if res.status_code == 200:
            data = res.json()
            print("✅ Trade Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ HTTP Error {res.status_code}: {res.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    # test_us_agent()
    test_see()
