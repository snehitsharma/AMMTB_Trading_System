from ledger import SQLiteLedger, Transaction
from datetime import datetime
import uuid

ledger = SQLiteLedger("ledger.db")

# Check if already seeded
conn = ledger._init_db() # Ensure tables exist
existing_balance = ledger.get_balance()

if existing_balance < 0:
    print(f"Current Balance: {existing_balance}. Seeding Initial Funding...")
    tx_id = str(uuid.uuid4())
    tx = Transaction(
        id=tx_id,
        timestamp=datetime.now().isoformat(),
        type="DEPOSIT",
        amount=25000.0,
        market="GLOBAL",
        status="COMPLETED"
    )
    ledger.add_transaction(tx)
    ledger.add_log("ADMIN", "INITIAL_SEED", {"amount": 25000, "id": tx_id})
    print(f"✅ Seeded $25,000. New Balance: {ledger.get_balance()}")
else:
    print(f"Balance Healthy: {existing_balance}")
