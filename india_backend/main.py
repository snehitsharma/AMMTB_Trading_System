from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sys
import os
import datetime

# --- LOCAL INTELLIGENCE ---
try:
    from strategy import StrategyEngine
except ImportError:
    class StrategyEngine: 
        def analyze_symbol(self, *args): return {"action": "WAIT", "reason": "Brain Missing"}

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- STATE ---
STOCKS = ["RELIANCE", "TCS", "INFY", "HDFCBANK"]
MARKET_STATE = {"scan_results": [], "last_updated": "Never"}
strategy = StrategyEngine()

# --- SCANNER ---
async def market_scanner():
    print("🇮🇳 India Smart Agent: Scanner Started")
    while True:
        try:
            scan = []
            # Mock Data for India (No API yet)
            for sym in STOCKS:
                # Mock History
                history = [{"close": 2500, "high": 2550, "low": 2450, "open": 2500, "volume": 100000} for _ in range(100)]
                decision = strategy.analyze_symbol(sym, history, False, 100000, 100000)
                
                scan.append({
                    "asset": sym,
                    "price": 2500,
                    "action": decision["action"],
                    "reason": decision["reason"]
                })
            
            MARKET_STATE["scan_results"] = scan
            MARKET_STATE["last_updated"] = datetime.datetime.now().strftime('%H:%M:%S')
            
        except Exception as e:
            print(f"India Scanner Error: {e}")
        
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(market_scanner())

@app.get("/")
def root(): return {"status": "India Agent Online"}

@app.get("/account/summary")
def get_account():
    # Placeholder for Upstox/Zerodha
    return {"equity": 0, "cash": 0, "status": "COMING_SOON"}

@app.get("/signals")
def get_signals(): return MARKET_STATE["scan_results"]
