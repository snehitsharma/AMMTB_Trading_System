import requests
import json

def test_backtest():
    url = "http://localhost:8004/api/v1/backtest"
    payload = {
        "symbol": "AAPL",
        "strategy": "TECHNICAL",
        "days": 30
    }
    
    try:
        print(f"🚀 Sending Backtest Request to {url}...")
        res = requests.post(url, json=payload)
        
        if res.status_code == 200:
            data = res.json()
            if "error" in data:
                print(f"❌ Backtest Error: {data['error']}")
            else:
                print("✅ Backtest Successful!")
                print(f"Metrics: {json.dumps(data['metrics'], indent=2)}")
                print(f"Equity Curve Points: {len(data['equity_curve'])}")
        else:
            print(f"❌ HTTP Error {res.status_code}: {res.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_backtest()
