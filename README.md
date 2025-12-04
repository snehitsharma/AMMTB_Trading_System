# AMMTB Trading System - Owner's Manual 🚀

## 1. Architecture Overview
The AMMTB System is a modular, agent-driven trading platform built on a microservices architecture.

### The 6 Core Agents
| Agent | Port | Role |
|-------|------|------|
| **US Agent** | `8001` | Interfaces with Alpaca (Stocks). Handles market data & execution. |
| **Crypto Agent** | `8002` | Interfaces with Alpaca (Crypto). Handles BTC/ETH data & execution. |
| **India Agent** | `8003` | Interfaces with Upstox (NSE/BSE). *Currently Optional.* |
| **AI Brain** | `8004` | The Intelligence Layer. Runs strategies, manages portfolio, and executes trades. |
| **Orchestrator** | `8005` | The Central Bank & Logger. Manages the Ledger, Wallet, and System Logs. |
| **Frontend** | `3000` | React-based Dashboard for monitoring and control. |

---

## 2. Quick Start
To launch the entire system (all agents + frontend):

1. Open PowerShell in the root directory.
2. Run the startup script:
   ```powershell
   .\start_system.ps1
   ```
3. The dashboard will automatically open at `http://localhost:3000`.

---

## 3. Features Guide

### 🧠 AI Brain & Strategies
- **Location**: `/strategies` page.
- **Control**: Toggle strategies (e.g., "Technical Analysis", "Insider Momentum") on/off in real-time.
- **Logic**: The Brain scans the universe every 5 minutes and executes trades based on active strategies.

### 🛡️ Risk Management
- **Location**: `/risk` page.
- **Rules**:
    - **Position Sizing**: Fixed at **5%** of equity per trade.
    - **Max Exposure**: Hard limit of **25%** total invested capital (75% cash buffer).
    - **Kill Switch**: Automatically triggers if **Daily Drawdown > 3%**. Halts all buying.
    - **Bracket Orders**: Every trade has a **-5% Stop Loss** and **+10% Take Profit**.

### 🏦 Banking & Wallet
- **Location**: `/wallet` page.
- **Liquidity**: View your "Available Liquidity" (Free Cash).
- **Withdrawals**: 
    1. Request a withdrawal via API (or future UI).
    2. Go to the **Wallet Page**.
    3. Click **Approve** (Green Check) to release funds or **Reject** (Red X) to deny.
    4. The Master Ledger updates immediately.

---

## 4. Configuration
The system is configured via the `.env` file in the root directory.

### Key Settings
```ini
# API Keys
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here

# System Flags
ENABLE_INDIA_AGENT=false  # Set to true to enable Upstox
TRADING_ENABLED=true      # Set to false for "Paper Trading" mode (Simulated execution)
```

---

## 5. Troubleshooting

### Common Issues
- **`ECONNREFUSED` / Connection Error**:
    - One of the agents is not running.
    - Check the terminal windows. If one closed, restart it manually or run `.\start_system.ps1` again.
- **"Kill Switch Active"**:
    - You hit the 3% daily loss limit.
    - To reset manually (Admin only), restart the AI Engine.
- **Empty Charts**:
    - The market might be closed, or Alpaca data is delayed. Check your API keys.

---

## 6. Maintenance
To wipe the system (Database, Logs, Cache) and start fresh:
```powershell
.\reset_system.ps1
```
**WARNING**: This deletes all trade history and ledger records!
