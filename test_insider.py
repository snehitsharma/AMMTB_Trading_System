from ai_engine.data_ingestion import InsiderDataIngestor
import time

def test_ingestion():
    print("🧪 Testing Insider Data Ingestion...")
    
    # 1. Initialize
    ingestor = InsiderDataIngestor(db_path="test_insider.db")
    
    # 2. Fetch Data (Should trigger Mock Generator)
    print("\n--- Fetching Data ---")
    data = ingestor.fetch_daily_filings()
    
    if not data:
        print("❌ No data returned!")
        return
        
    print(f"✅ Received {len(data)} filings.")
    print(f"Sample: {data[0]}")
    
    # 3. Verify DB Persistence
    print("\n--- Verifying DB ---")
    ticker = data[0]['ticker']
    recent = ingestor.get_recent_activity(ticker)
    
    if len(recent) > 0:
        print(f"✅ DB Query Successful for {ticker}: Found {len(recent)} records.")
        for r in recent:
            print(f"   - {r['date']}: {r['insider_name']} ({r['role']}) {r['transaction_type']} {r['shares']} shares @ ${r['price']}")
    else:
        print(f"❌ DB Query Failed for {ticker}")

if __name__ == "__main__":
    test_ingestion()
