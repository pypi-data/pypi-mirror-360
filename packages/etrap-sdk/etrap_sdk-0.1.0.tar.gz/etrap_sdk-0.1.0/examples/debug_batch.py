#!/usr/bin/env python3
"""
================================================================================
ETRAP SDK - Debug Batch Tool
================================================================================

This tool provides detailed inspection of ETRAP batch metadata stored on the
NEAR blockchain. It retrieves and displays NFT data directly from the smart
contract and attempts to parse it using the ETRAP SDK.

What this tool shows:
- Raw NFT metadata from NEAR smart contract (nft_token method)
- Batch summary information (database, transaction count, timestamps)
- S3 storage location for detailed batch data
- Merkle root hash for cryptographic verification
- Contract address and organization information

This is primarily a debugging and inspection tool for developers working with
ETRAP blockchain data or troubleshooting batch verification issues.

Usage: python debug_batch.py <batch_id> <organization_id>

Arguments:
  batch_id        - The NFT token ID (e.g., BATCH-2025-06-28-1107c8e1)
  organization_id - Organization identifier (e.g., lunaris, acme)

Example: python debug_batch.py BATCH-2025-06-28-1107c8e1 lunaris

The tool will query the {organization_id}.testnet contract and display the
complete NFT metadata for the specified batch.
"""

import asyncio
import json
import sys
from etrap_sdk import ETRAPClient


async def main():
    if len(sys.argv) < 3:
        print("Usage: debug_batch.py <batch_id> <organization_id>")
        print("Example: debug_batch.py BATCH-2025-06-28-1107c8e1 lunaris")
        sys.exit(1)
    
    batch_id = sys.argv[1]
    organization_id = sys.argv[2]
    
    # Initialize client
    client = ETRAPClient(
        organization_id=organization_id,
        network="testnet"
    )
    
    print(f"Fetching batch: {batch_id}")
    print(f"Organization: {organization_id}")
    print(f"Contract: {organization_id}.testnet\n")
    
    try:
        # Get raw response from NEAR
        result = await client.near_account.view_function(
            client.contract_id,
            "nft_token",
            {"token_id": batch_id}
        )
        
        # Handle ViewFunctionResult
        if hasattr(result, 'result'):
            result = result.result
            
        print("Raw NFT data from contract:")
        print(json.dumps(result, indent=2))
        
        # Try to parse it
        batch = await client.get_batch(batch_id)
        if batch:
            print(f"\nParsed batch info:")
            print(f"  Database: {batch.database_name}")
            print(f"  S3 bucket: {batch.s3_location.bucket}")
            print(f"  S3 key: {batch.s3_location.key}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())