import aiohttp
import asyncio
import time
import os
import json
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
import base58

import rug_checker
import db

# CONFIG
RPC_ENDPOINT = os.getenv("RPC_ENDPOINT", "https://api.mainnet-beta.solana.com")
JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_API = "https://quote-api.jup.ag/v6/swap"
SOL_MINT = "So11111111111111111111111111111111111111112"
IGNORED_SYMBOLS = ["SOL", "USDC", "USDT", "WSOL", "MSOL", "JITOSOL"]

class HodlScanner:
    def __init__(self):
        self.results = []
        self.is_running = False
        self.last_scan = 0
        self.sniper_active = False
        self.sol_price = 150.0 
        
        # Load Wallet
        try:
            pk_str = os.getenv("SOLANA_PRIVATE_KEY")
            if pk_str:
                if "[" in pk_str:
                    key_bytes = bytes(json.loads(pk_str))
                else:
                    key_bytes = base58.b58decode(pk_str)
                self.wallet = Keypair.from_bytes(key_bytes)
                self.solana_client = AsyncClient(RPC_ENDPOINT)
                self.sniper_active = True
                self.rug_checker = rug_checker.RugChecker()
                print(f"✅ Sniper Armed: {self.wallet.pubkey()}")

            else:
                self.sniper_active = False
                print("⚠️ Sniper Disabled (No Key)")
        except Exception as e:
            print(f"⚠️ Wallet Init Error: {e}")
            self.sniper_active = False

    async def get_sol_balance(self):
        if not self.sniper_active: return 0.0
        try:
            resp = await self.solana_client.get_balance(self.wallet.pubkey())
            return resp.value / 1000000000
        except Exception as e:
            print(f"Balance Error: {e}")
            return 0.0
            
    async def report_to_orchestrator(self, event_type, data):
        """Send logs/events to Orchestrator"""
        orch_url = os.getenv("ORCHESTRATOR_URL", "http://localhost:8005")
        try:
            payload = {
                "source": "HODL_AGENT",
                "event": event_type,
                "details": data
            }
            async with aiohttp.ClientSession() as session:
                await session.post(f"{orch_url}/api/v1/log_event", json=payload, timeout=2)
        except:
            # Fallback to local DB log
            await db.add_log(event_type, str(data))

    async def execute_snipe(self, token_address, symbol):
        """
        Full Snipe Logic: Safety Check -> Quote -> Execute -> Persist
        """
        if not self.sniper_active:
            print("Sniper disabled, skipping execute.")
            return

        print(f"🔫 Sniping {symbol} ({token_address}) ...")
        
        # 0. Rug Check
        is_safe = await self.rug_checker.check_token(token_address)
        if not is_safe:
            print(f"⛔ Rug Check Failed for {symbol}")
            await self.report_to_orchestrator("SNIPE_ABORTED", {"token": token_address, "reason": "Rug Check Failed"})
            return

        # 1. Get Quote (Safety Check First)
        amount_in_sol = float(os.getenv("SNIPE_AMOUNT_SOL", "0.05"))
        current_balance = await self.get_sol_balance()
        
        # User Question: "Will it charge $500?" -> NO. It uses fixed amount.
        # But we must ensure they have it.
        if current_balance < (amount_in_sol + 0.02):
             print(f"⚠️ Insufficient Funds for Snipe. Have: {current_balance:.4f}, Need: {amount_in_sol + 0.02}")
             await self.report_to_orchestrator("SNIPE_ABORTED", {"reason": "Insufficient Funds"})
             return

        amount_lamports = int(amount_in_sol * 1_000_000_000)
        
        quote_url = f"{JUPITER_QUOTE_API}?inputMint={SOL_MINT}&outputMint={token_address}&amount={amount_lamports}&slippageBps=200"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Quote with Retry
                quote_data = None
                for attempt in range(3):
                    try:
                        async with session.get(quote_url, timeout=5) as q_resp:
                            if q_resp.status == 200:
                                quote_data = await q_resp.json()
                                break
                            else:
                                print(f"⚠️ Quote Attempt {attempt+1} Failed: {q_resp.status}")
                    except Exception as e:
                        print(f"⚠️ Quote Connect Error ({attempt+1}): {e}")
                    await asyncio.sleep(1)
                
                if not quote_data:
                    print("❌ Final Quote Failure. Aborting.")
                    return
                
                # Swap Transaction
                swap_payload = {
                    "quoteResponse": quote_data,
                    "userPublicKey": str(self.wallet.pubkey()),
                    "wrapAndUnwrapSol": True
                }
                
                async with session.post(JUPITER_SWAP_API, json=swap_payload) as s_resp:
                    if s_resp.status != 200:
                        print(f"Swap build failed: {await s_resp.text()}")
                        return
                    swap_data = await s_resp.json()
                    
                # Sign & Send
                mode = os.getenv("HODL_MODE", "paper")
                live = os.getenv("HODL_LIVE", "false").lower() == "true"
                confirm = os.getenv("HODL_CONFIRM", "false").lower() == "true"
                
                if live and confirm:
                     print(f"🚀 EXECUTING LIVE TRADE for {symbol}...")
                     import base64
                     from solders.transaction import VersionedTransaction
                     from solana.rpc.types import TxOpts
                     
                     # Deserializing
                     raw_tx = base64.b64decode(swap_data['swapTransaction'])
                     tx = VersionedTransaction.from_bytes(raw_tx)
                     
                     # Signing
                     message = tx.message
                     signature = self.wallet.sign_message(message.to_bytes_versioned(message.version))
                     signed_tx = VersionedTransaction.populate(message, [signature])
                     
                     # Sending
                     encoded_tx = bytes(signed_tx)
                     sig = await self.solana_client.send_raw_transaction(encoded_tx, opts=TxOpts(skip_preflight=True))
                     tx_hash = str(sig.value)
                     print(f"✅ Transaction Sent! Signature: {tx_hash}")

                else:
                    print(f"📝 Paper Trading Snipe: {symbol}")
                    tx_hash = f"SIM_{int(time.time())}"

                # SAVE TO DB
                out_amount = float(quote_data.get("outAmount"))
                buy_price = amount_in_sol / (out_amount / 10**6) # rough guess 
                
                # Log Trade
                await db.log_trade(token_address, "BUY", buy_price, out_amount, tx_hash)
                
                # Save Position
                await db.save_position(token_address, symbol, buy_price, out_amount, sl_price=buy_price*0.8)
                
                print(f"✅ SNIPE COMPLETE for {symbol}")
                
                await self.report_to_orchestrator("SNIPE_EXECUTED", {
                    "token": token_address, 
                    "symbol": symbol,
                    "mode": "LIVE" if live else "PAPER",
                    "tx": tx_hash,
                    "qty": out_amount
                })
                
        except Exception as e:
            print(f"Snipe Execution Error: {e}")
            await self.report_to_orchestrator("SNIPE_ERROR", {"error": str(e)})

    async def scan_market(self):
        if self.is_running: return
        self.is_running = True
        
        try:
            await db.add_log("INFO", "Scanning DexScreener for new Solana pairs...")
            url = "https://api.dexscreener.com/latest/dex/search?q=SOL"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pairs = data.get("pairs", [])
                        
                        clean_list = []
                        for p in pairs[:40]: 
                            if p.get("chainId") != "solana": continue
                            base_sym = p.get("baseToken", {}).get("symbol", "").upper()
                            if base_sym in IGNORED_SYMBOLS: continue
                            
                            liq = float(p.get("liquidity", {}).get("usd", 0))
                            vol = float(p.get("volume", {}).get("h24", 0))
                            created = p.get("pairCreatedAt", time.time()*1000)
                            if created is None: created = time.time()*1000
                            age_hours = (time.time() - (created/1000)) / 3600
                            
                            risk = "HIGH"
                            if liq > 50000 and vol > 200000 and age_hours > 0.5: risk = "LOW"
                            elif liq > 20000: risk = "MED"
                            
                            clean_list.append({
                                "token": f"{base_sym}/{p.get('quoteToken', {}).get('symbol', '')}",
                                "address": p.get("baseToken", {}).get("address", ""),
                                "age": f"{age_hours:.1f}h",
                                "liq": liq,
                                "vol": vol,
                                "risk": risk,
                                "url": p.get("url", "#"),
                                "symbol": base_sym
                            })
                            if len(clean_list) >= 20: break
                        
                        self.results = clean_list
                        self.last_scan = time.time()
                        
                        await db.add_log("INFO", f"Scan Complete. Found {len(clean_list)} pairs. Analysing for opportunities...")
                        
                        # Auto-Snipe Logic
                        # If finding a LOW risk token we don't own -> Snipe
                        open_positions = await db.get_open_positions()
                        MAX_OPEN_SLOTS = int(os.getenv("MAX_OPEN_SLOTS", 5))
                        
                        if len(open_positions) >= MAX_OPEN_SLOTS:
                            await db.add_log("WARNING", f"Max Slots Reached ({len(open_positions)}/{MAX_OPEN_SLOTS}). Skipping Snipe.")
                            return

                        MAX_LOSS = float(os.getenv("MAX_DAILY_LOSS", 1.0))
                        daily_pnl = await db.get_daily_pnl()
                        if daily_pnl < -MAX_LOSS:
                             await db.add_log("CRITICAL", f"Daily Loss Limit Hit ({daily_pnl:.4f} < -{MAX_LOSS}). Sniping PAUSED.")
                             return

                        open_addresses = [p['token_address'] for p in open_positions]
                        
                        any_snipe = False
                        for token in clean_list:
                            if token['token'] in ["SOL/USDC", "SOL/USDT"]: continue 

                            if token['risk'] == 'LOW':
                                if token['address'] not in open_addresses:
                                    await db.add_log("ACTION", f"Found LOW RISK candidate {token['symbol']} (Liq: ${token['liq']:.0f}). Initiating Snipe...")
                                    await self.execute_snipe(token['address'], token['symbol'])
                                    any_snipe = True
                                    break # One per cycle
                                else:
                                     # Already own, just log thought
                                     pass
                            elif token['risk'] == 'MED':
                                await db.add_log("THOUGHT", f"Watching {token['symbol']} (Medium Risk). Waiting for volume spike...")
                        
                        if not any_snipe and len(clean_list) > 0:
                            top = clean_list[0]
                            await db.add_log("INFO", f"Top Candidate: {top['symbol']} (Risk: {top['risk']}). No action taken.")
                        
                    else:
                        await db.add_log("ERROR", f"DexScreener API Error: {resp.status}")
                        print(f"DexScreener API Error: {resp.status}")

        except Exception as e:
            await db.add_log("ERROR", f"Scan Failed: {e}")
            print(f"Scan Failed: {e}")
            await self.report_to_orchestrator("SCAN_ERROR", {"error": str(e)})
        finally:
            self.is_running = False
            
    def get_results(self):
        return {
            "timestamp": self.last_scan,
            "tokens": self.results
        }
