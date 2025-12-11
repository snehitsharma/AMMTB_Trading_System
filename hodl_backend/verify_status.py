
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

async def verify():
    print("--- START VERIFICATION ---")
    
    # 1. Check .env loading
    load_dotenv()
    print(f".env loaded? {os.path.exists('.env')}")
    
    # 2. Check Solana Key
    sol_key = os.getenv("SOLANA_PRIVATE_KEY")
    if sol_key:
        print(f"SOLANA_PRIVATE_KEY found. Length: {len(sol_key)}")
        if len(sol_key) > 10:
            print("✅ Solana Key format looks plausible (length > 10).")
        else:
            print("❌ Solana Key too short.")
    else:
        print("❌ SOLANA_PRIVATE_KEY NOT FOUND in env.")
        
    # 3. Check Jupiter API
    print("Testing Jupiter API...")
    url = "https://quote-api.jup.ag/v6/health"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                print(f"Status Code: {resp.status}")
                if resp.status == 200:
                    text = await resp.text()
                    print(f"Response: {text}")
                    print("✅ Jupiter API is reachable.")
                else:
                    print(f"❌ Jupiter API returned non-200 status.")
    except Exception as e:
        print(f"❌ Jupiter API connection failed: {e}")

    # 4. Check Solana RPC
    print("Testing Solana RPC...")
    rpc_url = os.getenv("RPC_ENDPOINT", "https://api.mainnet-beta.solana.com")
    try:
         async with aiohttp.ClientSession() as session:
            payload = {"jsonrpc": "2.0", "id": 1, "method": "getHealth"}
            async with session.post(rpc_url, json=payload, timeout=5) as resp:
                print(f"RPC Status: {resp.status}")
                if resp.status == 200:
                    print("✅ Solana RPC is reachable.")
                else:
                    print("❌ Solana RPC returned non-200.")
    except Exception as e:
        print(f"❌ Solana RPC connection failed: {e}")

    # 5. Attempting to fix .env if key is missing
    if not sol_key:
        print("🔧 Attempting to fix .env with new key...")
        try:
            from solders.keypair import Keypair
            new_key = Keypair()
            new_key_bytes = list(bytes(new_key))
            print(f"Generated new key: {new_key.pubkey()}")
            
            # Read .env
            with open(".env", "r") as f:
                lines = f.readlines()
            
            new_lines = []
            wrote_key = False
            for line in lines:
                if line.startswith("SOLANA_PRIVATE_KEY="):
                    new_lines.append(f"SOLANA_PRIVATE_KEY={new_key_bytes}\n")
                    wrote_key = True
                else:
                    new_lines.append(line)
            
            if not wrote_key:
                new_lines.append(f"\nSOLANA_PRIVATE_KEY={new_key_bytes}\n")
                
            with open(".env", "w") as f:
                f.writelines(new_lines)
            print("✅ .env updated with valid key.")
        except Exception as e:
            print(f"Failed to generate/save key: {e}")

    print("--- END VERIFICATION ---")

if __name__ == "__main__":
    asyncio.run(verify())
