from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import uuid
from datetime import datetime
from ledger import SQLiteLedger, Transaction

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ledger = SQLiteLedger()

from universe_engine import UniverseEngine
universe_engine = UniverseEngine()
universe_engine.generate_universe() # Initial Generation

class WithdrawRequest(BaseModel):
    amount: float
    market: str

class LogRequest(BaseModel):
    source: str
    event: str
    details: Dict[str, Any] = {}

@app.get("/")
def read_root():
    return {"status": "Orchestrator Active", "port": 8005}

@app.post("/api/v1/withdraw")
def withdraw_funds(request: WithdrawRequest):
    # Mock check: In a real system, we'd check balances with other agents
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
    action: str # "APPROVE" or "REJECT"

@app.patch("/api/v1/transactions/{transaction_id}")
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

@app.get("/api/v1/wallet/balance")
def get_wallet_balance():
    return {"balance": ledger.get_balance()}

@app.get("/api/v1/logs")
def get_logs():
    return {
        "logs": ledger.get_logs(),
        "transactions": ledger.get_transactions()
    }

@app.post("/api/v1/log_event")
def log_event(request: LogRequest):
    ledger.add_log(request.source, request.event, request.details)
    return {"status": "logged"}

@app.get("/api/v1/universe")
def get_universe():
    return universe_engine.get_universe()

@app.post("/api/v1/generate_universe")
def generate_universe():
    return universe_engine.generate_universe()

@app.post("/api/v1/shutdown")
def shutdown_system():
    """Emergency Stop: Kills all Python and Node processes"""
    import os
    import threading
    
    def kill():
        import time
        time.sleep(1)
        if os.name == 'nt': # Windows
            os.system("taskkill /F /IM python.exe")
            os.system("taskkill /F /IM uvicorn.exe")
            os.system("taskkill /F /IM node.exe")
        else: # Linux/Mac
            os.system("pkill -f python")
            os.system("pkill -f uvicorn")
            os.system("pkill -f node")
            
    # Run in background so request returns first
    threading.Thread(target=kill).start()
    
    return {"status": "SHUTTING_DOWN", "message": "System will terminate in 1 second."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
