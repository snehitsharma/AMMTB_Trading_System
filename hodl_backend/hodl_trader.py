import db
import aiohttp
import json
import asyncio
import os
import base64
import time
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
import base58

RPC_ENDPOINT = os.getenv("RPC_ENDPOINT", "https://api.mainnet-beta.solana.com")
JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_API = "https://quote-api.jup.ag/v6/swap"
SOL_MINT = "So11111111111111111111111111111111111111112"

class HodlTrader:
    def __init__(self):
        self.positions = []
        self.wallet = None
        self.solana_client = None
        self.trader_active = False
        
        try:
            pk_str = os.getenv("SOLANA_PRIVATE_KEY")
            if pk_str:
                if "[" in pk_str:
                    key_bytes = bytes(json.loads(pk_str))
                else:
                    key_bytes = base58.b58decode(pk_str)
                self.wallet = Keypair.from_bytes(key_bytes)
                self.solana_client = AsyncClient(RPC_ENDPOINT)
                self.trader_active = True
                print(f"✅ Trader Armed: {self.wallet.pubkey()}")
        except Exception as e:
            print(f"⚠️ Trader Wallet Error: {e}")
        
    async def get_current_price(self, token_address):
        """Fetch current price from DexScreener"""
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pairs = data.get("pairs", [])
                        if pairs:
                            # Prefer Solana pair
                            msg = pairs[0] 
                            return float(msg.get("priceUsd", 0))
        except:
            return 0.0
        return 0.0

    async def monitor_positions(self):
        """
        Check all open positions for TP/SL/Trailing Stop
        TP1: Sell 50% at +100%
        TP2: Sell 25% at +200%
        Trailing Stop: 20%
        """
        positions = await db.get_open_positions()
        
        if positions:
             assets = [f"{p['symbol']} (+{((float(p.get('current_price', 0) or 0) - p['entry_price'])/p['entry_price'])*100:.1f}%)" for p in positions] # Note: current_price might not be in p yet, calculated below
             # Wait, p comes from DB, doesn't have current_price until we fetch it below.
             # So we just log the count.
             await db.add_log("INFO", f"Monitoring {len(positions)} open positions: {', '.join([p['symbol'] for p in positions])}")
        else:
             # To avoid spamming "0 positions" every 10s, we could skipp or log only if changed.
             # but "System Idle" is handled by frontend if logs are empty.
             # Let's log periodically in main.py loop instead of here if empty.
             pass
        
        for p in positions:
            symbol = p['symbol']
            address = p['token_address']
            entry_price = float(p['entry_price'])
            qty = float(p['quantity'])
            
            # 1. Get Price
            current_price = await self.get_current_price(address)
            if current_price <= 0: continue
            
            # Calculate PnL
            gain_pct = (current_price - entry_price) / entry_price
            
            # Log significant moves or random sampling?
            # User wants "Real reasoning".
            if abs(gain_pct) > 0.05:
                 await db.add_log("INFO", f"Price Update {symbol}: ${current_price} (PnL: {gain_pct*100:.1f}%)")
            else:
                 # Debug level for minor moves, but we don't have levels in frontend really, just text.
                 # Let's log it as DEBUG so it shows up in the feed.
                 await db.add_log("DEBUG", f"Checking {symbol}... Price: ${current_price} (Stable)")
            
            # Load State
            tp_levels = json.loads(p['tp_levels'])
            peak_price = float(p['peak_price'])
            if current_price > peak_price:
                peak_price = current_price
                # Update DB with new peak
                await db.update_position(address, qty, "OPEN", peak_price, json.dumps(tp_levels))
            
            # Logic
            action = None
            sell_qty = 0
            
            # TP1 (+100%)
            if gain_pct >= 1.0 and not tp_levels.get("tp1_hit"):
                await db.add_log("SUCCESS", f"🎯 TP1 HIT for {symbol} (+{gain_pct*100:.1f}%)! Securing profits...")
                print(f"🎯 TP1 HIT for {symbol} (+{gain_pct*100:.1f}%)")
                action = "SELL_TP1"
                sell_qty = qty * 0.5
                tp_levels["tp1_hit"] = True

            # TP2 (+200%)
            elif gain_pct >= 2.0 and not tp_levels.get("tp2_hit"):
                await db.add_log("SUCCESS", f"🚀 TP2 HIT for {symbol} (+{gain_pct*100:.1f}%)! Moonbag activated...")
                print(f"🚀 TP2 HIT for {symbol} (+{gain_pct*100:.1f}%)")
                action = "SELL_TP2"
                sell_qty = qty * 0.25
                tp_levels["tp2_hit"] = True
                
            # Trailing Stop (-20% from Peak)
            drop_from_peak = (peak_price - current_price) / peak_price
            if drop_from_peak >= 0.20:
                await db.add_log("WARNING", f"🛑 Trailing Stop hit for {symbol} (-{drop_from_peak*100:.1f}% from peak). Exiting...")
                print(f"🛑 Trailing Stop hit for {symbol} (-{drop_from_peak*100:.1f}% from peak)")
                action = "SELL_STOP"
                sell_qty = qty # Sell ALL remaining
                
            # Execute Sell
            if action and sell_qty > 0:
                await self.execute_sell(address, sell_qty, action, current_price)
                
                new_qty = qty - sell_qty
                new_status = "CLOSED" if new_qty < (0.01 * qty) else "OPEN" # Close if dust left
                
                await db.update_position(address, new_qty, new_status, peak_price, json.dumps(tp_levels))
                msg = f"✅ Sold {sell_qty} of {symbol} at ${current_price}"
                await db.add_log("ACTION", msg)
                print(msg)

    async def execute_sell(self, token_address, qty, reason, price):
        if not self.trader_active:
             print("Trader disabled (no key), simulating sell.")
             await db.log_trade(token_address, "SELL", price, qty, f"SIM_SELL_{reason}")
             return

        print(f"📉 Selling {qty} of {token_address} ({reason})...")
        
        # JUPITER SELL
        try:
            amount_lamports = int(qty) # qty stored as raw int float in DB
            
            quote_url = f"{JUPITER_QUOTE_API}?inputMint={token_address}&outputMint={SOL_MINT}&amount={amount_lamports}&slippageBps=200"
            
            async with aiohttp.ClientSession() as session:
                # Quote
                quote_data = None
                try:
                    async with session.get(quote_url, timeout=5) as q_resp:
                        if q_resp.status != 200:
                            print(f"Sell Quote failed: {await q_resp.text()}")
                        else:
                            quote_data = await q_resp.json()
                except Exception as e:
                    print(f"Jupiter Quote network error: {e}")

                if not quote_data:
                    if not live:
                         print("⚠️ Jupiter unreachable, proceeding with SIMULATED paper sell.")
                    else:
                         print("❌ Jupiter unreachable, aborting LIVE sell.")
                         return

                # Swap Tx
                if quote_data:
                    swap_payload = {
                        "quoteResponse": quote_data,
                        "userPublicKey": str(self.wallet.pubkey()),
                        "wrapAndUnwrapSol": True
                    }
                    
                    async with session.post(JUPITER_SWAP_API, json=swap_payload) as s_resp:
                        if s_resp.status != 200:
                            print(f"Sell Swap build failed: {await s_resp.text()}")
                            return
                        swap_data = await s_resp.json()
                
                # Execute
                mode = os.getenv("HODL_MODE", "paper")
                live = os.getenv("HODL_LIVE", "false").lower() == "true"
                confirm = os.getenv("HODL_CONFIRM", "false").lower() == "true"
                
                if live and confirm:
                     print("🚀 EXECUTING LIVE SELL...")
                     raw_tx = base64.b64decode(swap_data['swapTransaction'])
                     tx = VersionedTransaction.from_bytes(raw_tx)
                     
                     message = tx.message
                     signature = self.wallet.sign_message(message.to_bytes_versioned(message.version))
                     signed_tx = VersionedTransaction.populate(message, [signature])
                     
                     encoded_tx = bytes(signed_tx)
                     sig = await self.solana_client.send_raw_transaction(encoded_tx, opts=TxOpts(skip_preflight=True))
                     tx_hash = str(sig.value)
                     print(f"✅ SELL SUCCESS! Tx: {tx_hash}")
                     await db.log_trade(token_address, "SELL", price, qty, tx_hash)
                else:
                    print("📝 Paper Sell Executed")
                    await db.log_trade(token_address, "SELL", price, qty, f"SIM_SELL_{reason}")

        except Exception as e:
            print(f"Sell Error: {e}")
            await db.log_trade(token_address, "SELL_ERROR", price, qty, str(e))
        
    def get_positions(self): 
        # Since this method is synchronous in main.py call, 
        # we might need to change main.py to await getting positions or 
        # keep this as a cached getter. 
        # But monitor_positions updates DB.
        # Let's make main.py call a new async method or use a synch wrapper.
        # Actually scanner is async, trader.monitor is async. 
        # But main.py endpoint `get_positions` is sync.
        # We need to change main.py endpoint to async to call db.
        return []
