from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import datetime
import pandas as pd
import pandas_ta as ta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import datetime
import pandas as pd
import pandas_ta as ta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CONFIG
US_AGENT = "http://localhost:8001"
CRYPTO_AGENT = "http://localhost:8002"
ORCHESTRATOR = "http://localhost:8005"
TRADING_ENABLED = True

# The Universe to Scan (Dynamic)
UNIVERSE = []
LAST_UNIVERSE_UPDATE = None

from strategy import StrategyEngine
from parallel_scanner import ParallelScanner

# Initialize Strategy & Scanner
strategy_engine = StrategyEngine()
scanner = ParallelScanner(strategy_engine, system_settings, US_AGENT, CRYPTO_AGENT)

# State
last_decisions = []

def update_universe():
    global UNIVERSE, LAST_UNIVERSE_UPDATE
    try:
        res = requests.get(f"{ORCHESTRATOR}/api/v1/universe", timeout=2)
        if res.status_code == 200:
            UNIVERSE = res.json()
            LAST_UNIVERSE_UPDATE = datetime.datetime.now()
            print(f"🌌 Universe Updated: {len(UNIVERSE)} assets")
        else:
            print("⚠️ Failed to fetch universe, using fallback.")
            if not UNIVERSE:
                UNIVERSE = ["AAPL", "NVDA", "TSLA", "MSFT", "AMD", "BTC/USD", "ETH/USD"]
    except Exception as e:
        print(f"Universe Update Error: {e}")
        if not UNIVERSE:
            UNIVERSE = ["AAPL", "NVDA", "TSLA", "MSFT", "AMD", "BTC/USD", "ETH/USD"]

def get_portfolio_positions():
    """Fetch current holdings from US & Crypto agents"""
    positions = set()
    total_equity = 100000.0 # Default fallback
    
    try:
        # Check US Agent
        us_res = requests.get(f"{US_AGENT}/api/v1/account/summary", timeout=2)
        if us_res.status_code == 200:
            data = us_res.json()
            if "total_equity" in data:
                total_equity = float(data["total_equity"])
        
        us_pos = requests.get(f"{US_AGENT}/api/v1/positions", timeout=2)
        if us_pos.status_code == 200:
            for p in us_pos.json():
                positions.add(p.get("symbol"))
            
        # Check Crypto Agent
        crypto_pos = requests.get(f"{CRYPTO_AGENT}/api/v1/positions", timeout=2)
        if crypto_pos.status_code == 200:
             for p in crypto_pos.json():
                positions.add(p.get("symbol"))
                
    except Exception as e:
        print(f"Portfolio Fetch Error: {e}")
        
    return positions, total_equity

def execute_trade(market, symbol, side, qty, reason):
    """Fire the trade to the backend"""
    url = US_AGENT if market == "US" else CRYPTO_AGENT
    payload = {"symbol": symbol, "qty": float(qty), "side": side, "type": "market"}
    
    # Round qty for crypto vs stocks
    if market == "US":
        payload["qty"] = int(qty)
    else:
        payload["qty"] = round(qty, 4)

    try:
        # 1. Log to Orchestrator
        requests.post(f"{ORCHESTRATOR}/api/v1/log_event", json={
            "source": "AI_BRAIN", "event": "EXECUTION", "details": {"message": f"Attempting {side} {symbol}: {reason}"}
        })
        
        # 2. Fire Trade (If Enabled)
        if TRADING_ENABLED:
            requests.post(f"{url}/api/v1/trade", json=payload, timeout=2)
            print(f"🚀 LIVE TRADE SENT: {side} {payload['qty']} {symbol} | {reason}")
        else:
            print(f"⚠️ TRADING DISABLED: Simulating {side} {payload['qty']} {symbol}")
            
    except Exception as e:
        print(f"Trade Failed: {e}")

from settings import system_settings, Settings

@app.get("/api/v1/settings")
def get_settings():
    return system_settings

@app.post("/api/v1/settings")
def update_settings(new_settings: Settings):
    global system_settings
    system_settings = new_settings
    # Update scanner settings too
    scanner.settings = new_settings
    return {"status": "updated", "settings": system_settings}

def analyze_asset(market, symbol, owned_assets, equity):
    """Fetch history, run strategy, return decision"""
    url = US_AGENT if market == "US" else CRYPTO_AGENT
    
    # --- GUARDRAIL: MAX POSITIONS ---
    if len(owned_assets) >= system_settings.max_positions and symbol not in owned_assets:
        return {"asset": symbol, "price": 0, "action": "WAIT", "reason": f"Max Positions Reached ({len(owned_assets)}/{system_settings.max_positions})"}
    # --------------------------------

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
        # Pass settings to strategy
        decision = strategy_engine.analyze_symbol(symbol, history, is_owned, equity, system_settings)
        
        action = decision["action"]
        reason = decision["reason"]
        price = decision["price"]
        qty = decision.get("quantity", 0)

        # 3. Execute (if BUY or SELL)
        if action == "BUY" and qty > 0:
            execute_trade(market, symbol, "buy", qty, reason)
        elif action == "SELL":
            # For sell, we'd need to know how much we own. For now, we just log it.
            # execute_trade(market, symbol, "sell", 1, reason) 
            pass

        return {"asset": symbol, "price": price, "action": action, "reason": reason}

    except Exception as e:
        print(f"Analysis Error {symbol}: {e}")
        return {"asset": symbol, "price": 0, "action": "ERROR", "reason": str(e)}

@app.post("/api/v1/manual_trade")
def manual_trade(trade: dict):
    """
    Endpoint for Manual User Overrides.
    Logs the event to Orchestrator and routes to the correct agent.
    """
    symbol = trade.get("symbol")
    side = trade.get("side")
    qty = float(trade.get("qty"))
    order_type = trade.get("type", "market")
    limit_price = trade.get("limit_price")
    
    # Determine Market
    market = "CRYPTO" if "/" in symbol else "US"
    url = US_AGENT if market == "US" else CRYPTO_AGENT
    
    try:
        # 1. Log to Orchestrator (Audit Trail)
        requests.post(f"{ORCHESTRATOR}/api/v1/log_event", json={
            "source": "MANUAL_USER", 
            "event": "OVERRIDE", 
            "details": {"message": f"User Manually Executed {side.upper()} {qty} {symbol} ({order_type.upper()})"}
        })
        
        # 2. Prepare Payload
        payload = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": order_type
        }
        if limit_price:
            payload["limit_price"] = float(limit_price)
            
        # 3. Fire Trade
        res = requests.post(f"{url}/api/v1/trade", json=payload, timeout=5)
        
        if res.status_code == 200:
            return res.json()
        else:
            return {"status": "error", "message": f"Agent Error: {res.text}"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def root():
    return {"status": "Brain Online (StrategyEngine Active)"}

@app.get("/signals")
@app.get("/api/v1/signals")
def get_signals():
    global last_decisions, UNIVERSE
    
    # 0. Update Universe (if needed)
    if not UNIVERSE or (datetime.datetime.now() - (LAST_UNIVERSE_UPDATE or datetime.datetime.min)).seconds > 300:
        update_universe()

    # 1. Get State
    owned_assets, equity = get_portfolio_positions()
    
    # 2. Parallel Scan
    decisions = scanner.scan_universe(UNIVERSE, owned_assets, equity)
    
    # 3. Execute Trades
    for d in decisions:
        if d["action"] == "BUY" and d.get("quantity", 0) > 0:
            market = "CRYPTO" if "/" in d["asset"] else "US"
            execute_trade(market, d["asset"], "buy", d["quantity"], d["reason"])
    
    last_decisions = decisions
    
    # Determine Regime based on BTC
    btc_decision = next((d for d in decisions if d["asset"] == "BTC/USD"), None)
    regime = "NEUTRAL"
    if btc_decision:
        if "Oversold" in btc_decision["reason"]: regime = "RISK_ON"
        if "Overbought" in btc_decision["reason"]: regime = "RISK_OFF"

    return {
        "regime": regime,
        "signal": "ACTIVE_STRATEGY",
        "confidence": 0.9,
        "scan_results": decisions,
        "universe_size": len(UNIVERSE),
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/api/v1/live_analysis")
def get_live_analysis():
    """Returns the full analysis feed for the frontend"""
    return last_decisions
