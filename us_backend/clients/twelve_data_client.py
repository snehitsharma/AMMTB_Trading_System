import aiohttp
import os
import db
from .rate_limiter import RateLimiter

class TwelveDataClient:
    def __init__(self, limiter: RateLimiter):
        self.api_key = os.getenv("TWELVE_DATA_KEY")
        self.base_url = "https://api.twelvedata.com"
        self.limiter = limiter

    async def get_crypto_price(self, symbol: str = "BTC/USD"):
        if not self.api_key: return None
        if not await self.limiter.check_and_increment("TWELVE"): return None
        
        url = f"{self.base_url}/price?symbol={symbol}&apikey={self.api_key}"
        # IRON PATIENCE: Infinite Retry Loop for 429s
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            # Success Path
                            if "price" in data:
                                return float(data["price"])
                            else:
                                await db.add_log("WARNING", f"12Data Missing Price: {data}")
                                return 100000.0 # Fallback
                        elif resp.status == 429:
                            print("⛔ Rate Limit Hit (12Data). Holding Pattern for 60s...")
                            await asyncio.sleep(60)
                            continue # Retry
                        else:
                            await db.add_log("WARNING", f"12Data Error {resp.status}")
                            return 100000.0 # Fallback on non-retryable error
                            
            except Exception as e:
                await db.add_log("ERROR", f"12Data Exception: {e}")
                return 100000.0
