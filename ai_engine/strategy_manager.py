import sys
import os

# Dynamic Imports to handle folder structure variations
try:
    from strategy import TechnicalStrategy # The original RSI engine
except ImportError:
    print("⚠️ Warning: Technical Strategy not found.")
    class TechnicalStrategy: 
        def analyze(self, s, h, p, e, set): return None

try:
    # Try root first, then subfolder
    from insider_strategy import InsiderMomentumStrategy
except ImportError:
    try:
        from strategies.insider_strategy import InsiderMomentumStrategy
    except ImportError:
        print("⚠️ Warning: Insider Strategy not found.")
        class InsiderMomentumStrategy:
            def analyze(self, s, h, p, e, set): return None

class StrategyManager:
    def __init__(self):
        # 1. Registry
        self.strategies = {
            "TECHNICAL": TechnicalStrategy(),
            "INSIDER": None # Will be initialized properly if passed in, or we can init here if we have dependencies
        }
        # 2. State (Default ON)
        self.active_map = {
            "TECHNICAL": True,
            "INSIDER": True
        }

    def register_strategy(self, strategy):
        """Add a strategy to the manager"""
        # Determine name based on class or attribute
        name = getattr(strategy, "name", "UNKNOWN").upper()
        if "TECHNICAL" in name: name = "TECHNICAL"
        if "INSIDER" in name: name = "INSIDER"
        
        self.strategies[name] = strategy
        self.active_map[name] = True
        print(f"✅ Strategy Registered: {name}")

    def set_active(self, name: str, state: bool):
        if name in self.active_map:
            self.active_map[name] = state
            return True
        return False

    def get_status(self):
        return self.active_map

    def run_all_strategies(self, symbol, history, is_owned, equity, settings):
        """Run enabled strategies and return the first BUY signal"""
        decisions = []
        
        # Default decision
        final_decision = {
            "asset": symbol,
            "price": 0,
            "action": "WAIT",
            "reason": "No active strategy triggered",
            "quantity": 0
        }
        
        if history:
             final_decision["price"] = float(history[-1]['close'])

        for name, engine in self.strategies.items():
            if not self.active_map.get(name):
                continue # Skip disabled strategies
            
            if engine is None:
                continue

            try:
                # Unified analyze method signature expected
                res = engine.analyze(symbol, history, is_owned, equity, settings)
                
                if res and res.get("action") == "BUY":
                    decisions.append({
                        "strategy": name,
                        "decision": res
                    })
                
                # If we own it and ANY strategy says SELL, we should probably listen (or at least consider it)
                if is_owned and res and res.get("action") == "SELL":
                     return res

            except Exception as e:
                print(f"Strategy {name} error: {e}")

        # Aggregation: First active BUY wins (Priority Logic)
        if decisions:
            # You could add logic here to prioritize INSIDER over TECHNICAL
            return decisions[0]["decision"]
            
        return final_decision
