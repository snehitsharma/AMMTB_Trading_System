
import asyncio
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Fix Windows Loop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load Env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from clients.rate_limiter import RateLimiter
from clients.fmp_client import FMPClient

async def test_bypass():
    print("🕵️ TESTING FMP STATIC BYPASS...")
    
    limiter = RateLimiter()
    client = FMPClient(limiter)
    
    # Force Mock Call
    results = await client.get_screener_stocks(limit=50)
    
    print(f"\n📊 RESULTS: {len(results)} Candidates")
    if results:
        print(f"First 3: {[r['symbol'] for r in results[:3]]}")
    else:
        print("❌ FAILED: Returned Empty List.")

if __name__ == "__main__":
    try:
        asyncio.run(test_bypass())
    except Exception as e:
        print(f"CRASH: {e}")
