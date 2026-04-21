# AMMTB Trading System 🚀

> **Autonomous Multi-Market Trading Bot** — A decentralized swarm of AI agents that autonomously trade US equities, crypto, and Solana memecoins 24/7.

---

## 📐 Architecture Overview

The AMMTB system is built on a **Decentralized Swarm** model. There is no single brain — each agent is fully autonomous with its own strategy logic, data pipeline, and execution layer. The Frontend aggregates signals from all agents for unified monitoring.

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Dashboard :5173                       │
│          (Polls all agents independently via REST API)          │
└────────────┬───────────────┬──────────────────┬────────────────┘
             │               │                  │
     ┌───────▼──────┐ ┌──────▼──────┐  ┌───────▼──────┐
     │  US Agent    │ │Crypto Agent │  │ HODL Agent   │
     │  :8001       │ │  :8002      │  │  :8006       │
     │  Alpaca SDK  │ │ Alpaca SDK  │  │ Solana/Jito  │
     └──────────────┘ └─────────────┘  └──────────────┘
             │               │                  │
     ┌───────▼───────────────▼──────────────────▼────────────────┐
     │                  Orchestrator :8005                        │
     │         (Global Ledger • Risk Logging • Banking)           │
     └────────────────────────────────────────────────────────────┘
```

### Agent Roster

| Agent | Port | Market | Strategy |
|---|---|---|---|
| 🇺🇸 **US Agent** | `8001` | US Equities (Alpaca) | Bio-Digital Dragnet — RSI/MACD/ATR + Confluence Scoring |
| 🪙 **Crypto Agent** | `8002` | BTC/ETH (Alpaca) | Trend Following + Volatility Breakout |
| 🇮🇳 **India Agent** | `8003` | NSE/BSE (Upstox) | Breakout Strategy *(Optional)* |
| 💎 **HODL Agent** | `8006` | Solana Memecoins | Sniper Logic — DexScreener + On-Chain Safety |
| 🛡️ **Orchestrator** | `8005` | — | Global Ledger, Risk Logging, Banking |
| 💻 **Frontend** | `5173` | — | React Dashboard (Vite) |

---

## 🧠 How It Works

### US Agent — "The Bio-Digital Dragnet"
The US Agent runs a continuous 6-phase autonomous loop every hour during market hours:

1. **Dragnet** — Aggregates a dynamic universe of 50–70+ tickers from FMP screener, Yahoo Finance most-actives, and daily gainers.
2. **The Sieve** — Filters every ticker with local RSI/MACD/ATR/Volume analysis. Only "BUY_CHECK" survivors advance.
3. **The Tribunal** — Each survivor is cross-verified with **Data Jockey** (financials), **Twelve Data** (macro), and **FMP** (fundamentals).
4. **The Verdict** — A [Confluence Score](#confluence-scoring) (0–100) is computed from technicals + macro + financials.
5. **The Leaderboard** — All `STRONG BUY` (score ≥ 80) signals are ranked by score.
6. **Olympic Execution** — Top 3 signals are executed as notional market orders with fractional share support.

Between full scans (every 60 min), the agent runs a **60-second exit heartbeat** to monitor stop-loss (−3%) and take-profit (+6%) on all open positions.

### Confluence Scoring

| Source | Points | Condition |
|---|---|---|
| Sieve Passed | +25 | RSI in range, Volume spike, Momentum up |
| Stable Financials | +50 | Data Jockey growth score positive |
| Macro Aligned | +25 | BTC price confirms risk-on sentiment |
| **Total** | **100** | `≥ 80 → STRONG BUY`, `≥ 40 → WATCH` |

### HODL Agent — "The Sniper"
The HODL Agent targets newly-launched Solana memecoins with a **Survivor Mode** strategy:

1. **Discovery** — Monitors `nursery.json` for new token launches captured via DexScreener WebSocket.
2. **Age Gate** — Token must be 5–20 minutes old (too young = hype only, too old = missed the move).
3. **Stats Gate** — Liquidity ≥ $10k AND 24h volume ≥ $10k.
4. **On-Chain Safety** — Verifies no active Mint Authority, no Freeze Authority, and top holder < 30% supply.
5. **Graduation** — Tokens passing all checks are queued for purchase via **Jupiter Swap + Jito Bundle** for reliable on-chain execution.

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Alpaca account (Paper or Live)
- API keys for FMP, Data Jockey, Twelve Data *(US Agent)*
- Solana wallet + Helius/QuikNode RPC *(HODL Agent)*

### 1. Configure Environment
Copy and fill in your keys:
```ini
# .env (root directory)

# Alpaca (US & Crypto Agents)
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_PAPER=True          # Set False for live trading

# US Agent Intelligence
FMP_API_KEY=your_key_here
DATA_JOCKEY_KEY=your_key_here
TWELVE_DATA_KEY=your_key_here

# HODL Agent (Solana)
SOLANA_WALLET_PRIVATE_KEY=your_base58_key
HELIUS_RPC_URL=https://mainnet.helius-rpc.com/?api-key=...

# Features
ENABLE_INDIA_AGENT=false
US_AGENT_AUTO_BUY=false    # Set True to enable autonomous buying
```

### 2. Launch Everything
```powershell
.\start_system.ps1
```
This launches all agents and opens the React dashboard at `http://localhost:5173`.

---

## 🛡️ Risk Management

All risk controls are **client-side, enforced by each agent independently**:

| Rule | Value | Description |
|---|---|---|
| Position Size | 30% of cash | Per-trade notional allocation |
| Max Positions | 3 concurrent | Olympic Execution picks top 3 only |
| Stop Loss | −3% unrealized | Soft bracket, checked every 60 seconds |
| Take Profit | +6% unrealized | Soft bracket, checked every 60 seconds |
| Wallet Guard | < $2.00 cash | Agent sleeps 1 hour if buying power is too low |

> **Note:** Soft brackets are client-side (checked in the exit heartbeat loop) to support fractional shares, which Alpaca does not support with native bracket orders.

---

## 🔌 API Reference

All agents expose a consistent REST API:

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Agent status and mode |
| `/health` | GET | Detailed health check (broker, scanner, mode) |
| `/account/summary` | GET | Equity, cash, buying power |
| `/positions` | GET | All open positions |
| `/signals` | GET | Latest scored signals / leaderboard |
| `/pnl` | GET | Total PnL vs initial capital |
| `/logs` | GET | Last 50 action logs |
| `/trade` | POST | Manual trade override |
| `/config/deposit` | POST | Add to invested capital baseline |

---

## 📂 Project Structure

```
AMMTB_Trading_System/
├── us_backend/          # US Equities Agent (FastAPI)
│   ├── main.py          # Dragnet loop + endpoints
│   ├── strategy.py      # RSI/MACD/ATR strategy engine
│   ├── analysis/        # Confluence scoring
│   └── clients/         # FMP, DataJockey, TwelveData, RateLimiter
├── crypto_backend/      # Crypto Agent (FastAPI)
├── india_backend/       # India Agent (FastAPI, optional)
├── hodl_backend/        # Solana HODL Agent (FastAPI)
│   ├── main.py          # Sniper loop + endpoints
│   ├── hodl_scanner.py  # On-chain safety checks
│   └── hodl_executor.py # Jupiter Swap + Jito execution
├── orchestrator/        # Central Ledger & Logger
├── frontend/            # React Dashboard (Vite)
├── .env                 # All API keys (never commit this)
├── start_system.ps1     # One-click launcher
└── reset_system.ps1     # Wipe DB + logs for fresh start
```

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `ECONNREFUSED` on dashboard | An agent crashed. Re-run `.\start_system.ps1` |
| `❌ KEY MISSING` in startup logs | Fill in the corresponding key in `.env` |
| US Agent not buying | Verify `US_AGENT_AUTO_BUY=true` in `.env` |
| HODL Agent RPC errors | Helius RPC may be rate-limiting — check your plan |
| Empty signals on dashboard | Market is closed or Alpaca data is delayed |

---

## 🚨 Disclaimer

This software is for **educational and experimental purposes only**. Automated trading involves significant financial risk. The authors are not liable for any financial losses. Always paper trade first. Never invest more than you can afford to lose.

---

## 📜 License

MIT License — see `LICENSE` for details.
