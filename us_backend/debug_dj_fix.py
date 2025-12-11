
import asyncio
import os
from clients.data_jockey_client import DataJockeyClient
from clients.rate_limiter import RateLimiter
from dotenv import load_dotenv

load_dotenv()

async def test():
    print("--- 🔎 DEBUG: Data Jockey URL Fix Verification ---")
    limiter = RateLimiter()
    client = DataJockeyClient(limiter)
    
    tickers = ["AAPL", "PLTR"]
    for t in tickers:
        print(f"\nTesting {t}...")
        score, details = await client.verify_financials(t)
        print(f"Result: Score={score}, Details='{details}'")

if __name__ == "__main__":
    asyncio.run(test())
