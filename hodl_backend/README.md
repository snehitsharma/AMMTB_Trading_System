
# HODL Agent Backend

The **HODL Agent** is a specialized Memecoin Sniper and Position Manager for the Solana blockchain. It scans DexScreener for Gems, validates them via RugCheck, executes swaps via Jupiter, and manages positions using a "Moonbag" strategy on a persistent SQLite ledger.

## Features
- **Sniper**: Auto-detects low-risk, high-velocity pairs on Solana.
- **RugCheck**: Pre-trade security analysis (Liquidity, Mint Auth, Freeze Auth).
- **Execution**: Simulates trades by default (Paper Mode) or executes live via Jupiter (Live Mode).
- **Manager**: Auto-takes profits at 50% (TP1) and 100% (TP2), managing the rest with a trailing stop.
- **Ledger**: Persists all trades and audits to `hodl_ledger.db`.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**
   Copy `.env.example` to `.env` and fill in details:
   - `SOLANA_PRIVATE_KEY`: Your key (base58 or array). Required for Live Mode.
   - `HODL_MODE`: `paper` (Safe) or `live` (Real Money).
   - `HODL_LIVE`: Set to `true` to enable real swaps.
   - `HODL_CONFIRM`: Set to `true` to confirm auto-execution.

3. **Running the Agent**
   ```bash
   uvicorn main:app --port 8006 --reload
   ```

## API Endpoints
- `GET /scan`: Latest scan results.
- `GET /positions`: List active positions.
- `GET /balance`: Real SOL balance.
- `GET /health`: System status.
- `POST /admin/snipe`: Manually trigger snipe (Admin only).

## Testing
Run the test suite to verify DB persistence and safety logic.
```bash
pytest
```

## Safety Disclaimer
**LIVE MODE USES REAL FUNDS.**
Ensure you understand the risks. The default configuration is PAPER MODE. 
Never share your `.env` file or commit it to a repo.
