from alpaca.trading.client import TradingClient
from alpaca.common.exceptions import APIError
import sys

# Use INVALID keys. If the code is real, Alpaca will reject us (401).
# If the code is fake, it might accidentally "succeed".
try:
    client = TradingClient("PK_FAKE_KEY", "FAKE_SECRET", paper=True)
    client.get_account()
    print("❌ FAIL: Function succeeded with fake keys? System is HALLUCINATING.")
    sys.exit(1)
except APIError as e:
    if "401" in str(e) or "unauthorized" in str(e).lower():
        print("✅ PASS: Received 401 Unauthorized from Real Alpaca Server.")
        print("   (This proves the network connection is live and the library is real.)")
    else:
        print(f"⚠️ WARNING: Unexpected error: {e}")
except Exception as e:
    print(f"❌ CRITICAL: Script crashed. Is 'alpaca-py' installed? Error: {e}")
    sys.exit(1)
