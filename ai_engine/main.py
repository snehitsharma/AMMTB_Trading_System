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

from strategy import TechnicalStrategy
from strategy_manager import StrategyManager
from strategies.insider_strategy import InsiderMomentumStrategy
from parallel_scanner import ParallelScanner
from data_ingestion import InsiderDataIngestor
from settings import system_settings, Settings

# Initialize Data Ingestor (Insider Trading)
insider_ingestor = InsiderDataIngestor()
insider_ingestor.start_scheduler(interval_minutes=60)

# Initialize Strategies
tech_strategy = TechnicalStrategy()
insider_strategy = InsiderMomentumStrategy(insider_ingestor)

# Initialize Manager & Register Strategies
strategy_manager = StrategyManager()
strategy_manager.register_strategy(tech_strategy)
strategy_manager.register_strategy(insider_strategy)

# Initialize Scanner with Manager
scanner = ParallelScanner(strategy_manager, system_settings, US_AGENT, CRYPTO_AGENT)

# Initialize Risk & Execution
from portfolio_manager import PortfolioManager
from execution_engine import ExecutionEngine
from event_engine import EventEngine
import asyncio

port_manager = PortfolioManager()
exec_engine = ExecutionEngine(port_manager, US_AGENT, CRYPTO_AGENT, ORCHESTRATOR)

# Initialize Event Engine
event_engine = EventEngine(strategy_manager, exec_engine, insider_ingestor, US_AGENT, CRYPTO_AGENT, ORCHESTRATOR)

# Initialize Backtester
from backtester import Backtester
backtester = Backtester(strategy_manager, US_AGENT, CRYPTO_AGENT)

@app.post("/api/v1/backtest")
def run_backtest(payload: dict):
    """
    Run a simulation.
    Payload: {"symbol": "AAPL", "strategy": "TECHNICAL", "days": 90}
    """
    symbol = payload.get("symbol", "AAPL")
    strategy = payload.get("strategy", "TECHNICAL")
    days = int(payload.get("days", 90))
    
    return backtester.run_backtest(symbol, strategy, days)

@app.get("/api/v1/risk")
def get_risk_status():
    """Return current risk metrics"""
    owned_assets, equity = get_portfolio_positions()
    # Estimate cash (simplified)
    # In reality we should fetch cash from agents, but for now we derive it
    # This is a placeholder estimation if we don't have exact cash
    # Let's try to fetch real cash from US agent if possible, or just use equity - holdings
    
    # For now, let's just ask PortfolioManager to calculate based on what we know
    # We need to pass current equity. 
    # We assume cash is equity * (1 - exposure) roughly, or we just pass equity and let PM handle it if it tracks cash.
    # The PM.get_risk_metrics needs equity and cash.
    
    # Let's fetch cash from US Agent for better accuracy
    cash = 100000.0 # Fallback
    try:
        us_res = requests.get(f"{US_AGENT}/api/v1/account/summary", timeout=1)
        if us_res.status_code == 200:
            cash = float(us_res.json().get("cash", 100000.0))
    except:
        pass
        
    return port_manager.get_risk_metrics(equity, cash)

@app.post("/api/v1/trade")
def execute_manual_trade(trade: dict):
    """
    Manual Trade Trigger via Smart Execution Engine.
    Payload: { "symbol": "AAPL", "action": "BUY", "price": 150.0 }
    """
    try:
        owned_assets, equity = get_portfolio_positions()
        # Calculate current holdings value roughly
        current_holdings_value = sum([p['market_value'] for p in owned_assets])
        
        signal = {
            "asset": trade["symbol"],
            "action": trade["action"],
            "price": float(trade["price"]),
            "reason": "Manual/API Trigger"
        }
        
        return exec_engine.execute_signal(signal, equity, current_holdings_value)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "ERROR", "reason": str(e)}

@app.get("/api/v1/trades")
def get_trade_history():
    """Return historical executed trades"""
    return exec_engine.get_trade_history()

@app.on_event("startup")
async def start_background_tasks():
    # Start Event Loop
    asyncio.create_task(event_engine.run_loop())

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
    positions = []
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
            positions.extend(us_pos.json())
            
        # Check Crypto Agent
        crypto_pos = requests.get(f"{CRYPTO_AGENT}/api/v1/positions", timeout=2)
        if crypto_pos.status_code == 200:
             positions.extend(crypto_pos.json())
                
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
    
    # Convert to set of symbols for scanner
    owned_symbols = {p['symbol'] for p in owned_assets}
    
    # 2. Parallel Scan
    decisions = scanner.scan_universe(UNIVERSE, owned_symbols, equity)
    
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

@app.get("/api/v1/insider_activity")
def get_insider_activity(symbol: str = "AAPL"):
    """Returns recent insider activity for a symbol"""
    return insider_ingestor.get_recent_activity(symbol)

@app.get("/api/v1/strategies")
def get_strategies():
    return strategy_manager.get_status()

@app.post("/api/v1/strategies/toggle")
def toggle_strategy(payload: dict):
    # Payload example: {"name": "TECHNICAL", "enabled": false}
    success = strategy_manager.set_active(payload["name"], payload["enabled"])
    return strategy_manager.get_status()
