from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"

class TradeRequest(BaseModel):
    symbol: str
    side: Side
    qty: float
    type: OrderType
    price: Optional[float] = None

class Position(BaseModel):
    symbol: str
    qty: float
    avg_price: float
    current_price: float
    unrealized_pl: float

class AccountSummary(BaseModel):
    broker: str
    cash_balance: float
    unrealized_pl: float
    total_equity: float

class OrderConfirmation(BaseModel):
    order_id: str
    status: str
    message: str
