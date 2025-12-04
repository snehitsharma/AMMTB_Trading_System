from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel

class Transaction(BaseModel):
    id: str
    timestamp: str
    type: str  # "DEPOSIT", "WITHDRAWAL"
    amount: float
    market: str
    status: str  # "PENDING", "COMPLETED", "FAILED"

class LogEntry(BaseModel):
    timestamp: str
    source: str
    event: str
    details: Dict[str, Any]

import sqlite3
import json

class SQLiteLedger:
    def __init__(self, db_path="ledger.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Transactions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                type TEXT,
                amount REAL,
                market TEXT,
                status TEXT
            )
        ''')
        
        # Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                source TEXT,
                event TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_transaction(self, transaction: Transaction):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (id, timestamp, type, amount, market, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction.id, transaction.timestamp, transaction.type, transaction.amount, transaction.market, transaction.status))
        conn.commit()
        conn.close()

    def add_log(self, source: str, event: str, details: Dict[str, Any] = {}):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (timestamp, source, event, details)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), source, event, json.dumps(details)))
        conn.commit()
        conn.close()

    def get_logs(self) -> List[LogEntry]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append(LogEntry(
                timestamp=row['timestamp'],
                source=row['source'],
                event=row['event'],
                details=json.loads(row['details'])
            ))
        return logs

    def update_transaction_status(self, transaction_id: str, status: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE transactions SET status = ? WHERE id = ?', (status, transaction_id))
        conn.commit()
        conn.close()

    def get_balance(self) -> float:
        """Calculate Available Liquidity (Deposits - Approved Withdrawals)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sum Deposits
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='DEPOSIT' AND status='COMPLETED'")
        deposits = cursor.fetchone()[0] or 0.0
        
        # Sum Approved Withdrawals
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='WITHDRAWAL' AND status='APPROVED'")
        withdrawals = cursor.fetchone()[0] or 0.0
        
        conn.close()
        return deposits - withdrawals

    def get_transactions(self) -> List[Transaction]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append(Transaction(
                id=row['id'],
                timestamp=row['timestamp'],
                type=row['type'],
                amount=row['amount'],
                market=row['market'],
                status=row['status']
            ))
        return transactions
