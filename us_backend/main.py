from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import os
from dotenv import load_dotenv
import datetime

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET = os.getenv("ALPACA_SECRET_KEY")

trading_client = TradingClient(API_KEY, SECRET, paper=True)
data_client = StockHistoricalDataClient(API_KEY, SECRET)

@app.get("/account/summary")
@app.get("/api/v1/account/summary")
def get_account():
    try:
        acct = trading_client.get_account()
        return {"equity": float(acct.equity), "cash": float(acct.cash), "total_equity": float(acct.equity)}
    except:
        return {"equity": 0, "cash": 0, "total_equity": 0}

@app.get("/positions")
@app.get("/api/v1/positions")
def get_positions():
    try:
        positions = trading_client.get_all_positions()
        return [{
            "symbol": p.symbol, 
            "qty": float(p.qty), 
            "market_value": float(p.market_value),
            "avg_entry_price": float(p.avg_entry_price),
            "current_price": float(p.current_price),
            "unrealized_pl": float(p.unrealized_pl),
            "unrealized_plpc": float(p.unrealized_plpc)
        } for p in positions if p.asset_class == 'us_equity']
    except:
        return []

@app.get("/quote")
@app.get("/api/v1/quote")
def get_quote(symbol: str = "AAPL"):
    try:
        req = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        res = data_client.get_stock_latest_quote(req)
        return {"symbol": symbol, "price": res[symbol].ask_price}
    except:
        return {"symbol": symbol, "price": 0.0}

# --- CRITICAL FIX: HISTORY ENDPOINT ---
@app.get("/api/v1/history")
def get_history(symbol: str, limit: int = 100):
    try:
        # Alpaca requires start time for bars
        start_time = datetime.datetime.now() - datetime.timedelta(days=limit*2) 
        req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_time,
            limit=limit
        )
        bars = data_client.get_stock_bars(req)
        return [
            {"close": b.close, "open": b.open, "high": b.high, "low": b.low, "volume": b.volume, "timestamp": b.timestamp.isoformat()} 
            for b in bars[symbol]
        ]
    except Exception as e:
        print(f"History Error {symbol}: {e}")
        return [] # Return empty list on error to prevent crash
        
@app.post("/api/v1/trade")
def place_trade(trade: dict):
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, TakeProfitRequest, StopLossRequest
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
    try:
        side = OrderSide.BUY if trade["side"] == "buy" else OrderSide.SELL
        qty = float(trade["qty"])
        
        # Bracket Params
        tp = trade.get("take_profit")
        sl = trade.get("stop_loss")
        
        tp_req = TakeProfitRequest(limit_price=float(tp)) if tp else None
        sl_req = StopLossRequest(stop_price=float(sl)) if sl else None

        if trade.get("type") == "limit":
            req = LimitOrderRequest(
                symbol=trade["symbol"],
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY,
                limit_price=float(trade["limit_price"]),
                take_profit=tp_req,
                stop_loss=sl_req
            )
        else:
            req = MarketOrderRequest(
                symbol=trade["symbol"],
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY,
                take_profit=tp_req,
                stop_loss=sl_req
            )
            
        res = trading_client.submit_order(req)
        return {"status": "filled", "id": str(res.id)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
