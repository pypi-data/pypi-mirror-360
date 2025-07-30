#!/usr/bin/env python3
"""
================================================================================
ETRAP SDK - Basic Usage Example
================================================================================

This example demonstrates the core functionality of the ETRAP SDK for verifying
database transactions against blockchain records stored on NEAR Protocol.

What this example shows:
- How to initialize the ETRAPClient with organization and network settings
- How to verify a transaction using the SDK's verify_transaction() method
- How to use optimization hints to improve verification performance
- Transaction hash computation and verification result handling

The example uses hardcoded transaction data from the 'lunaris' organization
that exists in the NEAR testnet blockchain for demonstration purposes.

Usage: python basic_usage.py

No parameters required - this is a self-contained demonstration.
"""

import asyncio
import logging
from etrap_sdk import ETRAPClient, S3Config, VerificationHints


async def main():
    # Optional: Enable debug logging to see what the SDK is doing
    # Uncomment these lines to see detailed SDK operations:
    # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # logging.getLogger('etrap_sdk').setLevel(logging.DEBUG)
    
    # Initialize the client for the 'lunaris' organization on testnet
    client = ETRAPClient(
        organization_id="lunaris",
        network="testnet",
        s3_config=S3Config(
            # bucket_name is automatically derived as "etrap-lunaris"
            # contract_id is automatically set to "lunaris.testnet"
            region="us-west-2"
        )
    )
    
    # Example transaction data (as returned from database)
    # This is record ID 144 that exists in batch BATCH-2025-06-28-1107c8e1
    transaction = {
        "id": 144,
        "account_id": "TEST555",
        "amount": "55555.55",
        "type": "C",
        "created_at": "2025-06-28 17:48:09.243538",
        "reference": "Test DEFAULT identity"
    }
    
    # Show computed hash
    tx_hash = client.compute_transaction_hash(transaction)
    print(f"Transaction hash: {tx_hash}")
    
    print("\nVerifying transaction...")
    print(f"  ID: {transaction['id']}")
    print(f"  Account: {transaction['account_id']}")
    print(f"  Amount: {transaction['amount']}")
    
    try:
        # Verify the transaction
        result = await client.verify_transaction(transaction)
        
        if result.verified:
            print(f"\n✓ Transaction verified!")
            print(f"  Batch ID: {result.batch_id}")
            print(f"  Blockchain timestamp: {result.blockchain_timestamp}")
            print(f"  Transaction hash: {result.transaction_hash}")
        else:
            print(f"\n✗ Verification failed: {result.error}")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    # Example with optimization hints
    print("\n\nVerifying with hints...")
    
    hints = VerificationHints(
        table_name="financial_transactions",
        database_name="etrapdb"
    )
    
    try:
        result = await client.verify_transaction(transaction, hints=hints)
        
        if result.verified:
            print(f"\n✓ Transaction verified with hints!")
            print(f"  Batch ID: {result.batch_id}")
        else:
            print(f"\n✗ Verification failed: {result.error}")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())