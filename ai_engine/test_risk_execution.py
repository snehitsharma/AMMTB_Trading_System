from portfolio_manager import PortfolioManager
from execution_engine import ExecutionEngine

def test_risk_execution():
    print("🧪 Testing Risk & Execution Infrastructure...")
    
    # 1. Setup
    pm = PortfolioManager()
    # Mock URLs
    ee = ExecutionEngine(pm, "http://mock-us", "http://mock-crypto", "http://mock-orch")
    
    equity = 100000
    pm.update_equity(equity)
    
    # 2. Test Max Position Size (Should Reject)
    print("\n--- Test 1: Max Position Size ---")
    # Try to buy $20k worth (20% of equity, limit is 10%)
    signal_large = {"asset": "AAPL", "action": "BUY", "price": 150, "quantity": 133} 
    res = ee.execute_signal(signal_large, equity)
    if res['status'] == "REJECTED" and "exceeds 10%" in res['reason']:
        print("✅ Large Trade Rejected Correctly.")
    else:
        print(f"❌ Large Trade Failed Check: {res}")

    # 3. Test Valid Trade (Should pass risk, fail network - which is expected)
    print("\n--- Test 2: Valid Trade ---")
    # Try to buy $5k worth (5% of equity)
    signal_valid = {"asset": "AAPL", "action": "BUY", "price": 150, "quantity": 33}
    res = ee.execute_signal(signal_valid, equity)
    
    # We expect NETWORK_ERROR because mock URLs don't exist, but that means it passed risk check
    if res['status'] == "ERROR" and "Network Error" in res['reason']:
        print("✅ Valid Trade Passed Risk (Network Error Expected).")
    elif res['status'] == "REJECTED":
        print(f"❌ Valid Trade Rejected: {res['reason']}")
    else:
        print(f"❓ Unexpected Result: {res}")

if __name__ == "__main__":
    test_risk_execution()
