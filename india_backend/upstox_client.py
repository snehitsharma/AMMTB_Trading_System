import uuid
import random

class UpstoxClient:
    def __init__(self, api_key=None, access_token=None):
        self.api_key = api_key
        self.access_token = access_token
        self.positions = []
        self.orders = []

    def get_profile(self):
        return {
            "email": "user@example.com",
            "exchanges": ["NSE", "BSE"],
            "products": ["D", "CO"],
            "broker": "Upstox"
        }

    def get_funds_and_margin(self):
        # Mock funds
        return {
            "equity": {
                "available_margin": 100000.0,
                "used_margin": 0.0
            }
        }

    def place_order(self, symbol, quantity, transaction_type, order_type="MARKET", product="D"):
        order_id = str(uuid.uuid4())
        order = {
            "order_id": order_id,
            "symbol": symbol,
            "quantity": quantity,
            "transaction_type": transaction_type,
            "order_type": order_type,
            "product": product,
            "status": "COMPLETE", # Auto-fill for mock
            "average_price": 24000.0 + random.uniform(-50, 50) # Mock fill price
        }
        self.orders.append(order)
        
        # Update positions (simplified)
        self.positions.append({
            "symbol": symbol,
            "quantity": quantity if transaction_type == "BUY" else -quantity,
            "average_price": order["average_price"]
        })
        
        return order

    def get_positions(self):
        return self.positions

    def get_orders(self):
        return self.orders
