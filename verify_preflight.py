
import os
import aiohttp
import asyncio
from dotenv import load_dotenv

async def verify_apis():
    print("🔍 Starting API Connectivity Check...")
    
    # 1. Alpaca (US Agent)
    # Check .env first 
    us_env_path = "d:/aamtb/AMMTB_Trading_System/us_backend/.env"
    if os.path.exists(us_env_path):
        load_dotenv(us_env_path)
        print(f"✅ US Agent .env found")
        if os.getenv("ALPACA_PAPER", "False").lower() == "true":
            print("✅ US Agent is in PAPER mode")
        else:
            print("⚠️ US Agent is in LIVE mode (or ALPACA_PAPER not set to true)")
    else:
        print("❌ US Agent .env MISSING")

    # 2. HODL Agent Env
    hodl_env_path = "d:/aamtb/AMMTB_Trading_System/hodl_backend/.env"
    if os.path.exists(hodl_env_path):
        load_dotenv(hodl_env_path) # Reloads on top, careful but fine for checking specifics if we parse manually
        # Better to parse manually to avoid collision
        with open(hodl_env_path, 'r') as f:
            content = f.read()
            if "HODL_LIVE=false" in content.lower() or "hodl_live=false" in content.lower():
                print("✅ HODL_LIVE is FALSE (Safe)")
            else:
                print("⚠️ HODL_LIVE might be TRUE or missing (Check manually)")
            
            if "HODL_CONFIRM=false" in content.lower() or "hodl_confirm=false" in content.lower():
                print("✅ HODL_CONFIRM is FALSE (Safe)")
            else:
                print("⚠️ HODL_CONFIRM might be TRUE")
    else:
        print("❌ HODL Agent .env MISSING")

    # 3. External APIs
    async with aiohttp.ClientSession() as session:
        # DEXSCREENER
        try:
            async with session.get("https://api.dexscreener.com/latest/dex/search?q=SOL") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "pairs" in data and isinstance(data["pairs"], list):
                        print("✅ DexScreener API: OK (Pairs found)")
                    else:
                        print("⚠️ DexScreener API: Unexpected Format")
                else:
                    print(f"❌ DexScreener API: Error {resp.status}")
        except Exception as e:
            print(f"❌ DexScreener Connection Failed: {e}")

        # RUGCHECK (Check a known token, e.g. USDC or a generic one)
        # USDC: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
        try:
            async with session.get("https://api.rugcheck.xyz/v1/tokens/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/report") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "score" in data:
                        print(f"✅ RugCheck API: OK (Score: {data['score']})")
                    else:
                        print("⚠️ RugCheck API: Unexpected Format (No score)")
                else:
                    print(f"❌ RugCheck API: Error {resp.status}")
        except Exception as e:
            print(f"❌ RugCheck Connection Failed: {e}")

        # JUPITER
        try:
            # Quote SOL -> USDC
            url = "https://quote-api.jup.ag/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=100000000&slippageBps=50"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "outAmount" in data:
                        print("✅ Jupiter Quote API: OK")
                    else:
                        print("⚠️ Jupiter API: Unexpected Format")
                else:
                    print(f"❌ Jupiter API: Error {resp.status}")
        except Exception as e:
            print(f"❌ Jupiter Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_apis())
