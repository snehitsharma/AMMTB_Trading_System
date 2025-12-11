from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import uuid
from datetime import datetime
from ledger import SQLiteLedger, Transaction

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

ledger = SQLiteLedger()

class WithdrawRequest(BaseModel):
    amount: float
    market: str

class LogRequest(BaseModel):
    source: str
    event: str
    details: Any = {}

# --- STANDARD ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "Orchestrator Active"}

@app.post("/withdraw")
def withdraw_funds(request: WithdrawRequest):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        id=transaction_id,
        timestamp=datetime.now().isoformat(),
        type="WITHDRAWAL",
        amount=request.amount,
        market=request.market,
        status="PENDING_APPROVAL"
    )
    ledger.add_transaction(transaction)
    ledger.add_log("Orchestrator", "WITHDRAWAL_REQUEST", {"amount": request.amount, "market": request.market, "id": transaction_id})
    return {"status": "PENDING_APPROVAL", "transaction_id": transaction_id}

class TransactionUpdate(BaseModel):
    action: str

@app.patch("/transactions/{transaction_id}")
def update_transaction(transaction_id: str, update: TransactionUpdate):
    if update.action == "APPROVE":
        ledger.update_transaction_status(transaction_id, "APPROVED")
        ledger.add_log("ADMIN", "FUNDS_RELEASED", {"id": transaction_id, "status": "APPROVED"})
        return {"status": "APPROVED"}
    elif update.action == "REJECT":
        ledger.update_transaction_status(transaction_id, "REJECTED")
        ledger.add_log("ADMIN", "WITHDRAWAL_DENIED", {"id": transaction_id, "status": "REJECTED"})
        return {"status": "REJECTED"}
    else:
        raise HTTPException(status_code=400, detail="Invalid Action")

import httpx

@app.get("/wallet/balance")
async def get_wallet_balance():
    """Aggregate Real-Time Liquidity from Agents"""
    try:
        async with httpx.AsyncClient() as client:
            # 1. US Cash (Alpaca)
            us_res = await client.get("http://localhost:8001/account/summary", timeout=2.0)
            us_cash = us_res.json().get("cash", 0.0) if us_res.status_code == 200 else 0.0

            # 2. Crypto Balance (SOL)
            hodl_res = await client.get("http://localhost:8006/balance", timeout=2.0)
            sol_bal = hodl_res.json().get("balance", 0.0) if hodl_res.status_code == 200 else 0.0

            # 3. Live SOL Price (Jupiter)
            sol_price = 200.0 # Default fallback
            try:
                price_res = await client.get("https://api.jup.ag/price/v2?ids=So11111111111111111111111111111111111111112", timeout=2.0)
                if price_res.status_code == 200:
                    data = price_res.json()
                    sol_price = float(data['data']['So11111111111111111111111111111111111111112']['price'])
            except:
                pass

            total_liquidity = us_cash + (sol_bal * sol_price)
            return {"balance": total_liquidity, "breakdown": {"us_cash": us_cash, "sol_value": sol_bal * sol_price, "sol_price": sol_price}}

    except Exception as e:
        print(f"Aggregation Error: {e}")
        # Fallback to Ledger if Agents are offline
        return {"balance": ledger.get_balance(), "note": "Agents Offline, using Ledger"}

@app.get("/transactions")
def get_transactions():
    return {"transactions": ledger.get_transactions()}

@app.get("/logs")
def get_logs(limit: int = 50, offset: int = 0):
    return {
        "logs": ledger.get_logs(limit, offset),
        "transactions": ledger.get_transactions()
    }

@app.post("/log_event")
def log_event(request: LogRequest):
    ledger.add_log(request.source, request.event, request.details)
    return {"status": "logged"}
