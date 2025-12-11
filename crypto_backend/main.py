from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from alpaca.trading.client import TradingClient
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import os
from dotenv import load_dotenv
import datetime

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# CLIENTS
trading_client = None
data_client = None
STATUS = "BOOTING"

try:
    API_KEY = os.getenv("ALPACA_API_KEY")
    SECRET = os.getenv("ALPACA_SECRET_KEY")
    if API_KEY and SECRET:
        trading_client = TradingClient(API_KEY, SECRET, paper=True)
        data_client = CryptoHistoricalDataClient()
        STATUS = "ONLINE"
        print("✅ Crypto Agent: Alpaca Connected")
except Exception as e:
    print(f"❌ Crypto Agent Init Fail: {e}")
    STATUS = "ERROR"

# --- STANDARD ENDPOINTS ---

@app.get("/")
def root(): return {"status": "Crypto Agent Online", "mode": STATUS}

@app.get("/account/summary")
def get_account():
    if not trading_client: return {"equity": 0, "status": STATUS}
    try:
        acct = trading_client.get_account()
        return {"equity": float(acct.equity), "cash": float(acct.cash), "status": "ACTIVE"}
    except: return {"equity": 0, "status": "ERROR"}

@app.get("/positions")
def get_positions():
    if not trading_client: return []
    try:
        return [p.dict() for p in trading_client.get_all_positions() if p.asset_class == 'crypto']
    except: return []

@app.get("/quote")
def get_quote(symbol: str = "BTC/USD"):
    if not data_client: return {"price": 0}
    try:
        req = CryptoLatestQuoteRequest(symbol_or_symbols=symbol)
        res = data_client.get_crypto_latest_quote(req)
        return {"symbol": symbol, "price": res[symbol].ask_price}
    except: return {"price": 0}

@app.get("/history")
def get_history(symbol: str, limit: int = 100):
    if not data_client: return []
    try:
        start_dt = datetime.datetime.now() - datetime.timedelta(days=limit*2)
        req = CryptoBarsRequest(symbol_or_symbols=symbol, timeframe=TimeFrame.Day, start=start_dt, limit=limit)
        bars = data_client.get_crypto_bars(req)
        return [{"close": b.close, "timestamp": b.timestamp.isoformat()} for b in bars[symbol]]
    except: return []

@app.get("/signals")
def get_signals():
    # Placeholder
    return [{"asset": "BTC/USD", "price": 0, "action": "HOLD", "reason": "System Sync", "source": "CRYPTO_AGENT"}]

@app.post("/trade")
def place_trade(trade: dict):
    if not trading_client: return {"status": "error"}
    try:
        req = MarketOrderRequest(
            symbol=trade.get("symbol"),
            qty=trade.get("qty"),
            side=OrderSide.BUY if trade.get("side") == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )
        res = trading_client.submit_order(req)
        return {"status": "filled", "id": str(res.id)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
