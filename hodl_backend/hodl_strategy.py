import aiohttp
import asyncio
import os
import time

class HodlV3Strategy:
    def __init__(self, rug_checker, wallet_manager=None):
        self.rug_checker = rug_checker
        self.wallet_manager = wallet_manager # For Jito execution potentially
        
        # Raydium Authority & Burn Addresses
        self.IGNORED_HOLDERS = [
            "5Q544fKrFoe6tsTRv468v2YgX9Zl8eR5yJ3T7y1", # Raydium Authority (Example) - Verify correct one
            "5Q544fKrFoe6tsTRv468v2YgX9Zl8eR5y5z5z5z5", # Another variant
            "11111111111111111111111111111111", # System
            "Dead111111111111111111111111111111111111111", # Dead
        ]

    async def check_token_safety(self, token_data):
        """
        A. THE "SAFE SNIPE" FILTER (Strict Entry)
        """
        symbol = token_data.get('symbol', 'UNKNOWN')
        print(f"🕵️ Analyzing candidate: {symbol}...")

        # 1. Age >= 30 minutes
        # token_data['age'] might be a string "0.5h" or float. Let's handle both.
        age_hours = 0.0
        try:
            if isinstance(token_data.get('age'), str):
                age_hours = float(token_data['age'].replace('h', ''))
            else:
                age_hours = float(token_data.get('age', 0))
        except:
            age_hours = 0.0
            
        if age_hours < 0.5:
            print(f"❌ Age too young: {age_hours:.2f}h < 0.5h")
            return False

        # 2. Liquidity >= $50,000
        liq = float(token_data.get('liq', 0))
        if liq < 50000:
            print(f"❌ Liquidity too low: ${liq:.0f} < $50k")
            return False

        # 3. Volume (1h) >= 50% of Liquidity
        # token_data['vol'] is 24h volume. We need 1h volume. 
        # If we only have 24h, we might need to approximate or fetch more detail.
        # Assuming token_data comes from DexScreener search which gives 24h volume.
        # We really need to fetch specific token data to get 1h volume.
        # Let's assume we fetch details inside here if needed or pass better data.
        # For now, let's use the provided vol if it's 24h, but the requirement is 1h.
        # We will fetch detailed pair data to get 1h volume.
        
        pair_address = token_data.get('token_address') or token_data.get('address')
        detailed_stats = await self.fetch_pair_stats(pair_address)
        
        vol_1h = detailed_stats.get('volume', {}).get('h1', 0)
        
        if vol_1h < (liq * 0.5):
             print(f"❌ Volume (1h) too low: ${vol_1h:.0f} < 50% of Liq (${liq:.0f})")
             return False

        # 4. RugCheck
        # mint_authority: NULL, freeze_authority: NULL, top_holders < 30%
        # This is handled in self.rug_checker.check_token_strict
        is_safe = await self.rug_checker.check_token_strict(token_data.get('address'))
        if not is_safe:
            print(f"❌ RugCheck Failed for {symbol}")
            return False

        print(f"✅ {symbol} Passed Safety Checks! (Age: {age_hours:.1f}h, Liq: ${liq:.0f}, Vol1h: ${vol_1h:.0f})")
        return True

    async def fetch_pair_stats(self, pair_address):
        if not pair_address: return {}
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pair = data.get('pair', {})
                        if not pair:
                            # Try pairs list
                            pairs = data.get('pairs', [])
                            if pairs: pair = pairs[0]
                        return pair
        except Exception as e:
            print(f"Error fetching pair stats: {e}")
        return {}

    async def check_momentum_signal(self, token_address):
        """
        B. THE "MOMENTUM" TRIGGER (Buy Signal)
        """
        # Fetch OHLCV for 5m candles
        # Using GeckoTerminal or similar 
        # https://api.geckoterminal.com/api/v2/networks/solana/pools/{pool_address}/ohlcv/minute?aggregate=5
        
        print(f"📊 Checking Momentum for {token_address}...")
        candles = await self.fetch_candles(token_address)
        
        if len(candles) < 55: # Need at least 50 for EMA50
            print("❌ Not enough candle data.")
            return False
            
        # Candles structure: [[time, open, high, low, close, vol], ...]
        # Sort by time just in case
        candles.sort(key=lambda x: x[0])
        
        closes = [float(c[4]) for c in candles]
        volumes = [float(c[5]) for c in candles]
        
        current_price = closes[-1]
        current_vol = volumes[-1]
        prev_vol = volumes[-2]
        
        # Calculate EMA 20
        ema_20 = self.calculate_ema(closes, 20)
        # Calculate EMA 50
        ema_50 = self.calculate_ema(closes, 50)
        
        if not ema_20 or not ema_50:
            return False
            
        latest_ema_20 = ema_20[-1]
        latest_ema_50 = ema_50[-1]
        
        print(f"   Price: {current_price:.6f} | EMA20: {latest_ema_20:.6f} | EMA50: {latest_ema_50:.6f}")
        
        # BUY CONDITION:
        # 1. Current Price > EMA_20
        cond1 = current_price > latest_ema_20
        
        # 2. EMA_20 > EMA_50 (Uptrend)
        cond2 = latest_ema_20 > latest_ema_50
        
        # 3. Volume of current candle > Volume of previous candle
        cond3 = current_vol > prev_vol
        
        if cond1 and cond2 and cond3:
            print("🚀 MOMENTUM SIGNAL CONFIRMED!")
            return True
        else:
            reasons = []
            if not cond1: reasons.append("Price <= EMA20")
            if not cond2: reasons.append("Not Uptrend (EMA20<=EMA50)")
            if not cond3: reasons.append("No Volume Spike")
            print(f"❌ Momentum Failed: {', '.join(reasons)}")
            return False

    async def fetch_candles(self, pool_address):
        # We need the POOL address, not the TOKEN address for GeckoTerminal usually.
        # But DexScreener often gives us the Pair Address (Pool Address).
        # Assuming token_address passed here IS the Pair/Pool address.
        
        url = f"https://api.geckoterminal.com/api/v2/networks/solana/pools/{pool_address}/ohlcv/minute?aggregate=5&limit=100"
        try:
             async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Gecko structure: data['data']['attributes']['ohlcv_list']
                        return data.get('data', {}).get('attributes', {}).get('ohlcv_list', [])
        except Exception as e:
            print(f"Candle fetch error: {e}")
        return []

    def calculate_ema(self, data, window):
        if len(data) < window: return None
        alpha = 2 / (window + 1)
        ema = [data[0]] # Start with SMA ideally, but for simple approximation logic
        # Actually standard is SMA first
        sma_first = sum(data[:window]) / window
        ema_values = [sma_first] * window # Pad start
        
        current_ema = sma_first
        for price in data[window:]:
            current_ema = (price * alpha) + (current_ema * (1 - alpha))
            ema_values.append(current_ema)
            
        return ema_values
