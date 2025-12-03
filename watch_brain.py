import time
import requests
import os
from datetime import datetime

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

print("🧠 Connecting to AI Brain...")
while True:
    try:
        # Fetch Signals
        res = requests.get("http://localhost:8004/api/v1/signals", timeout=30)
        data = res.json()
        
        clear()
        # Add timestamp if not present in data
        timestamp = data.get('timestamp', datetime.now().strftime("%H:%M:%S"))
        
        print(f"--- AI BRAIN MONITOR [ {timestamp} ] ---")
        print(f"📊 MARKET REGIME: {data.get('regime', 'UNKNOWN')}")
        print("-" * 80)
        print(f"{'ASSET':<10} | {'PRICE':<10} | {'ACTION':<6} | {'REASONING'}")
        print("-" * 80)
        
        for item in data.get('scan_results', []):
            price = f"${item.get('price', 0):.2f}"
            print(f"{item['asset']:<10} | {price:<10} | {item['action']:<6} | {item['reason']}")
            
        print("-" * 80)
        print("Press Ctrl+C to stop.")
        
    except Exception as e:
        # Don't clear screen on error so we can see it, just print error
        print(f"❌ Error contacting AI: {e}")
    
    time.sleep(2)
