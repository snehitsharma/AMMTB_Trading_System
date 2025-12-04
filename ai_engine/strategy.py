import pandas as pd
import pandas_ta as ta
import numpy as np

from risk_engine import RiskEngine
from sentiment_engine import SentimentEngine

class TechnicalStrategy:
    def __init__(self):
        self.name = "Technical Trend"
        self.risk_engine = RiskEngine()
        self.sentiment_engine = SentimentEngine()

    def calculate_indicators(self, df: pd.DataFrame):
        """
        Calculate Technical Indicators:
        - EMA (20, 50) for Trend
        - RSI (14) for Momentum
        - MACD (12, 26, 9) for Momentum
        - ATR (14) for Volatility
        """
        # Ensure we have enough data
        if len(df) < 50:
            return df

        # Trend
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)

        # Momentum
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)

        # Volatility
        df.ta.atr(length=14, append=True)

        return df

    def analyze(self, symbol: str, history: list, current_position: bool, equity: float, settings=None):
        """
        Analyze a single symbol using Technical Analysis + Risk + Sentiment
        """
        if not history or len(history) < 50:
            return {"asset": symbol, "price": 0, "action": "WAIT", "reason": "Insufficient Data"}

        # Use default settings if none provided (for safety)
        if settings is None:
            from settings import system_settings
            settings = system_settings

        df = pd.DataFrame(history)
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        
        # 1. Technical Indicators
        df = self.calculate_indicators(df)
        
        # Get latest values
        last = df.iloc[-1]
        price = last['close']
        
        # Indicators
        ema20 = last['EMA_20']
        ema50 = last['EMA_50']
        rsi = last['RSI_14']
        macd = last['MACD_12_26_9']
        signal = last['MACDs_12_26_9']
        atr = last['ATRr_14']
        
        # Check for NaN
        if np.isnan(ema50) or np.isnan(atr):
             return {"asset": symbol, "price": price, "action": "WAIT", "reason": "Indicators warming up"}

        # 2. Strategy Logic
        is_uptrend = price > ema20 > ema50
        is_momentum = rsi < settings.rsi_buy_threshold and macd > signal # Dynamic RSI Buy
        
        action = "WAIT"
        reason = "Scanning..."
        
        # BUY LOGIC
        if is_uptrend and is_momentum:
            if current_position:
                action = "HOLD"
                reason = "Buy Signal (Already Owned)"
            else:
                action = "BUY"
                
                # Risk Management (EVT)
                risk_scalar = 1.0
                if settings.enable_risk_engine:
                    risk_scalar = self.risk_engine.calculate_risk_scalar(history)
                
                # Sentiment Analysis
                sentiment_data = {"score": 0, "insider": "NEUTRAL", "summary": ""}
                if settings.enable_sentiment and "/" not in symbol:
                     sentiment_data = self.sentiment_engine.get_finviz_data(symbol)
                
                news_score = sentiment_data.get("score", 0)
                insider_status = sentiment_data.get("insider", "NEUTRAL")
                
                reason = f"Trend UP & Dip (RSI {rsi:.1f})"
                
                # Adjust for Risk
                if risk_scalar < 1.0:
                    reason += f" | Risk Reduced {int((1-risk_scalar)*100)}% (EVT)"
                
                # Adjust for Sentiment
                if news_score > 0.2:
                    reason += f" | News Positive ({news_score:.2f})"
                elif news_score < -0.2:
                    reason += f" | News Negative ({news_score:.2f})"
                    risk_scalar *= 0.5 # Reduce size on bad news
                    
                if insider_status == "INSIDER_BUY":
                    reason += " | Insider Buying"
                    if news_score > 0.2:
                        reason += " (High Confidence)"
                elif insider_status == "INSIDER_SELL":
                    reason += " | Insider Selling"
                    risk_scalar *= 0.8 # Reduce size on insider selling
                
                # Position Sizing
                risk_per_trade = equity * settings.risk_per_trade # Dynamic Risk %
                stop_loss = price - (settings.stop_loss_atr_multiplier * atr) # Dynamic Stop Loss
                take_profit = price + (settings.take_profit_atr_multiplier * atr) # Dynamic Take Profit
                risk_per_share = price - stop_loss
                
                if risk_per_share > 0:
                    quantity = (risk_per_trade / risk_per_share) * risk_scalar
                else:
                    quantity = 0
                
                return {
                    "asset": symbol,
                    "price": price,
                    "action": "BUY",
                    "quantity": int(quantity),
                    "reason": reason,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "indicators": {"rsi": rsi, "macd": macd, "atr": atr} # Return indicators for frontend
                }

        # SELL LOGIC
        elif current_position:
            if rsi > settings.rsi_sell_threshold: # Dynamic RSI Sell
                action = "SELL"
                reason = f"Overbought (RSI {rsi:.1f})"
            elif price < ema50:
                action = "SELL"
                reason = "Trend Broken (Below EMA50)"
        
        return {
            "asset": symbol,
            "price": price,
            "action": action,
            "reason": reason,
            "indicators": {"rsi": rsi, "macd": macd, "atr": atr}
        }
