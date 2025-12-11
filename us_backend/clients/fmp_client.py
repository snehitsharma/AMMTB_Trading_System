import aiohttp
import os
import db
from .rate_limiter import RateLimiter

class FMPClient:
    def __init__(self, limiter: RateLimiter):
        self.api_key = os.getenv("FMP_API_KEY")
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.limiter = limiter

    async def get_earnings_surprise(self, symbol: str):
        if not self.api_key: return None
        if not await self.limiter.check_and_increment("FMP"): return None
        
        url = f"{self.base_url}/earnings-surprises/{symbol}?apikey={self.api_key}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and isinstance(data, list):
                            return data[0] # Most recent
                    else:
                        await db.add_log("WARNING", f"FMP Error {resp.status} for {symbol}")
        except Exception as e:
            await db.add_log("ERROR", f"FMP Exception: {e}")
        return None

    async def get_analyst_ratings(self, symbol: str):
        if not self.api_key: return None
        if not await self.limiter.check_and_increment("FMP"): return None
        
        url = f"{self.base_url}/rating/{symbol}?apikey={self.api_key}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and isinstance(data, list):
                            return data[0]
        except: pass
        return None

    async def get_screener_stocks(self, limit: int = 50):
        # ⚠️ STATIC BYPASS: FMP Key has no Discovery Access (403).
        # We return a hardcoded high-beta universe to unblock the system.
        
        UNIVERSE = [
          "NVDA", "TSLA", "AAPL", "AMD", "MSFT", "AMZN", "GOOGL", "META", "NFLX",
          "COIN", "MSTR", "MARA", "RIOT", "CLSK", "HOOD", "DKNG", "PLTR", "SOFI",
          "INTC", "MU", "QCOM", "ARM", "AVGO", "SMCI",
          "SPY", "QQQ", "IWM", "TQQQ", "SQQQ", "SOXL", "SOXS",
          "GME", "AMC", "CVNA", "UPST", "AFRM", "AI",
          "JPM", "GS", "BAC", "C", "XOM", "CVX", "LLY"
        ]
        
        # Format as list of dicts to match expected FMP structure
        candidates = [{'symbol': ticker} for ticker in UNIVERSE]
        
        print(f"✅ FMP Bypass: Returning {len(candidates)} Static Targets.")
        return candidates

    async def _fetch_screener(self, url: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if isinstance(data, list):
                            return [s for s in data if s.get('sector') != 'Shell Companies']
                    else:
                        await db.add_log("WARNING", f"FMP Screener Error: {resp.status}")
        except Exception as e:
            await db.add_log("ERROR", f"FMP Screener Exception: {e}")
        return []
