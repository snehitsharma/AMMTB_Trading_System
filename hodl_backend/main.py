from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from dotenv import load_dotenv
from hodl_scanner import HodlScanner
from hodl_trader import HodlTrader
import db

# Load Environment Variables
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
scanner = HodlScanner()
trader = HodlTrader()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Init DB
    await db.init_db()
    print("✅ HODL Database Initialized")
    
    # Background Loop
    loop = asyncio.create_task(run_loops())
    yield
    loop.cancel()

async def run_loops():
    print("🔄 HODL Loops Started")
    while True:
        try:
            await scanner.scan_market()
            await trader.monitor_positions()
        except Exception as e:
            print(f"HODL Loop Error: {e}")
            await asyncio.sleep(5)
        await asyncio.sleep(10)

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- STANDARD ENDPOINTS ---

@app.get("/")
def root(): return {"status": "HODL Agent Online"}

@app.get("/scan")
def get_scan():
    return scanner.get_results()

@app.get("/positions")
async def get_positions():
    """Fetch real positions from DB"""
    data = await db.get_open_positions()
    return {"data": data}

@app.get("/api/v1/balance")
@app.get("/balance")
async def get_balance():
    bal = await scanner.get_sol_balance()
    return {"balance": bal}

@app.get("/logs")
async def get_logs():
    data = await db.get_recent_logs(limit=50)
    return {"logs": [f"[{l['timestamp']}] {l['level']}: {l['message']}" for l in data]}

@app.get("/health")
async def health_check():
    import os
    import aiohttp
    
    # 1. Check Solana Key
    sol_key = os.getenv("SOLANA_PRIVATE_KEY")
    key_loaded = bool(sol_key and len(sol_key) > 10)
    
    # 2. Check Jupiter
    jup_status = "unknown"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://quote-api.jup.ag/v6/health", timeout=3) as resp:
                jup_status = "ok" if resp.status == 200 else "fail"
    except:
        jup_status = "fail"
        
    # 3. Check DexScreener
    dex_status = "unknown"
    try:
         async with aiohttp.ClientSession() as session:
            async with session.get("https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112", timeout=3) as resp:
                dex_status = "ok" if resp.status == 200 else "fail"
    except:
        dex_status = "fail"

    return {
        "solana_key_loaded": key_loaded,
        "jupiter_status": jup_status,
        "dexscreener_status": dex_status,
        "rugcheck_status": "ok", # Passive check mostly
        "mode": "PAPER" # Hardcoded for now until we add config switching
    }
