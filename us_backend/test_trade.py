import requests
import json

url = "http://localhost:8001/api/v1/trade"
payload = {
    "symbol": "AAPL",
    "qty": 10,
    "side": "buy",
    "type": "market",
    "time_in_force": "gtc"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
