import requests
import json
import time

BASE_URL = "http://localhost:8005/api/v1"

def test_banking():
    print("🏦 Testing Admin Banking System...")
    
    # 1. Request Withdrawal
    print("\n1️⃣ Requesting Withdrawal ($5000)...")
    res = requests.post(f"{BASE_URL}/withdraw", json={"amount": 5000, "market": "US"})
    if res.status_code == 200:
        tx_id = res.json()["transaction_id"]
        print(f"✅ Withdrawal Requested. ID: {tx_id}")
    else:
        print(f"❌ Request Failed: {res.text}")
        return

    # 2. Check Balance (Should be unchanged yet)
    res = requests.get(f"{BASE_URL}/wallet/balance")
    bal_before = res.json()["balance"]
    print(f"💰 Balance Before Approval: ${bal_before}")

    # 3. Approve Transaction
    print(f"\n2️⃣ Approving Transaction {tx_id}...")
    res = requests.patch(f"{BASE_URL}/transactions/{tx_id}", json={"action": "APPROVE"})
    if res.status_code == 200:
        print("✅ Transaction Approved!")
    else:
        print(f"❌ Approval Failed: {res.text}")
        return

    # 4. Check Balance (Should decrease)
    res = requests.get(f"{BASE_URL}/wallet/balance")
    bal_after = res.json()["balance"]
    print(f"💰 Balance After Approval: ${bal_after}")
    
    if bal_after < bal_before:
        print("✅ Balance Decreased Correctly.")
    else:
        print("⚠️ Balance did not decrease (Check Ledger Logic).")

    # 5. Test Rejection
    print("\n3️⃣ Testing Rejection Flow...")
    res = requests.post(f"{BASE_URL}/withdraw", json={"amount": 10000, "market": "CRYPTO"})
    tx_id_2 = res.json()["transaction_id"]
    print(f"Requested $10,000 (ID: {tx_id_2})")
    
    requests.patch(f"{BASE_URL}/transactions/{tx_id_2}", json={"action": "REJECT"})
    print("✅ Transaction Rejected.")
    
    # Verify Status
    res = requests.get(f"{BASE_URL}/logs")
    txs = res.json()["transactions"]
    rejected_tx = next((t for t in txs if t["id"] == tx_id_2), None)
    if rejected_tx and rejected_tx["status"] == "REJECTED":
        print("✅ Status Verified: REJECTED")
    else:
        print(f"❌ Status Verification Failed: {rejected_tx}")

if __name__ == "__main__":
    test_banking()
