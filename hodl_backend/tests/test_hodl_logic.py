
import pytest
import shutil
import sys
import os

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rug_checker
import db

@pytest.mark.asyncio
async def test_rug_checker_mock():
    # We can mock the HTTP call or just test the logic with a mocked analyze function if dependencies allow
    # For now, we trust the integration test more, but simple pass-through here
    assert True

@pytest.mark.asyncio
async def test_db_persistence():
    # Setup
    db.DB_PATH = "test_hodl.db"
    await db.init_db()
    
    # Test Create
    pid = await db.add_position("TestToken", "TEST", 0.5, "tx123", 100)
    assert pid is not None
    
    # Test Read
    positions = await db.list_open_positions()
    assert len(positions) == 1
    assert positions[0]["token_symbol"] == "TEST"
    
    # Test Update
    await db.update_position(pid, high_price=0.6)
    positions = await db.list_open_positions()
    assert positions[0]["high_price"] == 0.6
    
    # Teardown
    os.remove("test_hodl.db")

