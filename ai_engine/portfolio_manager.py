import datetime

class PortfolioManager:
    def __init__(self):
        # --- FEATURE 6 CONSTANTS ---
        self.TARGET_POS_SIZE = 0.05       # 5% per trade
        self.MAX_TOTAL_EXPOSURE = 0.25    # Max 25% invested (75% cash)
        self.DAILY_DD_LIMIT = 0.03        # 3% Kill Switch
        self.STOP_LOSS_PCT = 0.05         # -5% Hard Stop
        self.TAKE_PROFIT_PCT = 0.10       # +10% Hard Target
        
        # State Tracking
        self.daily_high = 0.0
        self.is_kill_switch_active = False

    def update_metrics(self, equity):
        """Update high water mark for drawdown calculation"""
        if equity > self.daily_high:
            self.daily_high = equity
        
        current_dd = (self.daily_high - equity) / self.daily_high if self.daily_high > 0 else 0
        
        if current_dd > self.DAILY_DD_LIMIT:
            self.is_kill_switch_active = True
        
        return current_dd

    def check_trade(self, symbol, price, equity, current_exposure):
        """
        Validates a trade against strict risk rules.
        Returns: (Allowed: bool, Reason: str, SafeQty: float)
        """
        # 1. KILL SWITCH CHECK
        if self.is_kill_switch_active:
            return False, "KILL SWITCH ACTIVE (Daily Drawdown > 3%)", 0

        # 2. EXPOSURE CHECK
        # If current exposure is already > 25%, no new buys.
        if current_exposure >= (equity * self.MAX_TOTAL_EXPOSURE):
            return False, f"Max Exposure Reached ({self.MAX_TOTAL_EXPOSURE*100}%)", 0

        # 3. POSITION SIZING
        # Target = 5% of Equity
        target_value = equity * self.TARGET_POS_SIZE
        safe_qty = target_value / price
        
        # Adjust for Crypto vs Stock (decimals)
        if "/" in symbol:
            safe_qty = round(safe_qty, 4)
        else:
            safe_qty = int(safe_qty)

        if safe_qty <= 0:
            return False, "Calculated Qty is 0", 0
            
        return True, "Risk Approved", safe_qty

    def get_sl_tp(self, price):
        """Return calculated Hard Stop/Limit prices"""
        sl = price * (1 - self.STOP_LOSS_PCT)
        tp = price * (1 + self.TAKE_PROFIT_PCT)
        return sl, tp

    def get_risk_metrics(self, equity, cash):
        drawdown = self.update_metrics(equity)
        exposure_pct = (equity - cash) / equity if equity > 0 else 0
        return {
            "daily_drawdown": drawdown,
            "kill_switch": self.is_kill_switch_active,
            "current_exposure": exposure_pct,
            "cash_buffer": cash / equity if equity > 0 else 0,
            "rules": {
                "max_exposure": self.MAX_TOTAL_EXPOSURE,
                "pos_size": self.TARGET_POS_SIZE,
                "daily_limit": self.DAILY_DD_LIMIT
            }
        }
