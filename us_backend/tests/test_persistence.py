from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_trade_persistence():
    # 1. Get initial account summary
    response_start = client.get("/api/v1/account/summary")
    assert response_start.status_code == 200
    equity_start = response_start.json()["total_equity"]
    print(f"Start Equity: {equity_start}")

    # 2. Place a trade (Buy 10 AAPL)
    trade_payload = {
        "symbol": "AAPL",
        "qty": 10,
        "side": "buy",
        "type": "market",
        "time_in_force": "gtc"
    }
    response_trade = client.post("/api/v1/trade", json=trade_payload)
    assert response_trade.status_code == 200
    print(f"Trade Response: {response_trade.json()}")

    # 3. Get final account summary
    response_end = client.get("/api/v1/account/summary")
    assert response_end.status_code == 200
    equity_end = response_end.json()["total_equity"]
    print(f"End Equity: {equity_end}")

    # 4. ASSERTION: Equity must change
    assert equity_end != equity_start, f"Equity did not change! Start: {equity_start}, End: {equity_end}"

if __name__ == "__main__":
    test_trade_persistence()

