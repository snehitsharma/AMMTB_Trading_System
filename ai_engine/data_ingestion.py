import requests
import sqlite3
import pandas as pd
import os
import random
from datetime import datetime, timedelta
import threading
import time

class InsiderDataIngestor:
    def __init__(self, db_path="insider.db"):
        self.api_key = os.getenv("QUIVER_QUANT_KEY")
        self.db_path = db_path
        self.running = False
        self._init_db()

    def _init_db(self):
        """Create the insider_filings table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insider_filings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                insider_name TEXT,
                role TEXT,
                transaction_type TEXT,
                shares INTEGER,
                price REAL,
                value REAL,
                date TEXT,
                UNIQUE(ticker, insider_name, date, value)
            )
        ''')
        conn.commit()
        conn.close()

    def fetch_daily_filings(self):
        """Fetch filings from API or Mock Generator"""
        print("🕵️  Fetching Insider Filings...")
        
        if self.api_key:
            data = self._fetch_from_api()
        else:
            print("⚠️  No QuiverQuant Key found. Using Mock Generator.")
            data = self._generate_mock_data()

        self.save_filings(data)
        print(f"✅  Ingested {len(data)} insider filings.")
        return data

    def _fetch_from_api(self):
        """Real API Call to QuiverQuant"""
        # Placeholder for actual API implementation
        # url = "https://api.quiverquant.com/beta/live/insiders"
        # headers = {"Authorization": f"Token {self.api_key}"}
        # ...
        return []

    def _generate_mock_data(self):
        """Generate realistic dummy data for testing"""
        tickers = ["AAPL", "NVDA", "TSLA", "MSFT", "AMD", "PLTR", "COIN"]
        roles = ["CEO", "CFO", "Director", "VP", "10% Owner"]
        types = ["Purchase", "Sale"]
        
        data = []
        for _ in range(random.randint(5, 15)):
            ticker = random.choice(tickers)
            price = random.uniform(100, 500)
            shares = random.randint(100, 10000)
            
            # Logic: CEOs usually buy big
            role = random.choice(roles)
            if role == "CEO": shares *= 2
            
            # Logic: Sales are more common than buys
            trans_type = random.choices(types, weights=[0.3, 0.7])[0]
            
            filing = {
                "ticker": ticker,
                "insider_name": f"John Doe {random.randint(1,99)}",
                "role": role,
                "transaction_type": trans_type,
                "shares": shares,
                "price": round(price, 2),
                "value": round(shares * price, 2),
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            data.append(filing)
        return data

    def save_filings(self, filings):
        """Persist data to SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        count = 0
        for f in filings:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO insider_filings 
                    (ticker, insider_name, role, transaction_type, shares, price, value, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (f['ticker'], f['insider_name'], f['role'], f['transaction_type'], 
                      f['shares'], f['price'], f['value'], f['date']))
                if cursor.rowcount > 0:
                    count += 1
            except Exception as e:
                print(f"DB Error: {e}")
                
        conn.commit()
        conn.close()
        # print(f"Saved {count} new filings to DB.")

    def get_recent_activity(self, ticker, days=30):
        """Query DB for recent insider moves on a ticker"""
        conn = sqlite3.connect(self.db_path)
        # Calculate date threshold
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        df = pd.read_sql_query(f'''
            SELECT * FROM insider_filings 
            WHERE ticker = '{ticker}' AND date >= '{cutoff}'
            ORDER BY date DESC
        ''', conn)
        conn.close()
        return df.to_dict(orient="records")

    def start_scheduler(self, interval_minutes=10):
        """Run fetch loop in background"""
        self.running = True
        def loop():
            while self.running:
                try:
                    self.fetch_daily_filings()
                except Exception as e:
                    print(f"Ingestor Error: {e}")
                time.sleep(interval_minutes * 60)
                
        threading.Thread(target=loop, daemon=True).start()
        print("🕰️  Insider Ingestor Scheduler Started.")

    def stop(self):
        self.running = False
