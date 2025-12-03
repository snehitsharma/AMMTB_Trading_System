from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

class ParallelScanner:
    def __init__(self, strategy_engine, settings, us_agent_url, crypto_agent_url):
        self.strategy_engine = strategy_engine
        self.settings = settings
        self.us_agent = us_agent_url
        self.crypto_agent = crypto_agent_url

    def analyze_asset(self, symbol, owned_assets, equity):
        """
        Single Asset Analysis Task
        """
        market = "CRYPTO" if "/" in symbol else "US"
        url = self.us_agent if market == "US" else self.crypto_agent
        
        # --- GUARDRAIL: MAX POSITIONS ---
        if len(owned_assets) >= self.settings.max_positions and symbol not in owned_assets:
            return {"asset": symbol, "price": 0, "action": "WAIT", "reason": f"Max Positions Reached ({len(owned_assets)}/{self.settings.max_positions})"}

        try:
            # 1. Fetch History
            res = requests.get(f"{url}/api/v1/history?symbol={symbol}&limit=100", timeout=5)
            if res.status_code != 200:
                return {"asset": symbol, "price": 0, "action": "ERROR", "reason": "History fetch failed"}
            
            history = res.json()
            if not history:
                 return {"asset": symbol, "price": 0, "action": "WAIT", "reason": "No Data"}

            # 2. Run Strategy
            is_owned = symbol in owned_assets
            decision = self.strategy_engine.analyze_symbol(symbol, history, is_owned, equity, self.settings)
            
            # Enrich with indicators for frontend
            decision["indicators"] = {
                "rsi": decision.get("rsi", 0),
                "macd": decision.get("macd", 0),
                "atr": decision.get("atr", 0)
            }
            
            return decision

        except Exception as e:
            # print(f"Analysis Error {symbol}: {e}")
            return {"asset": symbol, "price": 0, "action": "ERROR", "reason": str(e)}

    def scan_universe(self, universe, owned_assets, equity):
        """
        Run analysis in parallel
        """
        results = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(self.analyze_asset, sym, owned_assets, equity): sym for sym in universe}
            
            for future in as_completed(futures):
                try:
                    res = future.result()
                    results.append(res)
                except Exception as e:
                    print(f"Scanner Exception: {e}")
                    
        return results
