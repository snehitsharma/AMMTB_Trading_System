import requests
import time

url = "http://localhost:8002/api/v1"

def test_crypto():
    # 1. Get Quote
    print("Fetching Quote...")
    try:
        resp = requests.get(f"{url}/quote?symbol=BTC/USD")
        if resp.status_code != 200:
            print(f"Quote Failed: {resp.text}")
            return
        data = resp.json()
        price = data['price']
        print(f"BTC Price: {price}")
    except Exception as e:
        print(f"Quote Error: {e}")
        return

    # 2. Get Initial Balance
    print("Fetching Balance...")
    resp = requests.get(f"{url}/account/summary")
    start_balance = resp.json()['cash_balance']
    print(f"Start Balance: {start_balance}")

    # 3. Place Trade
    print("Placing Trade...")
    trade = {
        "symbol": "BTC/USD",
        "qty": 0.01,
        "side": "buy",
        "type": "market",
        "time_in_force": "gtc"
    }
    resp = requests.post(f"{url}/trade", json=trade)
    if resp.status_code != 200:
        print(f"Trade Failed: {resp.text}")
        return
    print(f"Trade Result: {resp.json()}")

    # 4. Get Final Balance
    print("Fetching Final Balance...")
    resp = requests.get(f"{url}/account/summary")
    end_balance = resp.json()['cash_balance']
    print(f"End Balance: {end_balance}")

    if end_balance < start_balance:
        print("SUCCESS: Balance decreased after trade.")
    else:
        print("FAILURE: Balance did not decrease.")

if __name__ == "__main__":
    test_crypto()
