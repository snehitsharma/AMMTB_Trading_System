
import aiosqlite
import asyncio
import time
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "us_ledger.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
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
            return [dict(row) for row in rows][::-1]
