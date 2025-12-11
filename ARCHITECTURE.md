# AMMTB Swarm Architecture (v2.0)

## 1. Core Concept
The system has moved from a "Monolithic Brain" to a **Decentralized Swarm**. There is no central AI. Each market agent is autonomous, possessing its own logic, data, and execution capabilities.

## 2. The Agent Swarm
| Agent | Port | Role | Strategy Logic |
| :--- | :--- | :--- | :--- |
| **🇺🇸 US Agent** | `8001` | Stocks (AAPL, NVDA) | Local `strategy.py` (RSI/MACD/ATR) |
| **🪙 Crypto Agent** | `8002` | Coins (BTC, ETH) | Local `strategy.py` (Trend Following/Volatility) |
| **🇮🇳 India Agent** | `8003` | NSE (NIFTY) | Local `strategy.py` (Breakout/Mock) |
| **💎 HODL Agent** | `8006` | Memecoins (Solana) | Sniper Logic (DexScreener/RugCheck) |

## 3. Infrastructure
| Service | Port | Role |
| :--- | :--- | :--- |
| **🛡️ Orchestrator** | `8005` | Global Ledger, Risk Logging, Banking |
| **💻 Frontend** | `5173` | React Dashboard (Aggregates data from all agents) |

## 4. Data Flow
1. **Frontend** polls `8001`, `8002`, and `8006` independently via REST APIs.
2. **US Agent** scans its own universe (Dynamic Top 20) and executes its own trades.
3. **Crypto Agent** scans its own universe and executes its own trades.
4. **HODL Agent** scans for new tokens and executes snipes.
5. All agents send **Logs** to the **Orchestrator (8005)** for record-keeping only.

## 5. Deployment Guide
- **Local:** Run `start_system.ps1`. This script launches all agents and the frontend.
- **Cloud:** Deploy each folder (`us_backend`, `crypto_backend`, etc.) as a separate Docker container. This allows for independent scaling (e.g., scaling the US Agent for high-frequency trading without affecting the Crypto Agent).

## 6. Key Benefits
- **Fault Isolation:** If one agent crashes, others continue to operate.
- **Scalability:** Agents can be deployed on different servers closer to their respective exchanges.
- **Simplicity:** No complex inter-process communication for strategy decisions.
