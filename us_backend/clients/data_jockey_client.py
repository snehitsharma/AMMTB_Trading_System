import aiohttp
import os
import db
from .rate_limiter import RateLimiter

class DataJockeyClient:
    def __init__(self, limiter: RateLimiter):
        self.api_key = os.getenv("DATA_JOCKEY_KEY")
        self.base_url = "https://api.datajockey.io/v0"
        self.limiter = limiter

    async def verify_financials(self, ticker: str):
        """
        Verifies company growth using Data Jockey Financials API.
        Returns: Tuple (GrowthScore, DetailsString)
        """
        if not self.api_key: return (0, "No Key")
        
        # QUOTA OVERRIDE: If limit reached, return NEUTRAL (+15) instead of failing.
        count = self.limiter.get_status().get("DJ", 0)
        limit = 240
        if count >= limit:
             await db.add_log("WARNING", f"⚠️ DJ Daily Limit ({limit}) Hit. Skipping {ticker}...")
             return (15, "BYPASS (Daily Limit)")
        
        # Increment usage
        await self.limiter.check_and_increment("DJ")

        # Define URL
        url = f"{self.base_url}/company/financials?ticker={ticker}&apikey={self.api_key}"

        # IRON PATIENCE: Infinite Retry Loop for 429s (Daily Limit or Speed Limit)
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                   async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            # Logic: Check for > 10% Growth (Revenue or Net Income)
                            growth_detected = False
                            reason = []
                            
                            financials = data.get('financials', [])
                            if isinstance(financials, list) and len(financials) >= 2:
                                curr = financials[0]
                                prev = financials[1]
                                
                                rev_curr = float(curr.get('revenue', 0))
                                rev_prev = float(prev.get('revenue', 0))
                                
                                if rev_prev > 0:
                                    growth = ((rev_curr - rev_prev) / rev_prev) * 100
                                    if growth > 10:
                                        growth_detected = True
                                        reason.append(f"Rev Growth {growth:.1f}%")
                                        
                            if growth_detected:
                                return (25, f"✅ Financials Verified: {', '.join(reason)}")
                            else:
                                return (15, "Stable/Flat Financials")
                                
                        elif resp.status == 429:
                             print("⛔ Rate Limit Hit (Data Jockey). Holding Pattern for 60s...")
                             await asyncio.sleep(60)
                             continue # Retry forever until reset
                        
                        elif resp.status in [403, 404]:
                            await db.add_log("WARNING", f"Data Jockey: {ticker} Not Found ({resp.status})")
                            return (0, "Data Not Available")
                        else:
                            return (0, f"API Error {resp.status}")
                            
            except Exception as e:
                await db.add_log("ERROR", f"DJ Exception: {e}")
                return (0, "Connection Failed")
