import asyncio
import requests
import pandas as pd
from datetime import datetime
from strategy_manager import StrategyManager
from execution_engine import ExecutionEngine
from data_ingestion import InsiderDataIngestor

class EventEngine:
    def __init__(self, strategy_manager: StrategyManager, execution_engine: ExecutionEngine, insider_ingestor: InsiderDataIngestor, us_agent_url, crypto_agent_url, orchestrator_url):
        self.strategy_manager = strategy_manager
        self.execution_engine = execution_engine
        self.insider_ingestor = insider_ingestor
        self.US_AGENT = us_agent_url
        self.CRYPTO_AGENT = crypto_agent_url
        self.ORCHESTRATOR = orchestrator_url
        
        # State
        self.last_prices = {} # {symbol: {price: float, time: datetime}}
        self.running = False

    async def run_loop(self):
        """Main Event Loop"""
        self.running = True
        print("🚀 Event Engine Started")
        self._log_event("SYSTEM_START", "Event Engine Active")
        
        while self.running:
            try:
                # 1. Price & Volume Watcher
                await self.check_market_data()
                
                # 2. Filing Watcher
                await self.check_new_filings()
                
                # Sleep to prevent CPU hogging
                await asyncio.sleep(60) # Check every minute
                
            except Exception as e:
                print(f"⚠️ Event Loop Error: {e}")
                await asyncio.sleep(60)

    async def check_market_data(self):
        """Checks for Price Spikes and Volume Surges"""
        # For now, we'll just check a few key assets to avoid API limits
        watchlist = ["AAPL", "NVDA", "TSLA", "BTC/USD", "ETH/USD"]
        
        for symbol in watchlist:
            try:
                # Fetch Data
                agent = self.CRYPTO_AGENT if "/" in symbol else self.US_AGENT
                # We need a quick quote endpoint, but for now we can use /history with limit=1
                # Or better, just use the agent's quote if available. 
                # Let's assume we can get a quote. If not, we skip.
                
                # Simulating data fetch for now to avoid complex async requests structure in this snippet
                # In a real scenario, we'd call: requests.get(f"{agent}/api/v1/quote?symbol={symbol}")
                # Here we will rely on the main loop's data if possible, or just skip for this MVP step
                pass 

            except Exception as e:
                pass

    async def check_new_filings(self):
        """Polls for new insider filings"""
        # In a real system, we'd track the last_id seen.
        # Here we'll just check if the ingestor has new data in memory or DB.
        # Since the ingestor runs on its own thread, we can just query it.
        pass

    def trigger_strategy(self, symbol, event_type, details):
        """Triggers strategies immediately"""
        print(f"⚡ Event Triggered: {event_type} on {symbol}")
        self._log_event(event_type, f"{symbol}: {details}")
        
        # We need history to run strategies. 
        # For this MVP, we might not have it readily available without fetching.
        # So we'll log the trigger for now.
        
        # Future: Fetch history -> self.strategy_manager.run_all_strategies(...)

    def _log_event(self, event_type, message):
        try:
            requests.post(f"{self.ORCHESTRATOR}/log_event", json={
                "event": event_type,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
        except:
            pass
