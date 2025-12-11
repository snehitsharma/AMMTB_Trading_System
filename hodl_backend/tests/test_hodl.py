import pytest
import sys
import os
import asyncio

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hodl_backend import db, rug_checker

@pytest.mark.asyncio
async def test_db_init():
    # Test DB creation
    await db.init_db()
    assert os.path.exists(db.DB_PATH)

@pytest.mark.asyncio
async def test_save_and_get_position():
    await db.init_db()
    await db.save_position("test_addr", "TEST", 1.0, 10.0, 0.8)
    positions = await db.get_open_positions()
    assert len(positions) > 0
    found = False
    for p in positions:
        if p['token_address'] == "test_addr":
            found = True
            assert p['symbol'] == "TEST"
    assert found

@pytest.mark.asyncio
async def test_rug_checker_mock():
    # We can't easily test live API without mocking aiohttp, 
    # but we can import it and instantiate basic check logic
    checker = rug_checker.RugChecker()
    assert checker.api_url is not None
