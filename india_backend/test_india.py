import requests

def test_india():
    try:
        # 1. Health
        resp = requests.get("http://localhost:8003/api/v1/health")
        print(f"Health: {resp.json()}")
        
        # 2. Quote
        resp = requests.get("http://localhost:8003/api/v1/quote")
        print(f"Quote: {resp.json()}")
        
        # 3. Account
        resp = requests.get("http://localhost:8003/api/v1/account/summary")
        print(f"Account: {resp.json()}")
        
        # 4. Trade (Backtest)
        print("Placing Trade (Backtest)...")
        trade = {
            "symbol": "NIFTY",
            "qty": 1,
            "side": "buy",
            "type": "market",
            "time_in_force": "gtc"
        }
        resp = requests.post("http://localhost:8003/api/v1/trade", json=trade)
        print(f"Trade Result: {resp.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_india()
