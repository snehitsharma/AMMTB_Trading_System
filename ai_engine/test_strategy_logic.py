from strategy_manager import StrategyManager
from strategy import TechnicalStrategy
from strategies.insider_strategy import InsiderMomentumStrategy
from data_ingestion import InsiderDataIngestor
from settings import system_settings
import pandas as pd
import numpy as np
import pandas as pd
import numpy as np

def test_strategy_logic():
    print("🧪 Testing Strategy Manager Logic...")

    # 1. Setup
    ingestor = InsiderDataIngestor(db_path="test_insider.db")
    # Force some mock data for AAPL
    ingestor.save_filings([{
        "ticker": "AAPL", "insider_name": "Tim Cook", "role": "CEO", 
        "transaction_type": "Purchase", "shares": 5000, "price": 150, 
        "value": 750000, "date": "2025-12-04"
    }])
    
    manager = StrategyManager()
    manager.register_strategy(TechnicalStrategy())
    manager.register_strategy(InsiderMomentumStrategy(ingestor))
    
    # 2. Create Mock History (Uptrend)
    print("\n--- Generating Mock History (Uptrend) ---")
    history = []
    price = 100
    for i in range(100):
        price += 0.5 # Steady uptrend
        history.append({
            "close": price, "open": price, "high": price+1, "low": price-1, "volume": 1000000, "timestamp": "2025-01-01"
        })
    
    # 3. Run Analysis
    print("\n--- Running Analysis for AAPL ---")
    decision = manager.run_all_strategies("AAPL", history, False, 100000, system_settings)
    
    print(f"Decision: {decision['action']}")
    print(f"Reason: {decision['reason']}")
    
    if "Insider Conviction" in decision['reason']:
        print("✅ Insider Strategy Triggered Successfully!")
    else:
        print("❌ Insider Strategy Failed to Trigger.")

if __name__ == "__main__":
    test_strategy_logic()
