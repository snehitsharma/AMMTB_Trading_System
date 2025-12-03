import uvicorn
from fastapi import FastAPI
import requests
import pandas as pd

app = FastAPI(title="AI Agent (Brain)")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent URLs
US_AGENT_URL = "http://localhost:8001/api/v1"
CRYPTO_AGENT_URL = "http://localhost:8002/api/v1"
INDIA_AGENT_URL = "http://localhost:8003/api/v1"
ORCHESTRATOR_URL = "http://localhost:8005/api/v1"

last_logged_signal = None

@app.get("/api/v1/signals")
@app.get("/signals")
def get_signals():
    try:
        # 1. Fetch Data
        # For regime detection, we primarily need BTC price
        crypto_quote = requests.get(f"{CRYPTO_AGENT_URL}/quote").json()
        btc_price = crypto_quote.get("price", 0.0)
        
        # 2. Determine Regime
        regime = "NEUTRAL"
        signal = "HOLD"
        confidence = 0.5
        
        if btc_price > 90000:
            regime = "RISK_ON"
            signal = "BUY AAPL (Tech) & BTC"
            confidence = 0.9
        elif btc_price < 80000:
            regime = "RISK_OFF"
            signal = "BUY NIFTY (Defensive)"
            confidence = 0.8
            
        # 3. Log to Orchestrator if signal changed
        global last_logged_signal
        if signal != last_logged_signal:
            try:
                requests.post(f"{ORCHESTRATOR_URL}/log_event", json={
                    "source": "AI_AGENT",
                    "event": "SIGNAL_UPDATE",
                    "details": {
                        "regime": regime,
                        "signal": signal,
                        "reason": f"BTC Price: {btc_price}"
                    }
                }, timeout=1)
                last_logged_signal = signal
            except Exception as e:
                print(f"Failed to log to orchestrator: {e}")

        # 4. Construct Response
        return {
            "regime": regime,
            "signal": signal,
            "confidence": confidence,
            "market_data": {
                "btc_price": btc_price
            }
        }
        
    except Exception as e:
        return {
            "regime": "ERROR",
            "signal": "WAIT",
            "confidence": 0.0,
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
