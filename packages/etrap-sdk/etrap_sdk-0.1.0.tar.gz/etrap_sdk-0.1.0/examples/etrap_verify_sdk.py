#!/usr/bin/env python3
"""
================================================================================
ETRAP SDK - Transaction Verification Tool
================================================================================

Production-ready CLI tool for verifying database transactions against ETRAP
blockchain records. This is a complete SDK-based replacement for the original
etrap_verify.py with enhanced features and cleaner interface.

What this tool provides:
- Single transaction verification against blockchain records
- Multiple input methods (JSON string, file, stdin)
- Optimization hints for faster verification (batch, table, database, time)
- Smart contract or local verification methods
- JSON and human-readable output formats
- Comprehensive error handling and debugging information

This tool is designed for production use, automation, and integration into
existing verification workflows.

Usage: python etrap_verify_sdk.py -o <organization> --data '<json>' [options]

Basic Examples:
    # Verify from JSON string
    etrap_verify_sdk.py -o lunaris --data '{"id":144,"account_id":"TEST555","amount":"55555.55"}'
    
    # Verify from file
    etrap_verify_sdk.py -o lunaris --data-file transaction.json
    
    # Verify from stdin
    echo '{"id":123,...}' | etrap_verify_sdk.py -o lunaris --data -
    
    # Use optimization hints
    etrap_verify_sdk.py -o lunaris --data-file tx.json --hint-batch BATCH-2025-06-28-1107c8e1
    etrap_verify_sdk.py -o lunaris --data-file tx.json --hint-time-start 2025-06-28

Arguments:
    -o, --organization    Organization ID (required, e.g., lunaris, acme)
    --data               Transaction JSON string (use "-" for stdin)
    --data-file          Path to file containing transaction JSON
    --hint-batch         Specific batch ID for direct lookup
    --hint-time-start    Start time for time range search
    --hint-time-end      End time for time range search
    --json               Output result as JSON
    --quiet              Minimal output (just verification status)

For complete documentation and examples, see examples/README.md
"""

import argparse
import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path to import etrap_sdk
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(parent_dir, 'src'))

from etrap_sdk import ETRAPClient, S3Config, VerificationHints, TimeRange
from etrap_sdk.utils import format_transaction_summary


def print_verification_result(
    verified: bool,
    transaction_data: Dict[str, Any],
    result: Dict[str, Any],
    organization: str,
    network: str,
    quiet: bool = False
):
    """Print verification result in human-readable format."""
    if quiet:
        # Minimal output - just verification status
        if verified:
            print("✓ VERIFIED")
        else:
            print("✗ NOT VERIFIED")
        return
    
    # Header
    print("🔐 ETRAP Transaction Verification Tool")
    print(f"   Contract: {organization}.{network if network != 'mainnet' else 'near'}")
    print(f"   Network: {network}")
    print()
    
    print("🔍 ETRAP Transaction Verification")
    print("━" * 60)
    print()
    
    # Transaction hash
    tx_hash = result['transaction_hash']
    print(f"📊 Transaction Hash: {tx_hash}")
    
    # Verification method
    verification_method = result.get('verification_method', 'local')
    if verification_method == 'smart_contract':
        print(f"🔗 Verification Method: Smart Contract (on-chain)")
    else:
        print(f"💻 Verification Method: Local (off-chain)")
    print()
    
    if verified:
        # Search info if available
        if result.get('search_info'):
            if result['search_info'].get('direct_lookup'):
                print("🎯 Direct batch lookup...")
                print(f"   Using batch hint: {result['batch_id']}")
            else:
                print("🔎 Searching recent batches...")
                print(f"   Found {result['search_info']['total_batches']} recent batches to check")
                print(f"   Found in batch {result['search_info']['batch_position']} of {result['search_info']['total_batches']}")
            print()
        
        print("✅ TRANSACTION VERIFIED")
        print("━" * 60)
        print()
        
        # Transaction Details
        print("📄 Transaction Details:")
        print(f"   Hash: {tx_hash}")
        if result.get('operation_type'):
            print(f"   Operation: {result['operation_type']}")
        if result.get('batch_info'):
            batch = result['batch_info']
            print(f"   Database: {batch.get('database', 'unknown')}")
            print(f"   Table: {', '.join(batch.get('tables', []))}")
        print()
        
        # Blockchain Record
        print("🔗 Blockchain Record:")
        print(f"   NFT Token ID: {result['batch_id']}")
        print(f"   Contract: {organization}.{network if network != 'mainnet' else 'near'}")
        print(f"   Network: {network}")
        if result.get('merkle_proof'):
            print(f"   Merkle Root: {result['merkle_proof']['merkle_root']}")
        print()
        
        # Timestamp
        print("⏰ Recorded on Blockchain:")
        timestamp = result['blockchain_timestamp']
        if isinstance(timestamp, str):
            # Parse if string
            try:
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            except:
                try:
                    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                except:
                    pass
        
        if isinstance(timestamp, datetime):
            print(f"   {timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        else:
            print(f"   {timestamp}")
        print("   This is the official timestamp when this batch was")
        print("   permanently recorded on the NEAR blockchain.")
        print()
        
        # Cryptographic Proof
        if result.get('merkle_proof'):
            proof = result['merkle_proof']
            proof_height = len(proof.get('proof_path', []))
            tree_size = 2 ** proof_height if proof_height > 0 else 1
            
            print("🔐 Cryptographic Proof:")
            print(f"   Proof Height: {proof_height} levels")
            print(f"   Merkle Tree Nodes: {tree_size}")
            
            # Position in tree (if available)
            if result.get('position') is not None:
                print(f"   Position in Tree: {result['position']}")
            else:
                print(f"   Position in Tree: 0")
            print()
        
        # Audit Trail Location
        if result.get('batch_info'):
            print("💾 Audit Trail Location:")
            print(f"   S3 Bucket: etrap-{organization}")
            print(f"   S3 Path: {batch.get('database', 'unknown')}/{batch.get('tables', ['unknown'])[0]}/{result['batch_id']}/")
            print()
        
        # Search Statistics
        if result.get('search_info'):
            print("📊 Search Statistics:")
            print(f"   Batches searched: {result['search_info']['batch_position']}")
            print(f"   Found in: {result['batch_id']}")
            print()
        
        # Footer
        print("━" * 60)
        print("✅ This transaction is cryptographically proven to have existed")
        print("   in the database at the time of blockchain recording.")
        print("   Any tampering would invalidate this proof.")
        
    else:
        print("❌ VERIFICATION FAILED")
        print("━" * 60)
        print()
        if result.get('error'):
            print(f"Error: {result['error']}")
        else:
            print("Transaction not found in blockchain records.")
            print("This could mean:")
            print("  • The transaction doesn't exist")
            print("  • It hasn't been recorded on blockchain yet")
            print("  • The transaction data doesn't match exactly")


async def verify_transaction(
    client: ETRAPClient,
    transaction_data: Dict[str, Any],
    hints: Optional[Dict[str, Any]] = None,
    use_contract_verification: bool = False
) -> Dict[str, Any]:
    """Verify a transaction using the SDK."""
    # Track search statistics
    search_info = {
        'total_batches': 0,
        'batch_position': 0
    }
    
    # Create verification hints if provided
    verification_hints = None
    if hints:
        time_range = None
        if hints.get('time_start') and hints.get('time_end'):
            time_range = TimeRange(
                start=hints['time_start'],
                end=hints['time_end']
            )
        
        verification_hints = VerificationHints(
            batch_id=hints.get('batch_id'),
            table_name=hints.get('table'),
            database_name=hints.get('database'),
            time_range=time_range,
            expected_operation=hints.get('expected_operation')
        )
    
    # Track if we're using direct batch lookup
    using_batch_hint = hints and hints.get('batch_id')
    
    # Get recent batches for search statistics (unless using batch hint)
    recent_batches = []
    if not using_batch_hint:
        try:
            # Use internal method to get batch count
            recent_batches = await client._get_recent_batches(100)
            search_info['total_batches'] = len(recent_batches)
        except:
            search_info['total_batches'] = 0
    else:
        # For batch hint, we'll update statistics after verification
        search_info['total_batches'] = 1
        search_info['batch_position'] = 1
        search_info['direct_lookup'] = True
    
    # Perform verification
    result = await client.verify_transaction(
        transaction_data,
        hints=verification_hints,
        use_contract_verification=use_contract_verification
    )
    
    # Convert to dictionary format
    response = {
        'verified': result.verified,
        'transaction_hash': result.transaction_hash,
        'batch_id': result.batch_id,
        'blockchain_timestamp': result.blockchain_timestamp,
        'error': result.error,
        'search_info': search_info,
        'verification_method': 'smart_contract' if use_contract_verification else 'local'
    }
    
    if result.merkle_proof:
        response['merkle_proof'] = {
            'leaf_hash': result.merkle_proof.leaf_hash,
            'proof_path': result.merkle_proof.proof_path,
            'sibling_positions': result.merkle_proof.sibling_positions,
            'merkle_root': result.merkle_proof.merkle_root,
            'is_valid': result.merkle_proof.is_valid
        }
    
    # Get batch info and position if verified
    if result.verified and result.batch_id:
        batch = await client.get_batch(result.batch_id)
        if batch:
            response['batch_info'] = {
                'database': batch.database_name,
                'tables': batch.table_names,
                'transaction_count': batch.transaction_count,
                'timestamp': batch.timestamp
            }
            
            # Find position in recent batches
            for i, b in enumerate(recent_batches):
                if b.batch_id == result.batch_id:
                    search_info['batch_position'] = i + 1
                    break
            
            # Try to get operation type from batch data
            try:
                batch_data = await client.get_batch_data(result.batch_id)
                if batch_data:
                    # Check cached batch data for operation type
                    cache_key = f"batch_data_{result.batch_id}"
                    if cache_key in client._cache:
                        batch_json = client._cache[cache_key]
                        # Find transaction by hash
                        for tx in batch_json.get('transactions', []):
                            if tx.get('metadata', {}).get('hash') == result.transaction_hash:
                                response['operation_type'] = tx['metadata'].get('operation_type', 'INSERT')
                                response['position'] = int(tx['metadata']['transaction_id'].split('-')[-1])
                                break
            except:
                # Default to INSERT if can't determine
                response['operation_type'] = 'INSERT'
    
    return response


def load_transaction_data(args) -> Dict[str, Any]:
    """Load transaction data from various sources."""
    if args.data_file:
        # Load from file
        with open(args.data_file, 'r') as f:
            return json.load(f)
    elif args.data == '-':
        # Load from stdin
        return json.load(sys.stdin)
    else:
        # Load from command line argument
        return json.loads(args.data)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='ETRAP Transaction Verification - Verify database transactions against blockchain',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify a transaction from JSON string
  %(prog)s -o myorg --data '{"id":123,"account_id":"ACC500","amount":10000}'
  
  # Verify from a file
  %(prog)s -o myorg --data-file transaction.json
  
  # Verify from stdin
  echo '{"id":123,...}' | %(prog)s -o myorg --data -
  
  # Provide hints for faster search
  %(prog)s -o myorg --data-file tx.json --hint-table financial_transactions
  %(prog)s -o myorg --data-file tx.json --hint-batch BATCH-2025-06-14-abc123
  %(prog)s -o myorg --data-file tx.json --hint-database etrapdb
  %(prog)s -o myorg --data-file tx.json --hint-time-start 2025-06-14 --hint-time-end 2025-06-14
  
  # Use smart contract verification
  %(prog)s -o myorg --data-file tx.json --use-contract
        """
    )
    
    # Organization/contract arguments (at least one required)
    parser.add_argument(
        '-o', '--organization',
        help='Organization ID (required)'
    )
    
    # For backward compatibility, also accept --contract
    parser.add_argument(
        '-c', '--contract',
        help='NEAR contract ID (deprecated, use --organization instead)'
    )
    
    # Transaction data input (mutually exclusive)
    data_group = parser.add_mutually_exclusive_group(required=True)
    data_group.add_argument(
        '--data',
        help='Transaction data as JSON string (use "-" for stdin)'
    )
    data_group.add_argument(
        '--data-file',
        help='Path to file containing transaction JSON'
    )
    
    # Optimization hints
    parser.add_argument(
        '--hint-table',
        help='Table name hint for faster search'
    )
    parser.add_argument(
        '--hint-batch',
        help='Specific batch ID to check'
    )
    parser.add_argument(
        '--hint-database',
        help='Database name hint'
    )
    parser.add_argument(
        '--hint-time-start',
        help='Start time for time range search (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)'
    )
    parser.add_argument(
        '--hint-time-end',
        help='End time for time range search (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)'
    )
    
    # Network and output options
    parser.add_argument(
        '-n', '--network',
        choices=['testnet', 'mainnet', 'localnet'],
        default='testnet',
        help='NEAR network (default: testnet)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output result as JSON'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output (just verification status)'
    )
    parser.add_argument(
        '--use-contract',
        action='store_true',
        help='Use smart contract for verification instead of local verification'
    )
    parser.add_argument(
        '--operation',
        choices=['INSERT', 'UPDATE', 'DELETE'],
        help='Expected operation type (for disambiguating hash collisions)'
    )
    
    args = parser.parse_args()
    
    # Handle organization ID
    organization = args.organization
    if not organization and args.contract:
        # Extract organization from contract ID for backward compatibility
        # e.g., "acme.testnet" -> "acme"
        organization = args.contract.split('.')[0]
    
    if not organization:
        parser.error("Either --organization or --contract is required")
    
    # Load transaction data
    try:
        transaction_data = load_transaction_data(args)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading transaction data: {e}", file=sys.stderr)
        return 1
    
    # Create hints dictionary
    hints = {}
    if args.hint_table:
        hints['table'] = args.hint_table
    if args.hint_batch:
        hints['batch_id'] = args.hint_batch
    if args.hint_database:
        hints['database'] = args.hint_database
    if args.operation:
        hints['expected_operation'] = args.operation
    
    # Parse time range hints
    if args.hint_time_start and args.hint_time_end:
        try:
            # Parse start time
            if len(args.hint_time_start) == 10:  # YYYY-MM-DD
                start_time = datetime.strptime(args.hint_time_start, "%Y-%m-%d")
            else:  # YYYY-MM-DD HH:MM:SS
                start_time = datetime.strptime(args.hint_time_start, "%Y-%m-%d %H:%M:%S")
            
            # Parse end time
            if len(args.hint_time_end) == 10:  # YYYY-MM-DD
                end_time = datetime.strptime(args.hint_time_end, "%Y-%m-%d")
                # Set to end of day if only date provided
                end_time = end_time.replace(hour=23, minute=59, second=59)
            else:  # YYYY-MM-DD HH:MM:SS
                end_time = datetime.strptime(args.hint_time_end, "%Y-%m-%d %H:%M:%S")
            
            hints['time_start'] = start_time
            hints['time_end'] = end_time
        except ValueError as e:
            print(f"Error parsing time range: {e}", file=sys.stderr)
            return 1
    elif args.hint_time_start or args.hint_time_end:
        print("Error: Both --hint-time-start and --hint-time-end must be provided together", file=sys.stderr)
        return 1
    
    # Run verification
    return asyncio.run(verify_with_sdk(
        organization=organization,
        network=args.network,
        transaction_data=transaction_data,
        hints=hints,
        json_output=args.json,
        quiet=args.quiet,
        use_contract=args.use_contract
    ))


async def verify_with_sdk(
    organization: str,
    network: str,
    transaction_data: Dict[str, Any],
    hints: Optional[Dict[str, Any]] = None,
    json_output: bool = False,
    quiet: bool = False,
    use_contract: bool = False
) -> int:
    """Perform verification using the SDK."""
    # Initialize client
    client = ETRAPClient(
        organization_id=organization,
        network=network,
        s3_config=S3Config(region="us-west-2")
    )
    
    try:
        # Verify transaction
        result = await verify_transaction(client, transaction_data, hints, use_contract)
        
        if json_output:
            # JSON output
            print(json.dumps(result, indent=2, default=str))
        else:
            # Human-readable output
            print_verification_result(
                verified=result['verified'],
                transaction_data=transaction_data,
                result=result,
                organization=organization,
                network=network,
                quiet=quiet
            )
        
        # Return appropriate exit code
        return 0 if result['verified'] else 1
        
    except Exception as e:
        if json_output:
            error_result = {
                'verified': False,
                'error': str(e)
            }
            print(json.dumps(error_result, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())