import sys
import os
import uuid
from fastapi import FastAPI, HTTPException
from typing import List
import random

# Add parent directory to sys.path to allow importing shared_libs
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared_libs.schemas import AccountSummary, Position, TradeRequest, OrderConfirmation
from upstox_client import UpstoxClient

# PyAlgoTrade Imports
from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma

app = FastAPI(title="India Agent (Upstox Mock)")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Wallet (INR)
mock_wallet = {
    "cash_balance": 100000.0, # ₹1,00,000
    "positions": []
}

# Initialize Upstox Client
upstox = UpstoxClient()

class BuyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, qty):
        super(BuyStrategy, self).__init__(feed, 100000) # Start with 100k cash
        self.__instrument = instrument
        self.__qty = qty
        self.__position = None

    def onBars(self, bars):
        if self.__position is None:
            self.__position = self.enterLong(self.__instrument, self.__qty, True)

@app.get("/api/v1/health")
def health_check():
    return {"broker": "Upstox", "status": "ok"}

@app.get("/api/v1/quote")
def get_quote(symbol: str = "NIFTY50"):
    # Mock NIFTY50 price
    price = 24000.0 + random.uniform(-100, 100)
    return {"symbol": symbol, "price": price, "currency": "INR"}

@app.get("/api/v1/account/summary", response_model=AccountSummary)
def get_account_summary():
    return AccountSummary(
        broker="Upstox (Mock)",
        cash_balance=mock_wallet["cash_balance"],
        unrealized_pl=0.0,
        total_equity=mock_wallet["cash_balance"]
    )

@app.post("/api/v1/trade", response_model=OrderConfirmation)
def place_trade(trade: TradeRequest):
    # Real Backtest Logic (Ported from US Agent)
    try:
        # Load Feed
        feed = yahoofeed.Feed()
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'NIFTY.csv')
        
        if not os.path.exists(data_path):
             raise HTTPException(status_code=500, detail="Data file not found")
             
        feed.addBarsFromCSV("NIFTY", data_path)

        # Run Strategy
        myStrategy = BuyStrategy(feed, "NIFTY", trade.qty)
        myStrategy.run()
        
        final_equity = myStrategy.getResult()
        
        # Update Mock Wallet
        global mock_wallet
        mock_wallet["cash_balance"] = final_equity
        
        # Also update Upstox Mock Client
        upstox.place_order("NIFTY", trade.qty, "BUY")
        
        order_id = str(uuid.uuid4())
        return OrderConfirmation(
            order_id=order_id, 
            status="filled", 
            message=f"Backtest complete. Final Equity: ₹{final_equity:.2f}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
