from pydantic import BaseModel

class Settings(BaseModel):
    max_positions: int = 25
    risk_per_trade: float = 0.02
    rsi_buy_threshold: int = 55
    rsi_sell_threshold: int = 70
    stop_loss_atr_multiplier: float = 2.0
    take_profit_atr_multiplier: float = 3.0
    enable_sentiment: bool = True
    enable_risk_engine: bool = True

# Global instance
system_settings = Settings()
