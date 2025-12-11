import requests
import pandas as pd
from datetime import datetime

class UniverseGenerator:
    def __init__(self):
        self.tickers = ["AAPL", "NVDA", "TSLA", "MSFT", "AMD", "SPY", "QQQ"] # Fallback
        self.last_update = None

    def get_top_active(self, limit=20):
        """
        Fetches Top Active stocks (High Volume) to focus scanning on what's moving.
        Refreshes list every 60 minutes to save resources.
        """
        # Return cached if fresh
        if self.last_update and (datetime.now() - self.last_update).seconds < 3600:
            return self.tickers[:limit]

        print("📡 Fetching Dynamic Market Universe...")
        try:
            # Use Yahoo Finance "Day Gainers" API (Free, Unofficial)
            headers = {'User-Agent': 'Mozilla/5.0'}
            url = "https://query2.finance.yahoo.com/v1/finance/screener/predefined/saved/day_gainers?count=25"
            r = requests.get(url, headers=headers, timeout=5)
            data = r.json()
            
            new_tickers = []
            for quote in data['finance']['result'][0]['quotes']:
                sym = quote['symbol']
                # Filter out junk (penny stocks, warrants)
                if len(sym) <= 4 and quote.get('regularMarketPrice', 0) > 10:
                    new_tickers.append(sym)
            
            if new_tickers:
                self.tickers = new_tickers
                self.last_update = datetime.now()
                print(f"✅ Universe Updated: {len(self.tickers)} assets")
            
        except Exception as e:
            print(f"⚠️ Screener Failed ({e}). Using Fallback list.")
        
        return self.tickers[:limit]
