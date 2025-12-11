
import os
from dotenv import load_dotenv
from pathlib import Path
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
import datetime

# Load Env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

KEY = os.getenv("ALPACA_API_KEY")
SEC = os.getenv("ALPACA_SECRET_KEY")

print(f"Testing Data API with Key: {KEY[:5]}...")

client = StockHistoricalDataClient(KEY, SEC)

# Request
req = StockBarsRequest(
    symbol_or_symbols="AAPL",
    timeframe=TimeFrame.Day,
    start=datetime.datetime(2024, 1, 1),
    limit=5
)

print("\n--- TEST 1: Default Feed ---")
try:
    bars = client.get_stock_bars(req)
    print(f"Success! Got {len(bars['AAPL'])} bars.")
except Exception as e:
    print(f"FAILED (Default): {e}")

print("\n--- TEST 2: IEX Feed (Free) ---")
try:
    req.feed = DataFeed.IEX
    bars = client.get_stock_bars(req)
    print(f"Success! Got {len(bars['AAPL'])} bars.")
except Exception as e:
    print(f"FAILED (IEX): {e}")
