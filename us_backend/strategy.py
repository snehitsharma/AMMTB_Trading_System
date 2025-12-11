import pandas as pd
import pandas_ta as ta

class StrategyEngine:
    def __init__(self):
        self.name = "Standard Technical"

    def analyze_symbol(self, symbol: str, history: list, is_owned: bool, equity: float, buying_power: float = 999999):
        if not history or len(history) < 50:
            return {"action": "WAIT", "reason": "Not Enough Data", "tech_data": {}}

        # Convert to DataFrame
        df = pd.DataFrame(history)
        cols = ['close', 'open', 'high', 'low', 'volume']
        for c in cols:
            df[c] = pd.to_numeric(df[c])

        # Calculate Indicators (AGD Standard)
        df.ta.rsi(length=14, append=True)
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.ema(length=200, append=True)
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        price = last['close']
        rsi = last.get('RSI_14', 50)
        ema20 = last.get('EMA_20', 0)
        ema50 = last.get('EMA_50', 0)
        vol_avg = df['volume'].mean()
        
        # AGD Technical Flags
        # Rejection Criteria: Discard any stock immediately if:
        # RSI > 80 (Overextended)
        # Price < EMA20 (Downtrend)
        # Relative Volume < 1.2x (No momentum)
        
        is_overextended = rsi > 80
        is_downtrend = price < ema20
        rel_vol = last['volume'] / vol_avg if vol_avg > 0 else 0
        # Relaxed for IEX Data (Request: Change 1.2 -> 0.1)
        has_momentum = rel_vol >= 0.1

        tech_data = {
            "rsi_div": False, 
            "golden_cross": (prev['EMA_20'] < prev['EMA_50']) and (ema20 > ema50),
            "vol_spike": rel_vol > 2.0, # Used for scoring (+15pts)
            "price_above_ema20": price > ema20,
            "rsi": rsi,
            "rel_vol": rel_vol
        }

        # Logic
        if is_owned:
            # LIQUIDITY CRISIS MODE
            if buying_power < (equity * 0.05):
               if price < ema20: return {"action": "SELL", "reason": "Liquidity Crunch (Price < EMA20)", "tech_data": tech_data}
            
            # Standard Exit
            if rsi > 70: return {"action": "SELL", "reason": f"Overbought (RSI {rsi:.1f})", "tech_data": tech_data}
            if price < ema50: return {"action": "SELL", "reason": "Trend Broken (< EMA50)", "tech_data": tech_data}
            
            return {"action": "HOLD", "reason": "Trend Healthy", "tech_data": tech_data}
        else:
            # Entry Logic (The Sieve)
            if is_overextended:
                return {"action": "WAIT", "reason": f"Sieve Fail: Overextended (RSI {rsi:.1f} > 80)", "tech_data": tech_data}
            
            if is_downtrend:
                 return {"action": "WAIT", "reason": f"Sieve Fail: Downtrend ({price:.2f} < EMA20 {ema20:.2f})", "tech_data": tech_data}
            
            if not has_momentum:
                 return {"action": "WAIT", "reason": f"Sieve Fail: Low Vol ({rel_vol:.2f}x < 0.1x)", "tech_data": tech_data}

            # If passed all Sieve filters:
            return {"action": "BUY_CHECK", "reason": "Sieve Passed", "tech_data": tech_data}
