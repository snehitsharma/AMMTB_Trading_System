import pandas as pd
import numpy as np
import requests
from datetime import datetime
from strategy_manager import StrategyManager

class Backtester:
    def __init__(self, strategy_manager: StrategyManager, us_agent_url, crypto_agent_url):
        self.strategy_manager = strategy_manager
        self.US_AGENT = us_agent_url
        self.CRYPTO_AGENT = crypto_agent_url

    def run_backtest(self, symbol, strategy_name, days=90, initial_equity=100000):
        """
        Replays history and simulates trading.
        """
        print(f"⏳ Starting Backtest: {symbol} ({strategy_name}) for {days} days...")
        
        # 1. Fetch History
        agent_url = self.CRYPTO_AGENT if "/" in symbol else self.US_AGENT
        limit = days + 50 # Buffer for indicators
        
        try:
            res = requests.get(f"{agent_url}/api/v1/history?symbol={symbol}&limit={limit}")
            if res.status_code != 200:
                return {"error": "Failed to fetch history"}
            
            full_history = res.json()
            if len(full_history) < 50:
                return {"error": "Not enough data"}
                
        except Exception as e:
            return {"error": str(e)}

        # 2. Simulation Loop
        equity = initial_equity
        cash = initial_equity
        position = 0
        
        equity_curve = [] # [{date, equity}]
        trades = [] # [{date, type, price, qty, pnl}]
        
        # We need to iterate day by day, but we need enough history for indicators.
        # So we start loop from index 50
        
        # Convert to DataFrame for easier slicing if needed, but list of dicts is fine for now.
        # Let's assume history is sorted ASCENDING (Oldest first). 
        # If it's descending, we flip it.
        if full_history[0]['timestamp'] > full_history[-1]['timestamp']:
            full_history = full_history[::-1]

        for i in range(50, len(full_history)):
            # Slice history up to current day 'i'
            # We simulate that 'today' is full_history[i]
            # But strategies usually need 'closed' candles. 
            # So we pass history[0...i] and make decision for NEXT open or THIS close.
            # Let's assume we trade on CLOSE of day 'i' for simplicity of backtest.
            
            current_candle = full_history[i]
            current_date = current_candle['timestamp']
            current_price = current_candle['close']
            
            history_slice = full_history[:i+1]
            
            # Run Strategy
            # We need to temporarily force the strategy manager to use ONLY the selected strategy
            # or we just instantiate the strategy directly. 
            # Using manager is better if we want to test the full logic.
            # But manager runs ALL strategies. 
            # For this MVP, let's assume we just want to test the Technical Strategy for now.
            # Or we can ask manager to run specific strategy if we add that feature.
            # Let's just use the strategy instance directly from manager if possible.
            
            strategy = self.strategy_manager.strategies.get(strategy_name)
            if not strategy:
                return {"error": f"Strategy {strategy_name} not found"}

            # Mock settings
            from settings import system_settings
            
            decision = strategy.analyze(symbol, history_slice, position > 0, equity, system_settings)
            
            # Execute Logic (Simplified)
            action = decision['action']
            
            if action == "BUY" and cash > 0:
                # Buy Max
                qty = int(cash / current_price)
                if qty > 0:
                    cost = qty * current_price
                    cash -= cost
                    position += qty
                    trades.append({
                        "date": current_date,
                        "type": "BUY",
                        "price": current_price,
                        "qty": qty,
                        "value": cost
                    })
            
            elif action == "SELL" and position > 0:
                # Sell All
                revenue = position * current_price
                cash += revenue
                
                # Calculate PnL of this trade cycle
                last_buy = next((t for t in reversed(trades) if t['type'] == "BUY"), None)
                pnl = 0
                if last_buy:
                    pnl = revenue - last_buy['value']
                
                trades.append({
                    "date": current_date,
                    "type": "SELL",
                    "price": current_price,
                    "qty": position,
                    "value": revenue,
                    "pnl": pnl
                })
                position = 0

            # Update Equity
            current_equity = cash + (position * current_price)
            equity_curve.append({"date": current_date, "equity": current_equity})

        # 3. Calculate Metrics
        final_equity = equity_curve[-1]['equity'] if equity_curve else initial_equity
        total_return = ((final_equity - initial_equity) / initial_equity) * 100
        
        # Win Rate
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        total_sell_trades = [t for t in trades if t['type'] == "SELL"]
        win_rate = (len(winning_trades) / len(total_sell_trades) * 100) if total_sell_trades else 0
        
        # Max Drawdown
        max_equity = initial_equity
        max_drawdown = 0
        for point in equity_curve:
            if point['equity'] > max_equity:
                max_equity = point['equity']
            drawdown = (max_equity - point['equity']) / max_equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            "symbol": symbol,
            "strategy": strategy_name,
            "metrics": {
                "total_return": round(total_return, 2),
                "win_rate": round(win_rate, 2),
                "max_drawdown": round(max_drawdown * 100, 2),
                "trades_count": len(trades)
            },
            "equity_curve": equity_curve,
            "trades": trades
        }
