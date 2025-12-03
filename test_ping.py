from alpaca.trading.client import TradingClient
from alpaca.common.exceptions import APIError
import sys

print("🚀 Starting Ping Test...")

try:
    # Initialize with FAKE keys to test connectivity
    client = TradingClient("FAKE_KEY", "FAKE_SECRET", paper=True)
    
    print("📡 Attempting to contact Alpaca API...")
    client.get_account()
    
    # If we get here, it means the fake keys worked (Impossible)
    print("❌ FAIL: Function succeeded with fake keys? System is HALLUCINATING.")
    sys.exit(1)

except APIError as e:
    error_msg = str(e).lower()
    if "401" in error_msg or "unauthorized" in error_msg or "forbidden" in error_msg:
        print("✅ PASS: Received 401 Unauthorized from Real Alpaca Server.")
        print("   (This proves the network connection is live and the library is real.)")
    else:
        print(f"⚠️ WARNING: Unexpected API Error: {e}")
        sys.exit(1)

except ImportError:
    print("❌ FAIL: Module 'alpaca' not found. Is alpaca-py installed?")
    sys.exit(1)

except Exception as e:
    print(f"❌ CRITICAL: Script crashed with unexpected error: {e}")
    sys.exit(1)
