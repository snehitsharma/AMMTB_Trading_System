
import asyncio
import os
import sys

# Add parent to path to import backend modules
sys.path.append(os.path.join(os.getcwd(), 'hodl_backend'))

# Mock Dependencies
import db
import hodl_scanner
import hodl_trader

async def run_e2e_simulation():
    print("🚀 Starting HODL Agent E2E Simulation...")
    
    # Setup Env
    db.DB_PATH = "test_simulation.db"
    await db.init_db()
    
    # 1. Simulate finding a Gem
    print("\n--- STEP 1: SCANNER FIND ---")
    token_address = "TEST_TOKEN_MINT_ADDRESS_123"
    symbol = "TESTGEM"
    
    # Manually invoke snipe logic (mocked wallet)
    scanner = hodl_scanner.HodlScanner()
    scanner.sniper_active = True # Force active even without key for simulation
    
    # Mock execute_snipe to avoid real API calls for this test, OR allow it to fail gracefully
    # Actually, we want to test the FLOW.
    # Let's manually inject a position as if snipe succeeded
    print(f"Simulating Snipe Execution for {symbol}...")
    await db.log_trade(token_address, "BUY", 0.001, 1000, "tx_sim_buy_1")
    await db.save_position(token_address, symbol, 0.001, 1000, sl_price=0.0008)
    
    positions = await db.get_open_positions()
    assert len(positions) == 1
    print(f"✅ Position Created: {positions[0]['symbol']} (Qty: {positions[0]['quantity']})")

    # 2. Simulate Monitor (Price Pump)
    print("\n--- STEP 2: MONITOR PUMP (TP1) ---")
    trader = hodl_trader.HodlTrader()
    
    # Mock the get_current_price method to simulate a pump
    original_get_price = trader.get_current_price
    async def mock_get_price_pump(addr): return 0.0025 # +150% Pump (TP1 Hit)
    trader.get_current_price = mock_get_price_pump
    trader.trader_active = False # Paper mode
    
    await trader.monitor_positions()
    
    # Verify TP1 Sold 50%
    positions = await db.get_open_positions()
    p = positions[0]
    # TP1: Sold 50% of 1000 = 500. Remaining = 500.
    assert p['quantity'] == 500 
    print(f"✅ TP1 Triggered! Remaining Qty: {p['quantity']} (Expected 500)")

    # 3. Simulate Monitor (Dump -> Stop Loss)
    print("\n--- STEP 3: MONITOR DUMP (Trailing Stop) ---")
    # Peak price should be 0.0025. Stop is 20% below peak = 0.0020
    # Let's drop price to 0.0018
    async def mock_get_price_dump(addr): return 0.0018
    trader.get_current_price = mock_get_price_dump
    
    await trader.monitor_positions()
    
    # Verify Closed
    positions = await db.get_open_positions()
    assert len(positions) == 0
    print("✅ Trailing Stop Triggered! Position Closed.")

    print("\n🎉 E2E Simulation Logic PASSED")
    
    # Cleanup
    if os.path.exists("test_simulation.db"):
        os.remove("test_simulation.db")

if __name__ == "__main__":
    asyncio.run(run_e2e_simulation())
