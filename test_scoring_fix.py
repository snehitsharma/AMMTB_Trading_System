
import asyncio
import os
from dotenv import load_dotenv
from us_backend.analysis.scoring import calculate_confluence_score

# Mock Data with None values
insider_mock = [
    {"transactionType": "Buy", "securitiesTransacted": None, "price": 100}, # Should handle None
    {"transactionType": "Buy", "securitiesTransacted": 1000, "price": 50},
]
earnings_mock = {"estimatedEPS": 1.0, "actualEPS": 1.2}
tech_mock = {"vol_spike": True}
macro_mock = {"btc": 95000}

print("Testing Scoring Fix...")
try:
    score, report = calculate_confluence_score(insider_mock, earnings_mock, tech_mock, macro_mock)
    print(f"✅ Score: {score}")
    print(f"📝 Report: {report}")
except Exception as e:
    print(f"❌ Failed: {e}")
