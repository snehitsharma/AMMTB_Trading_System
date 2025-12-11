
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.data.enums import DataFeed

# Load Env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

async def run_sanity():
    print("🏥 ALPACA SANITY CHECK")
    
    if not API_KEY:
        print("❌ KEYS MISSING")
        return

    # 1. Check Trading API (Account Status)
    try:
        trade_client = TradingClient(API_KEY, SECRET_KEY, paper=False)
        acct = trade_client.get_account()
        print(f"✅ TRADING API: Connected. Status: {acct.status}, Equity: ${acct.equity}")
    except Exception as e:
        print(f"❌ TRADING API FAILED: {e}")

    # 2. Check Data API (Latest Trade) on Multiple Feeds
    data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    
    for feed in [DataFeed.IEX, DataFeed.SIP]:
        feed_name = str(feed)
        print(f"\n🧪 Testing Data Feed: {feed_name}")
        try:
            req = StockLatestTradeRequest(symbol_or_symbols="NVDA", feed=feed)
            trade = data_client.get_stock_latest_trade(req)
            if "NVDA" in trade:
                t = trade["NVDA"]
                print(f"✅ DATA SUCCESS ({feed_name}): Price ${t.price} at {t.timestamp}")
            else:
                print(f"⚠️ DATA EMPTY ({feed_name})")
        except Exception as e:
            print(f"❌ DATA FAILED ({feed_name}): {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_sanity())
