#!/usr/bin/env python3
"""
List batches from the NEAR contract.

This example shows how to query batches and their metadata.
"""

import asyncio
from etrap_sdk import ETRAPClient, S3Config


async def main():
    # Initialize client (no S3 needed for listing)
    client = ETRAPClient(
        organization_id="acme",
        network="testnet"
    )
    
    print("Fetching recent batches from NEAR contract...\n")
    
    try:
        # List recent batches
        batch_list = await client.list_batches(limit=5)
        
        print(f"Total batches available: {batch_list.total_count}")
        print(f"Showing first {len(batch_list.batches)} batches:\n")
        
        for i, batch in enumerate(batch_list.batches, 1):
            print(f"{i}. Batch ID: {batch.batch_id}")
            print(f"   Database: {batch.database_name}")
            print(f"   Tables: {', '.join(batch.table_names)}")
            print(f"   Transactions: {batch.transaction_count}")
            print(f"   Timestamp: {batch.timestamp}")
            print(f"   Merkle root: {batch.merkle_root}")
            print(f"   S3 location: s3://{batch.s3_location.bucket}/{batch.s3_location.key}")
            print(f"   Size: {batch.size_bytes:,} bytes")
            print()
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())