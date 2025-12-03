import requests
import pandas as pd
import random
from datetime import datetime

class UniverseEngine:
    def __init__(self):
        self.universe = []
        self.last_updated = None
        # Default fallback
        self.fallback_universe = ["AAPL", "NVDA", "TSLA", "MSFT", "AMD", "COIN", "GOOGL", "AMZN", "META", "NFLX"]

    def fetch_insider_trades(self):
        """
        Mock/Fetch Insider Trading Data.
        In a real scenario, this would scrape OpenInsider.
        For stability, we simulate 'Hot' insider stocks.
        """
        # TODO: Implement real scraping
        # For now, return a random selection of high-beta stocks
        candidates = ["PLTR", "SOFI", "MARA", "RIOT", "DKNG"]
        return random.sample(candidates, 2)

    def fetch_technical_movers(self):
        """
        Fetch top gainers/losers or high volume stocks from Alpaca (via US Agent if needed, or direct).
        For now, we return a static high-momentum list.
        """
        # In production, call US Agent /v1/screener
        return ["NVDA", "AMD", "SMCI", "ARM", "TSLA"]

    def generate_universe(self):
        """
        Combine multiple sources to build the Master Universe.
        """
        print("🌌 Generating New Universe...")
        
        insiders = self.fetch_insider_trades()
        technical = self.fetch_technical_movers()
        # Add some staples
        staples = ["AAPL", "MSFT", "BTC/USD", "ETH/USD"]
        
        combined = list(set(insiders + technical + staples))
        
        self.universe = combined
        self.last_updated = datetime.now()
        
        print(f"✅ Universe Generated: {len(self.universe)} assets")
        return self.universe

    def get_universe(self):
        if not self.universe:
            return self.generate_universe()
        return self.universe
