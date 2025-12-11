
import os
import sys
import datetime
from pathlib import Path
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
import pandas as pd
import pandas_ta as ta

# Load Env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

def analyze_nvda():
    print("🕵️ DEEP DIVE: NVDA (MULTI-FEED TEST)")
    
    if not API_KEY or not SECRET_KEY:
        print("❌ Error: Missing API Keys")
        return

    client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    
    end_dt = datetime.datetime.now()
    start_dt = end_dt - datetime.timedelta(days=250)
    
    print(f"📅 Fetching History: {start_dt.date()} to {end_dt.date()}")
    
    # Test multiple feeds
    feeds_to_test = [DataFeed.IEX, DataFeed.SIP, None]
    data = None
    used_feed = "NONE"

    for feed in feeds_to_test:
        feed_name = str(feed) if feed else "DEFAULT"
        print(f"\n🧪 TESTING FEED: {feed_name}")
        try:
            req = StockBarsRequest(
                symbol_or_symbols="NVDA",
                timeframe=TimeFrame.Day,
                start=start_dt,
                limit=200,
                feed=feed
            )
            bars = client.get_stock_bars(req)
            if "NVDA" in bars and len(bars["NVDA"]) > 0:
                print(f"✅ SUCCESS on {feed_name}! Found {len(bars['NVDA'])} bars.")
                data = bars["NVDA"]
                used_feed = feed_name
                break
            else:
                 print(f"⚠️ {feed_name} returned Empty List.")
        except Exception as e:
            print(f"⚠️ Failed on {feed_name}: {e}")

    if not data:
        print("\n❌ ALL FEEDS FAILED. No data found.")
        return

    # Proceed with Analysis
    try:
        # Convert to DF
        history = [{"close": b.close, "open": b.open, "high": b.high, "low": b.low, "volume": b.volume} for b in data]
        df = pd.DataFrame(history)
        
        # Calculate Indicators
        df.ta.rsi(length=14, append=True)
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        
        last = df.iloc[-1]
        
        price = last['close']
        rsi = last.get('RSI_14', 0)
        ema20 = last.get('EMA_20', 0)
        vol_curr = last['volume']
        vol_avg = df['volume'].mean()
        
        rel_vol = vol_curr / vol_avg if vol_avg > 0 else 0
        
        print("\n--- 🔍 INTERNAL STATE REPORT ---")
        print(f"Feed Used:       {used_feed}")
        print(f"Raw Price:       {price}")
        print(f"Calculated RSI:  {rsi}")
        print(f"Calculated EMA20:{ema20}")
        print(f"Current Volume:  {vol_curr}")
        print(f"Avg Volume:      {vol_avg:.2f}")
        print(f"Rel Vol Ratio:   {rel_vol:.4f}x")
        print("-------------------------------")
        
        # Check Filters
        print("\n--- ⚖️ FILTER CHECK ---")
        print(f"RSI Check (>80?):   {'FAIL (Too High)' if rsi > 80 else 'PASS'}")
        print(f"Trend Check (<EMA?): {'FAIL (Downtrend)' if price < ema20 else 'PASS'}")
        print(f"Vol Check (>0.1x?): {'FAIL (Low Vol)' if rel_vol < 0.1 else 'PASS'}")
        
    except Exception as e:
        print(f"❌ CRASH DURING ANALYSIS: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_nvda()
