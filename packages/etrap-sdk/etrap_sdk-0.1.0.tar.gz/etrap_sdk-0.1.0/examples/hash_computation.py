#!/usr/bin/env python3
"""
================================================================================
ETRAP SDK - Transaction Hash Computation Tool
================================================================================

This tool demonstrates how transaction hashes are computed by the ETRAP SDK
and provides debugging capabilities for hash calculation issues.

What this tool shows:
- Original transaction data with field types
- Normalized transaction data (what actually gets hashed)
- Final computed hash used for blockchain verification
- Step-by-step normalization process for debugging
- Comparison with and without normalization

This is primarily useful for:
- Debugging hash calculation differences between systems
- Understanding the normalization process applied to transaction data
- Troubleshooting verification failures due to hash mismatches
- Validating that transaction data produces the expected hash

Usage: python hash_computation.py [transaction_json]

Arguments:
  transaction_json - Optional JSON string containing transaction data
                    If not provided, uses example transaction data

Example: python hash_computation.py '{"id": 144, "account_id": "TEST555", "amount": "55555.55", "type": "C", "created_at": "2025-06-28 17:48:09.243538", "reference": "Test DEFAULT identity"}'

The tool will display the original data, normalized data, and computed hash
for debugging hash calculation issues.
"""

import json
import sys
from etrap_sdk import normalize_transaction_data, compute_transaction_hash


def main():
    # Check if transaction data provided as command line argument
    if len(sys.argv) > 1:
        try:
            db_transaction = json.loads(sys.argv[1])
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print("Please provide valid JSON transaction data")
            sys.exit(1)
    else:
        # Default example transaction
        db_transaction = {
            "id": 109,
            "account_id": "ACC999",
            "amount": 999.99,
            "type": "C",
            "created_at": "2025-06-14 07:10:55.461133",  # Space separator
            "reference": "TEST-VERIFY"
        }
    
    print("Original transaction from database:")
    for key, value in db_transaction.items():
        print(f"  {key}: {value} ({type(value).__name__})")
    
    # Normalize the transaction
    normalized = normalize_transaction_data(db_transaction)
    
    print("\nNormalized transaction:")
    for key, value in normalized.items():
        print(f"  {key}: {value} ({type(value).__name__})")
    
    # Compute hash
    hash_with_norm = compute_transaction_hash(db_transaction, normalize=True)
    hash_without_norm = compute_transaction_hash(db_transaction, normalize=False)
    
    print(f"\nHash with normalization: {hash_with_norm}")
    print(f"Hash without normalization: {hash_without_norm}")
    
    # Show that different formats produce same hash when normalized
    alt_transaction = {
        "id": "109",  # String instead of int
        "account_id": "ACC999",
        "amount": "999.99",  # String instead of float
        "type": "C",
        "created_at": "2025-06-14T07:10:55.461",  # T separator, 3 decimals
        "reference": "TEST-VERIFY"
    }
    
    alt_hash = compute_transaction_hash(alt_transaction, normalize=True)
    print(f"\nAlternative format hash: {alt_hash}")
    print(f"Hashes match: {hash_with_norm == alt_hash}")
    
    # Show null value handling
    tx_with_null = db_transaction.copy()
    tx_with_null["optional_field"] = None
    
    hash_with_null = compute_transaction_hash(tx_with_null, normalize=True)
    print(f"\nHash with null field: {hash_with_null}")
    print(f"Null fields ignored: {hash_with_norm == hash_with_null}")


if __name__ == "__main__":
    main()