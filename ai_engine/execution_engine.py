import requests
import json
from datetime import datetime
from portfolio_manager import PortfolioManager

class ExecutionEngine:
    def __init__(self, portfolio_manager: PortfolioManager, us_agent_url, crypto_agent_url, orchestrator_url):
        self.pm = portfolio_manager
        self.US_AGENT = us_agent_url
        self.CRYPTO_AGENT = crypto_agent_url
        self.ORCHESTRATOR = orchestrator_url
        self.trade_history = [] # In-memory storage for now

    def execute_signal(self, signal, equity, current_holdings_value=0):
        """
        Executes a trading signal after passing risk checks.
        """
        symbol = signal['asset']
        action = signal['action']
        price = signal['price']
        quantity = signal.get('quantity', 0)
        reason = signal.get('reason', 'Signal')
        
        # 1. Risk Check & Sizing
        # Note: check_trade returns safe_qty based on 5% rule if quantity is 0 or too high
        # We pass 0 as current_exposure for now if we don't have it per asset, 
        # but PM checks total exposure. Ideally we pass asset specific exposure too if needed.
        # For now, we rely on PM to check total exposure and sizing.
        
        # We need to calculate current exposure pct for the PM check
        # Assuming equity > 0
        exposure_pct = (equity - (equity - current_holdings_value)) / equity if equity > 0 else 0
        
        is_approved, rejection_reason, safe_qty = self.pm.check_trade(
            symbol, price, equity, exposure_pct
        )

        if not is_approved:
            print(f"❌ Trade Rejected: {rejection_reason}")
            self._log_event("TRADE_REJECTED", f"{symbol} {action}: {rejection_reason}")
            return {"status": "REJECTED", "reason": rejection_reason}

        # Use the safe quantity calculated by Risk Desk
        quantity = safe_qty
        
        # 2. Smart Execution (Bracket Orders)
        sl, tp = self.pm.get_sl_tp(price)
        
        # 3. Route Order
        target_agent = self.CRYPTO_AGENT if "/" in symbol else self.US_AGENT
        
        order_payload = {
            "symbol": symbol,
            "qty": quantity,
            "side": action.lower(),
            "type": "market", 
            "time_in_force": "gtc",
            "take_profit": tp,
            "stop_loss": sl
        }
        
        try:
            print(f"🚀 Executing {action} {quantity} {symbol} via {target_agent}...")
            print(f"   🛡️ Bracket: TP ${tp:.2f} | SL ${sl:.2f}")
            
            response = requests.post(f"{target_agent}/api/v1/trade", json=order_payload)
            
            if response.status_code == 200:
                details = response.json()
                self._log_event("TRADE_EXECUTED", f"Executed {action} {quantity} {symbol} @ ${price}")
                
                # Record Trade
                trade_record = {
                    "id": details.get("id", "unknown"),
                    "ticker": symbol,
                    "side": action,
                    "size": quantity,
                    "entry_price": price,
                    "stop_price": sl,
                    "take_profit_price": tp,
                    "timestamp": datetime.now().isoformat(),
                    "strategy_source": reason,
                    "status": "FILLED"
                }
                self.trade_history.append(trade_record)
                
                return {"status": "FILLED", "details": details}
            else:
                error_msg = f"Execution Failed: {response.text}"
                print(f"❌ {error_msg}")
                self._log_event("EXECUTION_ERROR", error_msg)
                return {"status": "ERROR", "reason": response.text}
                
        except Exception as e:
            print(f"❌ Network Error: {e}")
            self._log_event("NETWORK_ERROR", str(e))
            return {"status": "ERROR", "reason": str(e)}

    def get_trade_history(self):
        return self.trade_history

    def _log_event(self, event_type, message):
        try:
            requests.post(f"{self.ORCHESTRATOR}/log_event", json={
                "event": event_type,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
        except:
            pass # Don't crash on logging fail
