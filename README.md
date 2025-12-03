# AMMTB Trading System

Autonomous Multi-Market Trading System with 6 agents.

## Architecture

- **US Agent** (`us_backend`): PyAlgoTrade + FastAPI (Port 8001)
- **India Agent** (`india_backend`): Zerodha + FastAPI (Port 8002)
- **Crypto Agent** (`crypto_backend`): CCXT + FastAPI (Port 8003)
- **AI Agent** (`ai_engine`): PyTorch + FastAPI (Port 8004)
- **Orchestrator** (`orchestrator`): Gatekeeper (Not yet implemented)
- **Frontend** (`frontend`): React + Chakra UI (Port 5173)

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+

### Installation

1.  **Install Python Dependencies**:
    ```bash
    pip install fastapi uvicorn pydantic
    # Add other requirements as needed
    ```

2.  **Install Frontend Dependencies**:
    ```bash
    cd frontend
    npm install
    ```

### Running the System

1.  **Start US Agent**:
    ```bash
    python us_backend/main.py
    ```

2.  **Start India Agent**:
    ```bash
    python india_backend/main.py
    ```

3.  **Start Crypto Agent**:
    ```bash
    python crypto_backend/main.py
    ```

4.  **Start AI Agent**:
    ```bash
    python ai_engine/main.py
    ```

5.  **Start Frontend**:
    ```bash
    cd frontend
    npm run dev
    ```

## API Endpoints

All backends expose:
- `GET /api/v1/health`
- `GET /api/v1/account/summary`
- `GET /api/v1/positions`
- `POST /api/v1/trade`
- `POST /api/v1/dry_trade`
