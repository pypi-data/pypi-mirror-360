# ETRAP SDK Examples

This directory contains example scripts demonstrating how to use the ETRAP SDK for various transaction verification and audit trail operations.

## Batch Data Structure

The `batch-multi.json` file shows the complete structure of an ETRAP batch containing multiple transactions. This demonstrates:

- **Batch metadata**: Organization, database, timestamp information
- **Transaction records**: Individual transaction data with hashes and Merkle leaf positions  
- **Merkle tree**: Complete cryptographic proof structure for verification
- **Search indices**: Optimized lookups by timestamp, operation type, and date
- **Compliance data**: Rules, classifications, and retention policies
- **Verification anchoring**: Blockchain transaction details and signatures

This structure represents what gets stored in S3 for detailed batch verification.

## Examples Overview

### Basic Examples

- **basic_usage.py** - Self-contained demonstration of core ETRAP SDK functionality. Shows client initialization, transaction verification, and optimization hints using real blockchain data.
- **debug_batch.py** - Debugging tool for inspecting ETRAP batch metadata stored on NEAR blockchain. Retrieves raw NFT data and displays batch information including S3 locations and Merkle roots.
- **data_models.py** - Demonstrates the data structures and models used by the ETRAP SDK. Shows how to create and work with BatchInfo, filters, search criteria, and other SDK data models.
- **hash_computation.py** - Transaction hash computation and debugging tool. Shows how the SDK normalizes transaction data and computes hashes, useful for troubleshooting verification failures and understanding hash calculation differences.
- **analyze_batch_structure.py** - Analyzes ETRAP batch data structure using batch-multi.json. Shows how multi-transaction batches are organized, Merkle tree structure, and cryptographic verification process.
- **list_batches.py** - List recent batches from the blockchain

### Verification Tools

- **etrap_verify_sdk.py** - Production-ready transaction verification tool (drop-in replacement for etrap_sdk_demo.py)
- **sdk_demo.py** - Comprehensive SDK demonstration tool showcasing all SDK capabilities

## SDK Demo Tool (sdk_demo.py)

The `sdk_demo.py` script is a comprehensive demonstration tool that showcases all capabilities of the ETRAP SDK. It's designed for learning, exploration, and debugging. For production transaction verification, use `etrap_verify_sdk.py` instead.

**When to use which tool:**
- **`etrap_verify_sdk.py`** - For production transaction verification, automation, and as a drop-in replacement for the original etrap_sdk_demo.py
- **`sdk_demo.py`** - For learning the SDK, exploring blockchain data, debugging issues, and testing SDK features

### Features

- **Transaction Verification** - Verify individual transactions against blockchain records
- **Batch Management** - List, search, and analyze batches
- **Transaction Search** - Find transactions by hash across multiple batches
- **Contract Statistics** - View usage statistics and contract information
- **Transaction History** - Query historical transaction data with filters
- **Multiple Output Formats** - Human-readable or JSON output

### Installation

Make sure you have the ETRAP SDK installed:

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

### Basic Usage

```bash
# Verify a transaction
uv run examples/sdk_demo.py --organization lunaris verify  --data '{"id": 132, "account_id": "ACC7777", "amount": 1007.07, "type": "D", "created_at": "2025-06-26 12:47:07", "reference": "BATCH-TEST-77"}'

# Search for a transaction by hash
python sdk_demo.py search --hash abc123...

# List recent batches
python sdk_demo.py list-batches --limit 10

# Get contract statistics
python sdk_demo.py stats --period 24h
```

### Command Reference

#### Global Options

- `-o, --organization` - Organization ID (default: acme)
- `-n, --network` - NEAR network: testnet, mainnet, or localnet (default: testnet)
- `--json` - Output results in JSON format instead of human-readable format

#### verify - Verify a Transaction

Verifies a single transaction against blockchain records.

```bash
python sdk_demo.py verify --data '<JSON_DATA>' [OPTIONS]
```

**Options:**
- `--data` (required) - Transaction data as JSON string
- `--batch-id` - Specific batch ID to check (optimization hint)
- `--table` - Table name hint for faster verification

**Example:**

```bash
# Verify a financial transaction
python sdk_demo.py verify --data '{
  "id": 109,
  "account_id": "ACC999",
  "amount": 999.99,
  "type": "C",
  "created_at": "2025-06-14 07:10:55.461133",
  "reference": "TEST-VERIFY"
}'

# Output:
🔐 ETRAP Transaction Verification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Organization: acme
   Contract: acme.testnet
   Network: testnet

📊 Transaction Summary:
   ID: 109 | Account: ACC999 | Amount: $999.99 | Type: C
   Hash: 147236710593a5eb2f386b7fa1508bf5...

✅ TRANSACTION VERIFIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Batch ID: BATCH-2025-06-14-978b1710
   Blockchain Time: 2025-06-14 00:10:55.463000
   Merkle Root: 147236710593a5eb2f386b7fa1508bf5...
   Database: etrapdb
   Table(s): financial_transactions
```

**JSON Output:**

```bash
python sdk_demo.py --json verify --data '{"id": 109, ...}'

# Output:
{
  "verified": true,
  "transaction_hash": "147236710593a5eb2f386b7fa1508bf5...",
  "batch_id": "BATCH-2025-06-14-978b1710",
  "blockchain_timestamp": "2025-06-14 00:10:55.463000",
  "merkle_proof": {
    "leaf_hash": "147236710593a5eb2f386b7fa1508bf5...",
    "proof_path": [],
    "root": "147236710593a5eb2f386b7fa1508bf5...",
    "valid": true
  },
  "batch_info": {
    "database": "etrapdb",
    "tables": ["financial_transactions"],
    "transaction_count": 1,
    "timestamp": "2025-06-14 00:10:55.463000"
  }
}
```

#### search - Search by Transaction Hash

Find a transaction by its hash across recent batches.

```bash
python sdk_demo.py search --hash <TRANSACTION_HASH> [OPTIONS]
```

**Options:**
- `--hash` (required) - Transaction hash to search for
- `--depth` - Number of batches to search (default: 500)

**Example:**

```bash
python sdk_demo.py search --hash 147236710593a5eb2f386b7fa1508bf5...

# Output:
🔍 Searching for transaction: 147236710593a5eb2f386b7fa1508bf5...
✓ Found in batch: BATCH-2025-06-14-978b1710
  Position: 0
  Merkle proof: 0 nodes
  Root: 147236710593a5eb2f386b7fa1508bf5...
```

#### list-batches - List Recent Batches

Display recent batches with optional filtering.

```bash
python sdk_demo.py list-batches [OPTIONS]
```

**Options:**
- `--limit` - Number of batches to show (default: 20)
- `--database` - Filter by database name
- `--table` - Filter by table name
- `--start-date` - Start date filter (YYYY-MM-DD)
- `--end-date` - End date filter (YYYY-MM-DD)

**Example:**

```bash
python sdk_demo.py list-batches --limit 5 --database etrapdb

# Output:
📦 Recent Batches (showing 5 of 27)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Batch ID                       Time                 DB        Txns  Size
────────────────────────────────────────────────────────────────────────
BATCH-2025-06-14-978b1710      2025-06-14 00:10:55  etrapdb   1     1.9KB
BATCH-2025-06-14-d86e6e52      2025-06-14 00:01:29  etrapdb   1     1.9KB
BATCH-2025-06-14-5da8b7f9      2025-06-13 23:54:27  etrapdb   1     1.9KB
```

#### analyze-batch - Analyze a Specific Batch

Get detailed information about a batch including Merkle tree and S3 data.

```bash
python sdk_demo.py analyze-batch --batch-id <BATCH_ID>
```

**Options:**
- `--batch-id` (required) - Batch ID to analyze

**Example:**

```bash
python sdk_demo.py analyze-batch --batch-id BATCH-2025-06-14-978b1710

# Output:
🔬 Analyzing batch: BATCH-2025-06-14-978b1710
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Batch Information:
   Database: etrapdb
   Tables: financial_transactions
   Transactions: 1
   Timestamp: 2025-06-14 00:10:55.463000
   Merkle Root: 147236710593a5eb2f386b7fa1508bf5...
   S3 Location: s3://etrap-acme/etrapdb/financial_transactions/BATCH-2025-06-14-978b1710/

🌳 Merkle Tree:
   Algorithm: sha256
   Height: 1
   Root: 147236710593a5eb2f386b7fa1508bf5...

📑 Indices Available:
   By timestamp: 1 entries
   By operation: INSERT
   By date: 1 dates
```

#### get-nft - Get NFT Metadata and Blockchain Details

Get comprehensive NFT information for ETRAP batch tokens. Each batch in ETRAP creates a unique NFT on the blockchain that represents ownership of the audit record.

```bash
python sdk_demo.py get-nft --token-id <TOKEN_ID>
```

**Options:**
- `--token-id` (required) - NFT token ID (same as batch ID)

**Example:**

```bash
python sdk_demo.py get-nft --token-id BATCH-2025-07-01-c9de5968

# Output:
🎨 NFT Information: BATCH-2025-07-01-c9de5968
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Basic Information:
   Token ID: BATCH-2025-07-01-c9de5968
   Owner: lunaris.testnet
   Minted: 2025-07-01 09:55:10.475000
   Organization: lunaris

🏷️  Metadata:
   Title: ETRAP Batch BATCH-2025-07-01-c9de5968
   Description: Integrity certificate for 4 transactions from table financial_transactions
   Reference: https://s3.amazonaws.com/etrap-lunaris/BATCH-2025-07-01-c9de5968/batch-data.json

⛓️  Blockchain Details:
   Contract: lunaris.testnet
   Network: testnet
   Standard: NEP-171
   Merkle Root: b1e52265e4fd5afaf673454fe7351cbc516bea056c08f99e3d0876217b0aacab
```

**JSON Output:**

```bash
python sdk_demo.py --json get-nft --token-id BATCH-2025-07-01-c9de5968

# Output:
{
  "token_id": "BATCH-2025-07-01-c9de5968",
  "owner_id": "lunaris.testnet",
  "metadata": {
    "title": "ETRAP Batch BATCH-2025-07-01-c9de5968",
    "description": "Integrity certificate for 4 transactions from table financial_transactions",
    "reference": "https://s3.amazonaws.com/etrap-lunaris/BATCH-2025-07-01-c9de5968/batch-data.json",
    "issued_at": "1751388910475",
    "copies": 1
  },
  "minted_timestamp": "2025-07-01T09:55:10.475000",
  "batch_id": "BATCH-2025-07-01-c9de5968",
  "organization_id": "lunaris",
  "merkle_root": "b1e52265e4fd5afaf673454fe7351cbc516bea056c08f99e3d0876217b0aacab",
  "blockchain_details": {
    "contract_id": "lunaris.testnet",
    "network": "testnet",
    "token_standard": "NEP-171",
    "approved_account_ids": {}
  }
}
```

**Key Features:**
- **NEP-171 Compliant**: Full NEAR NFT standard compliance
- **Ownership Information**: Current owner and approved accounts
- **Rich Metadata**: Title, description, and S3 reference for audit data
- **Blockchain Asset Data**: Contract details and minting information
- **Cryptographic Integrity**: Merkle root for transaction verification

**Use Cases:**
- **Asset Ownership**: Determine who owns the audit record NFT
- **Compliance Documentation**: Generate certificates of audit record ownership
- **Blockchain Integration**: Access NFT data for marketplace or transfer operations
- **Audit Trail**: Link blockchain assets to audit records

#### stats - Get Contract Statistics

View contract usage statistics for different time periods.

```bash
python sdk_demo.py stats [OPTIONS]
```

**Options:**
- `--period` - Time period: 1h, 24h, 7d, 30d, or all (default: 24h)

**Example:**

```bash
python sdk_demo.py stats --period 7d

# Output:
📊 Contract Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Overall Statistics:
   Contract: acme.testnet
   Total Batches: 27
   Total Transactions: 57
   Date Range: 2024-12-12 to 2025-06-14
   Databases: etrapdb, test_db, unknown
   Tables: 4 unique tables

📊 Period Statistics (7d):
   Batches Created: 26
   Transactions: 53
   Active Tables: 3
   Active Databases: 2
```

#### search-batches - Search Batches

Search for batches using various criteria.

```bash
python sdk_demo.py search-batches [OPTIONS]
```

**Options:**
- `--tx-hash` - Transaction hash to find
- `--merkle-root` - Merkle root to find
- `--start-date` - Start date (YYYY-MM-DD)
- `--end-date` - End date (YYYY-MM-DD)
- `--max-results` - Maximum results (default: 100)

**Example:**

```bash
python sdk_demo.py search-batches --start-date 2025-06-13 --end-date 2025-06-14

# Output:
🔍 Searching Batches
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Found 10 batches in 890ms

Matching Batches:
 1. BATCH-2025-06-14-978b1710 - 2025-06-14 00:10:55 (1 txns)
 2. BATCH-2025-06-14-d86e6e52 - 2025-06-14 00:01:29 (1 txns)
 3. BATCH-2025-06-14-5da8b7f9 - 2025-06-13 23:54:27 (1 txns)
    ... and 7 more
```

#### history - Get Transaction History

Query historical transaction data with filters.

```bash
python sdk_demo.py history [OPTIONS]
```

**Options:**
- `--operations` - Filter by operation types: INSERT, UPDATE, DELETE
- `--start-time` - Start time (ISO format)
- `--end-time` - End time (ISO format)
- `--limit` - Maximum results (default: 100)

**Example:**

```bash
python sdk_demo.py history --operations INSERT --limit 10

# Output:
📜 Transaction History
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Found 10 transactions
Time range: 2025-06-13 22:03:09 to 2025-06-14 00:10:55

Recent Transactions:
Time                 Operation  Table                    Hash
──────────────────────────────────────────────────────────────────
2025-06-14 00:10:55  INSERT     financial_transactions   147236710593a5eb...
2025-06-14 00:01:29  INSERT     financial_transactions   ba5ba542b41eaa22...
2025-06-13 23:54:27  INSERT     financial_transactions   4d1c3c7d0db0e74d...
```

### Advanced Usage Examples

#### Verify with Optimization Hints

Speed up verification by providing hints:

```bash
# If you know the batch ID
python sdk_demo.py verify --data '{"id": 123, ...}' --batch-id BATCH-2025-06-14-978b1710

# If you know the table name
python sdk_demo.py verify --data '{"id": 123, ...}' --table financial_transactions
```

#### Time Range Search Optimization

The ETRAP Verify SDK tool supports time range hints for efficient verification when you know the approximate time when a transaction was recorded:

```bash
# Search within a specific day
./etrap_verify_sdk.py -o acme --data '{"id": 109, ...}' \
  --hint-time-start 2025-06-14 \
  --hint-time-end 2025-06-14

# Search within specific hours 
./etrap_verify_sdk.py -o acme --data '{"id": 109, ...}' \
  --hint-time-start "2025-06-14 06:00:00" \
  --hint-time-end "2025-06-14 08:00:00"

# Combine time range with database hint for maximum efficiency
./etrap_verify_sdk.py -o acme --data '{"id": 109, ...}' \
  --hint-time-start 2025-06-14 \
  --hint-time-end 2025-06-14 \
  --hint-database etrapdb

# Multi-day range search
./etrap_verify_sdk.py -o acme --data '{"id": 109, ...}' \
  --hint-time-start "2025-06-13 00:00:00" \
  --hint-time-end "2025-06-15 23:59:59"
```

**Time Format Options:**
- **Date only**: `YYYY-MM-DD` (automatically extends end time to 23:59:59)
- **Full timestamp**: `YYYY-MM-DD HH:MM:SS` for precise time ranges

**Performance Benefits:**
- Uses smart contract's `get_batches_by_time_range()` method
- Searches only batches within the specified time range
- Can reduce search from hundreds of batches to just a few
- Combines efficiently with database and table hints

**Example Output with Time Range:**
```bash
./etrap_verify_sdk.py -o acme --data '{"id": 109, ...}' \
  --hint-time-start 2025-06-14 --hint-time-end 2025-06-14

🔐 ETRAP Transaction Verification Tool
   Contract: acme.testnet
   Network: testnet

📊 Transaction Hash: 147236710593a5eb2f386b7fa1508bf563a11b73b3d580219db2b59c2e135fc8

🔎 Searching recent batches...
   Found 29 recent batches to check
   Found in batch 3 of 29

✅ TRANSACTION VERIFIED
```

**Hint Priority Order:**
1. **Batch hint** (`--hint-batch`) - Most specific, direct lookup
2. **Time range hint** (`--hint-time-start` + `--hint-time-end`) - Time-based search
3. **Database hint** (`--hint-database`) - Database-specific search  
4. **Table hint** (`--hint-table`) - Table-specific search
5. **No hints** - Searches recent batches sequentially

#### Filter Batches by Date Range

```bash
python sdk_demo.py list-batches \
  --start-date 2025-06-01 \
  --end-date 2025-06-14 \
  --database etrapdb \
  --limit 50
```

#### Search for Specific Transaction Types

```bash
python sdk_demo.py history \
  --operations INSERT UPDATE \
  --start-time "2025-06-13T00:00:00" \
  --end-time "2025-06-14T23:59:59" \
  --limit 100
```

#### Export Results as JSON

All commands support JSON output for programmatic use:

```bash
# Verify and get JSON result
python sdk_demo.py --json verify --data '{"id": 123, ...}' > verification_result.json

# List batches as JSON
python sdk_demo.py --json list-batches --limit 100 > batches.json

# Get stats as JSON
python sdk_demo.py --json stats --period all > contract_stats.json
```

### Error Handling

The tool provides clear error messages:

- **Transaction Not Found**: Returns exit code 1
- **Network Errors**: Shows connection issues
- **Invalid Data**: Reports JSON parsing errors
- **S3 Access Issues**: Indicates when batch data is not available

### Integration Examples

#### Bash Script Integration

```bash
#!/bin/bash
# Verify a transaction and check result

TX_DATA='{"id": 123, "amount": 100.50, ...}'

if python sdk_demo.py --json verify --data "$TX_DATA" > result.json; then
    echo "Transaction verified!"
    BATCH_ID=$(jq -r '.batch_id' result.json)
    echo "Found in batch: $BATCH_ID"
else
    echo "Verification failed!"
    exit 1
fi
```

#### Python Integration

```python
import subprocess
import json

# Run verification
result = subprocess.run([
    'python', 'sdk_demo.py', '--json', 'verify',
    '--data', json.dumps(transaction_data)
], capture_output=True, text=True)

if result.returncode == 0:
    verification = json.loads(result.stdout)
    print(f"Verified: {verification['verified']}")
    print(f"Batch: {verification['batch_id']}")
```

### Performance Tips

1. **Use Hints**: Provide batch ID or table name hints when available
2. **Limit Search Depth**: Use reasonable limits for batch searches
3. **Cache Results**: The SDK caches data for 5 minutes by default
4. **Batch Operations**: Use the SDK directly for bulk verifications

### Troubleshooting

**"Transaction not found"**
- Ensure the transaction data matches exactly what was recorded
- Check if the batch has been created (may take a few seconds)
- Increase search depth with `--depth` parameter

**"S3 Access Error"**
- Verify AWS credentials are configured
- Check if the batch data has been uploaded by the CDC agent
- The tool can still verify using blockchain data only

**"Contract Error"**
- Ensure the organization ID is correct
- Verify the NEAR network (testnet/mainnet) matches your setup
- Check if the contract is deployed and accessible

### SDK Methods Demonstrated

The sdk_demo.py tool showcases all major SDK capabilities:

- `verify_transaction()` - Core verification with Merkle proofs
- `find_transaction()` - Search by transaction hash
- `list_batches()` - List and filter batches
- `get_batch()` & `get_batch_data()` - Access batch information
- `search_batches()` - Advanced batch search
- `get_transaction_history()` - Query historical data
- `get_contract_info()` & `get_contract_stats()` - Contract analytics
- `compute_transaction_hash()` - Hash computation
- `get_merkle_proof()` - Merkle proof retrieval

## ETRAP Verify SDK Tool (etrap_verify_sdk.py)

A complete clone of the original `etrap_sdk_demo.py` tool that uses the ETRAP SDK for all operations. This tool provides identical functionality with a cleaner interface using organization IDs instead of contract IDs.

### Key Differences from Original

- Uses `-o/--organization` instead of `-c/--contract` (though `--contract` is supported for backward compatibility)
- Automatically derives the contract ID from organization ID and network
- Leverages the SDK for all verification operations

### Usage

```bash
# Verify a transaction from JSON string
./etrap_verify_sdk.py -o acme --data '{"id":123,"account_id":"ACC500","amount":10000}'

# Verify from a file
./etrap_verify_sdk.py -o acme --data-file transaction.json

# Verify from stdin
echo '{"id":123,...}' | ./etrap_verify_sdk.py -o acme --data -

# Provide hints for faster search
./etrap_verify_sdk.py -o acme --data-file tx.json --hint-table financial_transactions
./etrap_verify_sdk.py -o acme --data-file tx.json --hint-batch BATCH-2025-06-14-abc123
./etrap_verify_sdk.py -o acme --data-file tx.json --hint-database production
./etrap_verify_sdk.py -o acme --data-file tx.json --hint-time-start 2025-06-14 --hint-time-end 2025-06-14

# JSON output
./etrap_verify_sdk.py -o acme --data '{...}' --json

# Quiet mode (minimal output)
./etrap_verify_sdk.py -o acme --data '{...}' --quiet

# Use smart contract verification
./etrap_verify_sdk.py -o acme --data-file tx.json --use-contract
```

### Command-Line Options

- `-o, --organization` - Organization ID (e.g., 'acme')
- `-c, --contract` - NEAR contract ID (deprecated, use --organization)
- `--data` - Transaction data as JSON string (use "-" for stdin)
- `--data-file` - Path to file containing transaction JSON
- `--hint-table` - Table name hint for faster search
- `--hint-batch` - Specific batch ID to check
- `--hint-database` - Database name hint
- `--hint-time-start` - Start time for time range search (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `--hint-time-end` - End time for time range search (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `-n, --network` - NEAR network: testnet, mainnet, or localnet (default: testnet)
- `--json` - Output result as JSON
- `-q, --quiet` - Minimal output (just verification status)
- `--use-contract` - Use smart contract for verification instead of local verification


### Use contract vs. local verification with data from S3
Comparison:

  - Local verification (default): Downloads data from S3, verifies locally
  - Smart contract verification (--use-contract): Calls view function on RPC node at cost zero gas

  Both are free, but smart contract verification provides stronger assurance that the verification logic
  matches exactly what's deployed on-chain.

### Output Formats

#### Standard Output

```
🔐 ETRAP Transaction Verification Tool
   Contract: acme.testnet
   Network: testnet

🔍 ETRAP Transaction Verification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Transaction Hash: 8684c656d2addf8a0c5040ba3863c0fb...
💻 Verification Method: Local (off-chain)

✅ TRANSACTION VERIFIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Transaction Details:
   Hash: 8684c656d2addf8a0c5040ba3863c0fb...
   Database: production
   Table: financial_transactions

🔗 Blockchain Record:
   NFT Token ID: BATCH-2025-06-14-abc123
   Contract: acme.testnet
   Network: testnet
   Merkle Root: def456...

⏰ Recorded on Blockchain:
   2025-06-14 12:34:56 UTC
   This is the official timestamp when this batch was
   permanently recorded on the NEAR blockchain.
```

When using `--use-contract`, the verification method shows:
```
🔗 Verification Method: Smart Contract (on-chain)
```

#### JSON Output

```json
{
  "verified": true,
  "transaction_hash": "8684c656d2addf8a0c5040ba3863c0fb...",
  "batch_id": "BATCH-2025-06-14-abc123",
  "blockchain_timestamp": "2025-06-14 12:34:56",
  "error": null,
  "search_info": {
    "total_batches": 29,
    "batch_position": 3,
    "direct_lookup": false
  },
  "verification_method": "local",
  "merkle_proof": {
    "leaf_hash": "8684c656d2addf8a0c5040ba3863c0fb...",
    "proof_path": [...],
    "sibling_positions": ["left", "right"],
    "merkle_root": "def456...",
    "is_valid": true
  },
  "batch_info": {
    "database": "production",
    "tables": ["financial_transactions"],
    "transaction_count": 100,
    "timestamp": "2025-06-14 12:34:56"
  },
  "operation_type": "INSERT",
  "position": 0
}
```

#### Quiet Mode Output

```
✓ VERIFIED
```

or

```
✗ NOT VERIFIED
```

### Exit Codes

- `0` - Transaction verified successfully
- `1` - Verification failed or error occurred

### Verification Methods

The tool supports two verification methods:

1. **Local Verification (default)**: 
   - Downloads merkle proof data from S3
   - Verifies the proof locally against the blockchain's merkle root
   - Faster and more efficient
   - Shown as: `💻 Verification Method: Local (off-chain)`

2. **Smart Contract Verification** (with `--use-contract`):
   - Calls the NEAR smart contract's `verify_document_in_batch` method
   - Performs verification entirely on-chain
   - Provides stronger guarantee but slower
   - Shown as: `🔗 Verification Method: Smart Contract (on-chain)`

Example using smart contract verification:
```bash
# Basic smart contract verification
./etrap_verify_sdk.py -o acme --data-file tx.json --use-contract

# With batch hint for direct lookup
./etrap_verify_sdk.py -o acme --data-file tx.json --hint-batch BATCH-2025-06-14-abc123 --use-contract

# JSON output shows verification method
./etrap_verify_sdk.py -o acme --data-file tx.json --use-contract --json | jq .verification_method
# Output: "smart_contract"
```

### Migration from etrap_sdk_demo.py

To migrate from the original tool:

1. Replace `-c contract.testnet` with `-o organization`
2. All other options remain the same
3. The tool will automatically derive the correct contract ID

Example migration:
```bash
# Old:
etrap_sdk_demo.py -c acme.testnet --data '{...}'

# New:
etrap_verify_sdk.py -o acme --data '{...}'
```

## Other Examples

### basic_usage.py

Simple transaction verification:

```python
result = await client.verify_transaction({
    "id": 109,
    "account_id": "ACC999",
    "amount": 999.99,
    "type": "C",
    "created_at": "2025-06-14 07:10:55.461133"
})
```

### list_batches.py

List recent batches with filtering:

```python
batch_list = await client.list_batches(
    filter=BatchFilter(database_name="etrapdb"),
    limit=10
)
```

### debug_batch.py

Debug batch metadata:

```bash
python debug_batch.py BATCH-2025-06-14-978b1710
```

### hash_computation.py

Transaction hash computation and debugging tool. Shows how the SDK normalizes transaction data and computes hashes:

```bash
# Use with custom transaction data
uv run examples/hash_computation.py '{"id": 144, "account_id": "TEST555", "amount": "55555.55", "type": "C", "created_at": "2025-06-28 17:48:09.243538", "reference": "Test DEFAULT identity"}'

# Use with default example data  
uv run examples/hash_computation.py
```

### analyze_batch_structure.py

Analyzes ETRAP batch data structure and shows how multi-transaction verification works:

```bash
# Analyze the example multi-transaction batch
uv run examples/analyze_batch_structure.py

# Analyze a custom batch file
uv run examples/analyze_batch_structure.py path/to/batch-data.json
```

## Debugging and Troubleshooting

### Enable Debug Logging

To see detailed SDK operations and troubleshoot issues, enable debug logging:

```python
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable debug logging for ETRAP SDK
logging.getLogger('etrap_sdk').setLevel(logging.DEBUG)
```

This will show:
- Contract calls and responses
- S3 access attempts and results
- Merkle proof verification steps
- Search optimization decisions
- Cache hits and misses

The `basic_usage.py` example includes commented logging setup that can be uncommented for debugging.

## Requirements

- Python 3.8+
- ETRAP SDK installed
- NEAR account access (for blockchain queries)
- AWS credentials (optional, for S3 access)

## Troubleshooting Transaction Verification Issues

### Investigating Failed Verifications

When a transaction verification fails unexpectedly, follow these steps to diagnose the issue:

#### Step 1: Verify the Transaction Hash Calculation

First, check that the transaction hash is being calculated correctly:

```bash
# Use the hash_computation.py tool to see the computed hash
python hash_computation.py '{"id":109,"account_id":"ACC999","amount":"999.99","type":"C","created_at":"2025-06-14T07:10:55.461133","reference":"TEST-VERIFY"}'

# Output shows:
# - Original transaction data types
# - Normalized transaction (what gets hashed)
# - Hash with normalization
# - Hash without normalization
```

#### Step 2: Check if the Batch Exists

List recent batches to see what's actually on the blockchain:

```bash
# List recent batches
python list_batches.py -o acme

# Look for the batch you're trying to verify
# Note the Merkle root - for single-transaction batches, this equals the transaction hash
```

#### Step 3: Compare with Original Tool

If you have access to the original `etrap_sdk_demo.py`, compare results:

```bash
# Original tool
python3 /path/to/etrap_sdk_demo.py -c acme.testnet --data '{"id":109,...}'

# SDK tool
python etrap_verify_sdk.py -o acme --data '{"id":109,...}'

# Compare the computed hashes - they should match
```

#### Step 4: Debug Batch Contents

Use the debug tool to inspect batch metadata:

```bash
python debug_batch.py BATCH-2025-06-14-978b1710

# This shows:
# - Raw NFT data from contract
# - Parsed batch information
# - S3 location details
```

#### Step 5: Common Issues and Solutions

##### Issue: Different Hash Calculations

**Symptom**: SDK calculates a different hash than the original tool

**Cause**: Normalization differences, especially with numeric fields

**Solution**: Check the normalization logic in `src/etrap_sdk/utils.py`:
- The SDK should NOT convert `id` fields to strings (keep as integers)
- Only monetary fields (`amount`, `balance`, etc.) should be normalized to strings
- Timestamps should be normalized to ISO format with milliseconds

**Example Fix**:
```python
# WRONG - converts id to string
for field in ['id', 'amount', 'balance', 'count']:
    if field in normalized and isinstance(normalized[field], (int, float)):
        normalized[field] = str(normalized[field])

# CORRECT - keeps id as integer
for field in ['amount', 'balance', 'total', 'price', 'cost', 'value']:
    if field in normalized and isinstance(normalized[field], (int, float)):
        normalized[field] = str(normalized[field])
```

##### Issue: Transaction Not Found in Batch

**Symptom**: "Transaction not found in specified batch"

**Cause**: The transaction hash doesn't match what's in the batch

**Solution**: 
1. Check the batch's Merkle root (for single-tx batches, this IS the transaction hash)
2. Verify your transaction data exactly matches what was recorded
3. Pay attention to timestamp precision and format

##### Issue: Transaction Not Found in Blockchain

**Symptom**: "Transaction not found in blockchain records"

**Cause**: The transaction was never recorded, or search depth is insufficient

**Solution**:
1. Verify the transaction was actually recorded by the CDC agent
2. Try without hints to search all recent batches
3. Increase search depth if needed

#### Step 6: Test Data vs Real Data

Be aware of the difference:
- **Test data**: May not exist on blockchain, used for unit tests
- **Real data**: Actually recorded transactions with valid hashes

To find real transactions for testing:
```bash
# List recent batches and note single-transaction batches
python list_batches.py -o acme

# For single-tx batches, the Merkle root IS the transaction hash
# You need the original transaction data that produces this hash
```

### Example Investigation Walkthrough

Here's a real example of investigating a verification failure:

```bash
# 1. Try to verify - it fails
$ python etrap_verify_sdk.py -o acme --data '{"id":109,...}' --hint-batch BATCH-2025-06-14-978b1710
❌ VERIFICATION FAILED
Error: Transaction not found in specified batch

# 2. Check what hash we're computing
$ python hash_computation.py '{"id":109,...}'
Hash with normalization: 8684c656d2addf8abb8408699d81eeed3576da03254364bc1e9ca614d0eff8ab

# 3. Check what's actually in the batch
$ python list_batches.py -o acme | grep 978b1710
3. Batch ID: BATCH-2025-06-14-978b1710
   Merkle root: 147236710593a5eb2f386b7fa1508bf563a11b73b3d580219db2b59c2e135fc8

# 4. Hashes don't match! Check with original tool
$ python3 /path/to/etrap_sdk_demo.py -c acme.testnet --data '{"id":109,...}'
📊 Transaction Hash: 147236710593a5eb2f386b7fa1508bf5...
✅ TRANSACTION VERIFIED

# 5. Original tool gets different hash - normalization issue!
# Fix: Update SDK normalization to match original behavior
# (Don't convert 'id' field to string)

# 6. After fix, verify it works
$ python etrap_verify_sdk.py -o acme --data '{"id":109,...}'
📊 Transaction Hash: 147236710593a5eb2f386b7fa1508bf563a11b73b3d580219db2b59c2e135fc8
✅ TRANSACTION VERIFIED
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## 🪪 License

MIT. See `./LICENSE`


## 📄 Copyright

Copyright (c) 2025 Graziano Labs Corp. All rights reserved.


## 📧 Contact

For questions or support, please open an issue in the GitHub repository.

---