import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

load_dotenv()

print("Checking Alpaca Keys...")
api_key = os.getenv("ALPACA_API_KEY")
secret_key = os.getenv("ALPACA_SECRET_KEY")

if not api_key:
    print("❌ ALPACA_API_KEY is missing from .env")
elif not secret_key:
    print("❌ ALPACA_SECRET_KEY is missing from .env")
else:
    print(f"✅ Keys Found (API_KEY starts with {api_key[:4]})")
    try:
        print("Connecting to Alpaca Paper Trading...")
        client = TradingClient(api_key, secret_key, paper=True)
        acct = client.get_account()
        print(f"✅ Connection Success! Equity: ${acct.equity}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
