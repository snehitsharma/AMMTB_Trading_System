import pandas as pd
import pandas_ta as ta
from data_ingestion import InsiderDataIngestor

class InsiderMomentumStrategy:
    def __init__(self, insider_ingestor: InsiderDataIngestor):
        self.name = "Insider Momentum"
        self.ingestor = insider_ingestor

    def analyze(self, symbol, history, is_owned, equity, settings):
        """
        Logic:
        1. High Insider Buying (> $250k in last 7 days)
        2. Uptrend (Price > SMA 20)
        """
        df = pd.DataFrame(history)
        df['close'] = df['close'].astype(float)
        
        # 1. Calculate SMA 20
        df.ta.sma(length=20, append=True)
        current_price = df.iloc[-1]['close']
        sma20 = df.iloc[-1]['SMA_20']

        # 2. Check Insider Data
        # We use the ingestor to query the local DB
        recent_activity = self.ingestor.get_recent_activity(symbol, days=7)
        
        total_buy_value = 0
        for r in recent_activity:
            if r['transaction_type'] == 'Purchase':
                total_buy_value += r['value']

        # LOGIC
        is_uptrend = current_price > sma20
        has_insider_conviction = total_buy_value > 250000

        if is_uptrend and has_insider_conviction:
            if is_owned:
                return {"asset": symbol, "price": current_price, "action": "HOLD", "reason": "Insider Momentum (Holding)"}
            
            # Position Sizing (Standard Risk)
            # We could be more aggressive here if we wanted
            risk_per_trade = equity * settings.risk_per_trade
            # Simple Stop Loss at SMA 20
            stop_loss = sma20 
            risk_per_share = current_price - stop_loss
            
            qty = 0
            if risk_per_share > 0:
                qty = risk_per_trade / risk_per_share
            
            return {
                "asset": symbol,
                "price": current_price,
                "action": "BUY",
                "quantity": int(qty),
                "reason": f"Insider Conviction (${int(total_buy_value/1000)}k Buys) + Uptrend",
                "stop_loss": stop_loss,
                "take_profit": current_price * 1.2 # 20% upside target
            }

        return {"asset": symbol, "price": current_price, "action": "WAIT", "reason": "No Insider Signal"}
