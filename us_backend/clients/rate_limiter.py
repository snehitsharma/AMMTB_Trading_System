
import time
import os
import json
import asyncio
import db

# Persistence File
LIMITS_FILE = os.path.join(os.path.dirname(__file__), "rate_limits.json")

class RateLimiter:
    def __init__(self):
        self.limits = {
            "FMP": 240,
            "DJ": 240,
            "TWELVE": 800
        }
        self.counts = self._load_counts()
        self.last_reset = self.counts.get("last_reset", time.time())

    def _load_counts(self):
        if os.path.exists(LIMITS_FILE):
            try:
                with open(LIMITS_FILE, "r") as f:
                    return json.load(f)
            except: pass
        return {"FMP": 0, "DJ": 0, "TWELVE": 0, "last_reset": time.time()}

    def _save_counts(self):
        with open(LIMITS_FILE, "w") as f:
            json.dump(self.counts, f)

    def _check_reset(self):
        # Reset if > 24 hours
        if time.time() - self.last_reset > 86400:
            self.counts = {"FMP": 0, "DJ": 0, "TWELVE": 0, "last_reset": time.time()}
            self._save_counts()
            print("🔄 Rate Limits Reset")

    async def check_and_increment(self, source: str) -> bool:
        """
        Returns True if call is allowed.
        """
        self._check_reset()
        
        limit = self.limits.get(source, 100)
        current = self.counts.get(source, 0)
        
        if current < limit:
            self.counts[source] = current + 1
            self._save_counts()
            # Log periodic usage warnings
            if current % 50 == 0:
                 await db.add_log("INFO", f"API Usage {source}: {current}/{limit}")
            return True
        else:
            await db.add_log("WARNING", f"🚫 API Limit Reached for {source} ({current}/{limit}). Request Blocked.")
            return False

    def get_status(self):
        return self.counts
