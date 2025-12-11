import pandas as pd
import pandas_ta as ta

class StrategyEngine:
    def __init__(self):
        self.name = "Crypto Technical"

    def analyze_symbol(self, symbol: str, history: list, is_owned: bool, equity: float):
        if not history or len(history) < 50:
            return {"action": "WAIT", "reason": "Not Enough Data"}

        # Convert to DataFrame
        df = pd.DataFrame(history)
        cols = ['close', 'open', 'high', 'low', 'volume']
        for c in cols:
            df[c] = pd.to_numeric(df[c])

        # Calculate Indicators
        df.ta.rsi(length=14, append=True)
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        
        last = df.iloc[-1]
        price = last['close']
        rsi = last['RSI_14']
        ema20 = last['EMA_20']
        ema50 = last['EMA_50']

        # Logic (Crypto is more volatile, wider bands)
        if is_owned:
            if rsi > 80:
                return {"action": "SELL", "reason": f"Overbought (RSI {rsi:.1f})"}
            if price < ema50:
                return {"action": "SELL", "reason": "Trend Broken (< EMA50)"}
            return {"action": "HOLD", "reason": "HODLing"}
        else:
            if price > ema20 and ema20 > ema50 and rsi < 45:
                return {"action": "BUY", "reason": f"Dip Buy (RSI {rsi:.1f})"}
            
        return {"action": "WAIT", "reason": f"No Signal (RSI {rsi:.1f})"}
