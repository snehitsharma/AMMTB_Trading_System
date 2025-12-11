import aiosqlite
import asyncio
import json
import time
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "hodl_ledger.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Positions Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                token_address TEXT PRIMARY KEY,
                symbol TEXT,
                entry_price REAL,
                quantity REAL,
                current_status TEXT,
                entry_time REAL,
                last_updated REAL,
                tp_levels TEXT,
                sl_price REAL,
                peak_price REAL
            )
        """)
        
        # Trades Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT,
                side TEXT,
                price REAL,
                quantity REAL,
                tx_hash TEXT,
                timestamp REAL,
                pnl REAL DEFAULT 0
            )
        """)
        
        # Logs Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                message TEXT,
                timestamp REAL
            )
        """)
        await db.commit()

async def save_position(token_address, symbol, price, qty, sl_price):
    async with aiosqlite.connect(DB_PATH) as db:
        tp_levels = json.dumps({"tp1_hit": False, "tp2_hit": False})
        await db.execute("""
            INSERT OR REPLACE INTO positions 
            (token_address, symbol, entry_price, quantity, current_status, entry_time, last_updated, tp_levels, sl_price, peak_price)
            VALUES (?, ?, ?, ?, 'OPEN', ?, ?, ?, ?, ?)
        """, (token_address, symbol, price, qty, time.time(), time.time(), tp_levels, sl_price, price))
        await db.commit()

async def get_open_positions():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM positions WHERE current_status = 'OPEN'") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def update_position(token_address, quantity, status, peak_price, tp_levels_json):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE positions 
            SET quantity = ?, current_status = ?, peak_price = ?, tp_levels = ?, last_updated = ?
            WHERE token_address = ?
        """, (quantity, status, peak_price, tp_levels_json, time.time(), token_address))
        await db.commit()

async def log_trade(token_address, side, price, qty, tx_hash, pnl=0):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO trades (token_address, side, price, quantity, tx_hash, timestamp, pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (token_address, side, price, qty, tx_hash, time.time(), pnl))
        await db.commit()

async def add_log(level, message):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO logs (level, message, timestamp) VALUES (?, ?, ?)", 
                         (level, message, time.time()))
        await db.commit()

async def get_recent_logs(limit=50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows][::-1] # Reverse to show oldest first in scroll

async def get_daily_pnl():
    """Calculate realized PnL for trades in the last 24h"""
    start_time = time.time() - 86400
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT SUM(pnl) FROM trades WHERE timestamp > ?", (start_time,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result and result[0] else 0.0
