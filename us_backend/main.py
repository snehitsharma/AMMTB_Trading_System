from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
import pandas as pd
from yahoo_fin import stock_info as si
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
from alpaca.trading.requests import MarketOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
import os
from dotenv import load_dotenv
import time
import datetime
import asyncio
import sys
from contextlib import asynccontextmanager
from strategy import StrategyEngine
# Deprecated: from insider_scanner import get_insider_candidates 

# AGD MODULES
from clients.rate_limiter import RateLimiter
from clients.fmp_client import FMPClient
from clients.twelve_data_client import TwelveDataClient
from clients.data_jockey_client import DataJockeyClient
from analysis.scoring import calculate_confluence_score

# Load Environment Variables
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# STATE
LATEST_SIGNALS = []
SCANNER_SIGNALS = [{"asset": "DRAGNET_SYSTEM", "price": 0, "action": "WAIT", "reason": "Initializing Bio-Digital Protocol...", "source": "AGD_CORE"}] 
LAST_DRAGNET_RAW = [] 
STATUS = "BOOTING"

# CLIENTS
trading_client = None
data_client = None
limiter = RateLimiter()
fmp_client = FMPClient(limiter)
twelve_client = TwelveDataClient(limiter)
dj_client = DataJockeyClient(limiter)
strategy_engine = StrategyEngine()

# CLIENT_INIT
# CLIENT_INIT
def init_alpaca():
    global trading_client, data_client, STATUS, mode_label
    try:
        API_KEY = os.getenv("ALPACA_API_KEY")
        SECRET = os.getenv("ALPACA_SECRET_KEY")
        if API_KEY and SECRET:
            # Auto-Detect Live Mode if Key starts with AK
            if API_KEY.startswith("AK"):
                 is_paper = False
                 print(f"DEBUG: Live Key Detected ({API_KEY[:4]}...). Forcing ONLINE mode.")
            else:
                 is_paper = os.getenv("ALPACA_PAPER", "True").lower() == "true"

            trading_client = TradingClient(API_KEY, SECRET, paper=is_paper)
            data_client = StockHistoricalDataClient(API_KEY, SECRET)
            
            mode_label = "PAPER" if is_paper else "LIVE (REAL MONEY)"
            STATUS = f"ONLINE ({mode_label})"
    except Exception as e:
        print(f"❌ US Agent Init Fail: {e}")
        STATUS = "ERROR"

import db

# STATE - Add startup log
async def startup_logging():
    await db.init_db()
    await db.add_log("INFO", f"US Agent Booting up... Mode: {STATUS}")
    
    # SYSTEM DIAGNOSTIC
    print("\n--- 🧬 BIO-DIGITAL SYSTEM DIAGNOSTIC 🧬 ---")
    print(f"Alpaca Connection: {'✅ CONNECTED' if trading_client else '❌ FAIL'}")
    print(f"FMP Client: {'✅ READY' if os.getenv('FMP_API_KEY') else '❌ KEY MISSING'}")
    print(f"Data Jockey: {'✅ READY' if os.getenv('DATA_JOCKEY_KEY') else '❌ KEY MISSING'}")
    print(f"12Data Client: {'✅ READY' if os.getenv('TWELVE_DATA_KEY') else '❌ KEY MISSING'}")
    print("-------------------------------------------\n")

# LOOP
async def run_trading_loop():
    global LATEST_SIGNALS, LAST_DRAGNET_RAW, SCANNER_SIGNALS
    
    await db.add_log("INFO", "🔄 Bio-Digital Dragnet: Activated")
    print("🔄 Bio-Digital Dragnet: Activated")
    
    while True:
        # --- AUTONOMY: FOREVER LOOP ---
        try:
             clock = await asyncio.to_thread(trading_client.get_clock)
             if not clock.is_open:
                  print("⏳ Market Closed. Sleeping 1 Hour...")
                  await asyncio.sleep(3600)
                  continue
        except Exception as ce:
             print(f"⚠️ Clock Check Failed: {ce}")
             await asyncio.sleep(60)
             continue
             
        if not trading_client or not data_client:
            await db.add_log("WARNING", "Waiting for Alpaca Client initialization...")
            await asyncio.sleep(10)
            continue
            
            
        try:
            # 1. Get Summary & Positions
            if 'last_scan_time' not in locals(): last_scan_time = 0
            current_time = time.time()

            print("💓 Pulse: Checking Acct...")
            acct = await asyncio.to_thread(trading_client.get_account)
            print("💓 Pulse: Account Checked.")
            positions = await asyncio.to_thread(trading_client.get_all_positions)
            equity = float(acct.equity)
            buying_power = float(acct.buying_power)
            
            # --- PHASE 0: EXIT MANAGEMENT (Manage Risk) ---
            for p in positions:
                symbol = p.symbol
                qty = float(p.qty)
                try:
                    # History for Exit
                    end_dt = datetime.datetime.now()
                    start_dt = end_dt - datetime.timedelta(days=250) 
                    req = StockBarsRequest(symbol_or_symbols=symbol, timeframe=TimeFrame.Day, start=start_dt, limit=200, feed=DataFeed.IEX)
                    bars = await asyncio.to_thread(data_client.get_stock_bars, req)
                    if symbol not in bars: continue
                    history = [{"close": b.close, "open": b.open, "high": b.high, "low": b.low, "volume": b.volume} for b in bars[symbol]]
                    
                    decision = strategy_engine.analyze_symbol(symbol, history, is_owned=True, equity=equity, buying_power=buying_power)
                    
                    # --- SOFT BRACKET (Client-Side Exit) ---
                    # Works for Fractional Shares
                    profit_pct = float(p.unrealized_plpc)
                    if profit_pct >= 0.06:
                        decision = {'action': 'SELL', 'reason': f"Take Profit (+{profit_pct*100:.1f}%)"}
                    elif profit_pct <= -0.03:
                        decision = {'action': 'SELL', 'reason': f"Stop Loss ({profit_pct*100:.1f}%)"}
                    
                    if decision['action'] == "SELL":
                        msg = f"📉 AGD SELL: {symbol} | Reason: {decision['reason']}"
                        await db.add_log("ACTION", msg)
                        print(msg)
                        order_req = MarketOrderRequest(symbol=symbol, qty=qty, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
                        await asyncio.to_thread(trading_client.submit_order, order_req)
                except Exception as ex_e:
                    print(f"Exit Check Error {symbol}: {ex_e}")

            # --- WALLET GUARD (Resource Saver) ---
            # DUAL HEARTBEAT CHECK
            if (current_time - last_scan_time) < 3600 and LAST_DRAGNET_RAW:
                 # print(f"🛡️ Sentinel Active. Checking exits... (Next Scan in ~{int((3600 - (current_time - last_scan_time))/60)} mins)")
                 await asyncio.sleep(1) # Yield
                 continue

            last_scan_time = current_time

            cash_available = float(acct.non_marginable_buying_power)
            if cash_available < 2.00:
                 msg = f"🛡️ Wallet Guard: Cash ${cash_available:.2f} < $2.00. Standing By (1Hr)."
                 print(msg)
                 await db.add_log("INFO", msg)
                 await asyncio.sleep(3600)
                 continue

            # --- PHASE 1: THE DRAGNET (Discovery) ---
            dragnet_candidates = []
            current_minute = datetime.datetime.now().minute
            
            # Run Dragnet at top of hour OR if raw list is empty (Startup)
            if current_minute == 0 or not LAST_DRAGNET_RAW:
                 try: 
                     await db.add_log("INFO", "🕸️ Deploying Hybrid Dragnet...")
                     
                     # 1. THE PATROL (Static List)
                     static_patrol = await fmp_client.get_screener_stocks(limit=50)
                     candidates = set([x['symbol'] for x in static_patrol])
                     
                     # 2. THE SCOUT (Dynamic Yahoo Lists)
                     try:
                         print("💓 Pulse: Scouting Most Active...")
                         actives = si.get_day_most_active()[:20]
                         active_tickers = [x for x in actives.index if isinstance(x, str)] if hasattr(actives, 'index') else list(actives['Symbol'])[:20] 
                         # Yahoo_fin returns pandas df typically.
                         # Correction: si.get_day_most_active() returns a DataFrame. Column 0 is Symbol usually?
                         # Let's use a safer extraction if possible, or just try/except.
                         # Actually yahoo_fin returns a DF with "Symbol" column.
                         
                         active_tickers = actives['Symbol'].tolist()[:20]
                         candidates.update(active_tickers)
                         
                         print("💓 Pulse: Scouting Gainers...")
                         gainers = si.get_day_gainers()[:10]
                         gainer_tickers = gainers['Symbol'].tolist()[:10]
                         candidates.update(gainer_tickers)
                         
                         await db.add_log("INFO", f"✅ Static: {len(static_patrol)} | 🌊 Active: {len(active_tickers)} | 🚀 Gainers: {len(gainer_tickers)}")
                     except Exception as ye:
                         print(f"⚠️ Scout Failed: {ye}")
                         await db.add_log("WARNING", f"Hybrid Scout Failed (using Static): {ye}")

                     dragnet_candidates = list(candidates)
                     LAST_DRAGNET_RAW = dragnet_candidates
                     await db.add_log("INFO", f"🕸️ Total Universe: {len(dragnet_candidates)} Targets.")
                 except Exception as e: 
                     await db.add_log("ERROR", f"Dragnet Failed: {e}")
            else:
                 dragnet_candidates = LAST_DRAGNET_RAW

            NEW_AGD_SIGNALS = []
            valid_candidates = []
            discarded_count = 0
            survivor_count = 0

            for i, ticker in enumerate(dragnet_candidates):
                print(f"💓 Phase 2: Processing [{i+1}/{len(dragnet_candidates)}] {ticker}...")
                # --- PHASE 2: THE SIEVE (Local Filter) ---
                try:
                    # Fetch History (Yahoo Finance Bypass)
                    # print(f"🔎 Checking {ticker} via YF...")
                    df = await asyncio.to_thread(yf.download, ticker, period="60d", interval="1d", progress=False)
                    
                    if df.empty or len(df) < 50:
                        discarded_count += 1
                        continue

                    # Flatten MultiIndex if present (YF v0.2+)
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    
                    # Normalize columns for AGD Strategy Engine
                    # Expected: close, open, high, low, volume
                    df = df.rename(columns={
                        "Close": "close", "Open": "open", "High": "high", "Low": "low", "Volume": "volume"
                    })
                    
                    # Convert to list of dicts (for compatibility with existing StrategyEngine)
                    history = df[['close', 'open', 'high', 'low', 'volume']].to_dict('records')
                    current_price = history[-1]['close']

                    # Local Technical Analysis
                    decision = strategy_engine.analyze_symbol(ticker, history, is_owned=False, equity=100000)
                    tech_data = decision.get("tech_data", {})
                    
                    # THE SIEVE: Strict Local Filter
                    if decision['action'] != "BUY_CHECK":
                        # VERBOSE: Log ALL rejections to DB for remote debugging
                        rej_msg = f"❌ Rejected [{ticker}]: {decision['reason']} | RSI: {tech_data.get('rsi',0):.1f} | Vol: {tech_data.get('rel_vol',0):.1f}x"
                        print(rej_msg)
                        await db.add_log("WARNING", rej_msg)
                        discarded_count += 1
                        continue
                    
                    survivor_count += 1

                    # --- PHASE 3: THE TRIBUNAL (Deep Verification) ---
                    # Data Jockey Financials Check
                    # IRON PATIENCE: No Bypass. We wait for the API.
                    dj_score, dj_details = await dj_client.verify_financials(ticker)
                    print(f"🔎 Checking {ticker} (Data Jockey)... {dj_details}")
                    
                    btc_price = await twelve_client.get_crypto_price("BTC/USD")
                    
                    # --- PHASE 4: THE VERDICT (Confluence Scoring) ---
                    # Calculate Technical & Macro Score first
                    confluence_score, score_report = calculate_confluence_score(
                        insider_data=[], # Replaced by DJ Financials
                        earnings_data=None, # Replaced by DJ Financials
                        technicals=tech_data,
                        macro_data={"btc": btc_price}
                    )
                    
                    # Add Data Jockey Growth Score (+25)
                    confluence_score += dj_score
                    if dj_score > 0:
                        score_report.append(f"DJ Financials ({dj_details})")
                    
                    verdict = "WATCH"
                    if confluence_score >= 80: verdict = "STRONG BUY"
                    elif confluence_score >= 40: verdict = "WATCH"
                    else: verdict = "IGNORE"
                    
                    # LOGGING
                    report_log = (
                        f"🎯 AGD SIGNAL REPORT: {ticker}\n"
                        f"Confidence Score: {confluence_score} / 100\n"
                        f"Verdict: {verdict}\n\n"
                        f"Signal Stack:\n"
                        f"✅ Sieve Passed: RSI {tech_data.get('rsi',0):.1f}, RelVol {tech_data.get('rel_vol',0):.1f}x\n"
                        f"✅ Data Jockey: {dj_details}\n"
                        f"✅ Macro (12Data): BTC ${'%.0f' % (btc_price or 0)}\n\n"
                        f"API Limits: {limiter.get_status()}"
                    )
                    
                    # Only log Watch/Buy to keep noise down, or log all? 
                    # Directive says "Log: ..." implies detailed log.
                    await db.add_log("ACTION", report_log)
                    print(report_log)
                    
                    NEW_AGD_SIGNALS.append({
                        "asset": ticker,
                        "price": current_price,
                        "action": verdict,
                        "reason": f"Score {confluence_score}",
                        "source": "AGD_DRAGNET"
                    })
                    
                    # --- PHASE 5: SIGNAL ACCUMULATION (The Leaderboard) ---
                    if verdict == "STRONG BUY":
                        valid_candidates.append({
                            'ticker': ticker, 
                            'score': confluence_score,
                            'price': current_price
                        })

                except Exception as e:
                    await db.add_log("ERROR", f"Sieve/Tribunal Failed {ticker}: {e}")
                
                # ⏳ PACER: Slow Scan (The Metronome)
                print(f"⏳ Pacing: Sleeping 15s to respect API limits...")
                await asyncio.sleep(15)
            
            # Log Sieve Summary
            if discarded_count > 0 or survivor_count > 0:
                await db.add_log("INFO", f"📉 Sieve Status: {discarded_count} discarded, {survivor_count} survivors.")

            if NEW_AGD_SIGNALS:
                SCANNER_SIGNALS = NEW_AGD_SIGNALS

            # --- PHASE 6: THE OLYMPICS (Ranked Execution) ---
            if valid_candidates and os.getenv("US_AGENT_AUTO_BUY", "False").lower() == "true":
                # 1. Sort by Score (Desc)
                valid_candidates.sort(key=lambda x: x['score'], reverse=True)
                
                # 2. Take Top 3
                podium = valid_candidates[:3]
                
                await db.add_log("INFO", f"🏆 Leaderboard Finalists: {[x['ticker'] for x in podium]}")
                
                # 3. Execute sequentially
                for candidate in podium:
                    ticker = candidate['ticker']
                    score = candidate['score']
                    
                    try:
                        acct_now = await asyncio.to_thread(trading_client.get_account)
                        cash_power = float(acct_now.non_marginable_buying_power)
                        
                        # 30% Allocation
                        trade_amount = round(cash_power * 0.30, 2)
                        if trade_amount < 2.00: trade_amount = round(cash_power * 0.95, 2)
                        
                        if trade_amount < 1.00:
                             await db.add_log("WARNING", f"💰 Insufficient Funds for {ticker}. Skipping.")
                             continue
                             
                        trigger_msg = f"⚡ OLYMPIC EXECUTION: Buying ${trade_amount} of {ticker} (Score: {score})"
                        print(trigger_msg)
                        await db.add_log("SUCCESS", trigger_msg)
                        
                        order_req = MarketOrderRequest(
                            symbol=ticker, 
                            notional=trade_amount, 
                            side=OrderSide.BUY, 
                            time_in_force=TimeInForce.DAY
                        )
                        await asyncio.to_thread(trading_client.submit_order, order_req)
                        print(f"⚡ Trade Filled: {ticker}")
                        
                    except Exception as exe:
                         await db.add_log("ERROR", f"Olympic Exec Failed {ticker}: {exe}")

        except Exception as e:
            await db.add_log("ERROR", f"Dragnet Loop Failure: {e}")
            print(f"⚠️ Dragnet Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Dual-Heartbeat: Sleep 60s to check exits frequently.
        # print("⏳ Cycle Complete. Sleeping 60s...")
        await asyncio.sleep(60) 

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_alpaca()
    await startup_logging()
    loop = asyncio.create_task(run_trading_loop())
    yield
    loop.cancel()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- ENDPOINTS ---
@app.get("/")
def root(): return {"status": "Bio-Digital Dragnet Online", "mode": STATUS}

@app.get("/account/summary")
def get_account():
    if not trading_client: return {"equity": 0, "status": STATUS}
    try:
        acct = trading_client.get_account()
        return {
            "equity": float(acct.equity), 
            "cash": float(acct.cash), 
            "buying_power": float(acct.buying_power),
            "status": "ACTIVE_DRAGNET"
        }
    except: return {"equity": 0, "status": "ERROR"}

@app.get("/positions")
def get_positions():
    if not trading_client: return []
    try:
        return [p.dict() for p in trading_client.get_all_positions() if p.asset_class == 'us_equity']
    except: return []

@app.get("/signals")
def get_signals():
    # Fallback to Scanner Signals if main loop hasn't merged yet
    return LATEST_SIGNALS if LATEST_SIGNALS else SCANNER_SIGNALS

@app.get("/scanner/insider")
def get_raw_dragnet():
    return {"candidates": LAST_DRAGNET_RAW, "count": len(LAST_DRAGNET_RAW)}

@app.get("/health")
def health_check():
    # 1. Alpaca Status
    alpaca_status = "ok" if trading_client else "fail"
    try:
        trading_client.get_clock()
    except:
        alpaca_status = "error"

    # 2. Scanner Status
    scanner_status = "ok"
    
    return {
        "alpaca_status": alpaca_status,
        "scanner_status": scanner_status,
        "mode": "PAPER" if os.environ.get('ALPACA_PAPER', 'True') == 'True' else "LIVE",
        "auto_buy": os.environ.get('US_AGENT_AUTO_BUY', 'False')
    }

@app.get("/history")
def get_history(symbol: str, limit: int = 100):
    if not data_client: return []
    try:
        start_dt = datetime.datetime.now() - datetime.timedelta(days=limit*2)
        req = StockBarsRequest(symbol_or_symbols=symbol, timeframe=TimeFrame.Day, start=start_dt, limit=limit)
        bars = data_client.get_stock_bars(req)
        return [{"close": b.close, "timestamp": b.timestamp.isoformat()} for b in bars[symbol]]
    except: return []

@app.get("/logs")
async def get_logs():
    data = await db.get_recent_logs(limit=50)
    return {"logs": [f"[{l['timestamp']}] {l['level']}: {l['message']}" for l in data]}

@app.post("/trade")
def place_trade(trade: dict):
    # Manual Override
    if not trading_client: return {"status": "error"}
    try:
        req = MarketOrderRequest(
            symbol=trade.get("symbol"),
            qty=trade.get("qty"),
            side=OrderSide.BUY if trade.get("side") == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        res = trading_client.submit_order(req)
        return {"status": "filled", "id": str(res.id)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- PnL TRACKING ---
INITIAL_BALANCE_FILE = "initial_balance.txt"
DEFAULT_BALANCE = 100000.0

def get_initial_balance():
    if os.path.exists(INITIAL_BALANCE_FILE):
        try:
            with open(INITIAL_BALANCE_FILE, "r") as f:
                return float(f.read().strip())
        except: return DEFAULT_BALANCE
    return DEFAULT_BALANCE

def set_initial_balance_file(amount: float):
    with open(INITIAL_BALANCE_FILE, "w") as f:
        f.write(str(amount))

@app.get("/pnl")
def get_pnl():
    if not trading_client: return {"status": "waiting"}
    try:
        # 1. Fetch Current State
        acct = trading_client.get_account()
        current_equity = float(acct.equity)
        
        # 2. Fetch Initial State
        initial_balance = get_initial_balance()
        
        # 3. Calculate Unrealized (Open Positions)
        # Filter for US Equity to avoid Crypto noise if keys are shared
        positions = [p for p in trading_client.get_all_positions() if p.asset_class == 'us_equity']
        unrealized_pnl = sum(float(p.unrealized_pl) for p in positions)
        
        # 4. derived Metrics
        total_pnl = current_equity - initial_balance
        realized_pnl = total_pnl - unrealized_pnl
        
        return {
            "initial_balance": initial_balance,
            "current_equity": current_equity,
            "total_pnl": total_pnl,
            "unrealized_pnl": unrealized_pnl,
            "realized_pnl": realized_pnl,
            "pnl_pct": (total_pnl / initial_balance) * 100 if initial_balance > 0 else 0
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

class BalanceUpdate(BaseModel):
    amount: float

@app.post("/config/deposit")
def add_funds(data: BalanceUpdate):
    """Securely add funds to the Invested Capital (Cost Basis)"""
    current = get_initial_balance()
    new_bal = current + data.amount
    set_initial_balance_file(new_bal)
    return {"status": "deposited", "added": data.amount, "total_invested": new_bal}

@app.post("/config/reset_capital")
def reset_capital(data: BalanceUpdate):
    """Reset the baseline (e.g. for a fresh start)"""
    set_initial_balance_file(data.amount)
    return {"status": "reset", "total_invested": data.amount}
