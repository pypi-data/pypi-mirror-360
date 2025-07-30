# ETRAP SDK

Python SDK for the Enterprise Transaction Recording and Audit Platform (ETRAP).

## Overview

The ETRAP SDK provides a simple and intuitive interface for:
- Verifying transactions against blockchain records
- Searching and retrieving audit trail data
- Validating Merkle proofs
- Accessing batch information stored on NEAR blockchain
- Retrieving NFT metadata and blockchain asset information

### Organization-Based Architecture

ETRAP uses your organization ID as the primary identifier:
- **Organization ID**: `acme`
- **NEAR Contract**: `acme.testnet` (testnet) or `acme.near` (mainnet)
- **S3 Bucket**: `etrap-acme`

This consistent naming convention ensures all resources are properly linked.

## Installation

### Using uv (Recommended)

```bash
# Add to your project
uv add etrap-sdk

# Or install directly
uv pip install etrap-sdk
```

### Using pip

```bash
pip install etrap-sdk
```

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and packaging.

```bash
# Clone the repository
git clone https://github.com/marcoeg/etrap-sdk.git
cd etrap-sdk

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set Python version (if using pyenv)
pyenv install 3.11
pyenv local 3.11

# Create virtual environment and install dependencies
rm -rf .venv  # Remove existing venv if any
uv sync       # Creates .venv and installs all dependencies
uv pip install -e .  # Install SDK in editable mode

# Run examples (use 'uv run' to automatically use the virtual environment)
cd examples
uv run python list_batches.py
uv run python basic_usage.py

# Or activate the virtual environment manually
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python list_batches.py
deactivate  # When done

# Run tests
uv run pytest

# Type checking
uv run mypy etrap_sdk

# Linting
uv run ruff check .

# Format code
uv run black .

# Build the package
uv build
```

### Managing Dependencies with uv

```bash
# Add a new dependency
uv add requests

# Add a development dependency
uv add --dev pytest-mock

# Update dependencies
uv lock --upgrade

# Install from lock file
uv sync

# Run any Python command with uv (automatically uses virtual environment)
uv run python your_script.py
uv run pytest
uv run mypy etrap_sdk
```

### Important: Using the Virtual Environment

When working with the ETRAP SDK, always ensure you're using the correct Python environment:

**Option 1: Use `uv run` (Recommended)**
```bash
# This automatically uses the virtual environment
uv run python examples/list_batches.py
```

**Option 2: Activate the virtual environment**
```bash
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate     # On Windows

python examples/list_batches.py
deactivate  # When done
```

**Option 3: Use the virtual environment Python directly**
```bash
.venv/bin/python examples/list_batches.py
```

**Common Issue**: If you get `ModuleNotFoundError: No module named 'etrap_sdk'`, you're likely using the global Python instead of the virtual environment Python.

## Environment Variables

The SDK primarily uses environment variables for AWS credentials. See `.env.example` for a complete reference.

### AWS Credentials for S3 Access

The SDK uses boto3, which automatically reads AWS credentials from:

1. Environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-west-2
   ```

2. AWS credentials file (`~/.aws/credentials`)

3. IAM role (when running on AWS infrastructure)

### Configuration Notes

- **NEAR_ENV is NOT used** - The SDK requires you to specify the network explicitly in the ETRAPClient constructor
- **ETRAP_SDK_LOG_LEVEL is NOT used** - Configure logging using Python's standard logging module
- **Organization settings** - Must be passed to ETRAPClient constructor (not read from environment)
- **Logging configuration** - Use Python's standard logging module in your application:
  ```python
  import logging
  logging.getLogger('etrap_sdk').setLevel(logging.DEBUG)
  ```

### Using .env Files

For development, you can use a `.env` file:

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
vim .env

# Load in your application (requires python-dotenv)
from dotenv import load_dotenv
load_dotenv()
```

## Quick Start

```python
import asyncio
from etrap_sdk import ETRAPClient, S3Config

async def verify_transaction():
    # Initialize client
    client = ETRAPClient(
        organization_id="acme",  # Your organization ID
        network="testnet",       # Contract will be "acme.testnet"
        s3_config=S3Config(
            # bucket_name automatically set to "etrap-acme"
            region="us-west-2"
        )
    )

# Verify a transaction
result = await client.verify_transaction({
    "id": 109,
    "account_id": "ACC999",
    "amount": 999.99,
    "type": "C",
    "created_at": "2025-06-14 07:10:55.461133",
    "reference": "TEST-VERIFY"
})

if result.verified:
    print(f" Transaction verified!")
    print(f"   Batch ID: {result.batch_id}")
    print(f"   Blockchain timestamp: {result.blockchain_timestamp}")
else:
    print(f"L Verification failed: {result.error}")
```

## Examples and Tools

### SDK Demo Tool (examples/sdk_demo.py)

The SDK includes a comprehensive demo tool that showcases all major functionality:

```bash
# Run with uv (recommended)
uv run python examples/sdk_demo.py -o <organization> <command> [options]

# Or with activated virtual environment
python examples/sdk_demo.py -o <organization> <command> [options]
```

#### Available Commands

- `verify` - Verify a single transaction
- `search` - Search for transaction by hash
- `list-batches` - List recent batches with filtering
- `analyze-batch` - Analyze specific batch in detail
- `get-nft` - Get NFT metadata and blockchain details
- `stats` - Get contract statistics and usage
- `search-batches` - Search batches by criteria
- `history` - Query transaction history

#### Example Usage

```bash
# Verify a transaction
uv run python examples/sdk_demo.py -o lunaris verify \
  --data '{"id": 144, "account_id": "TEST555", "amount": "55555.55"}'

# Analyze a batch with operation counts
uv run python examples/sdk_demo.py -o lunaris analyze-batch \
  --batch-id BATCH-2025-07-01-c9de5968

# Get NFT information (human-readable)
uv run python examples/sdk_demo.py -o lunaris get-nft \
  --token-id BATCH-2025-07-01-c9de5968

# Get NFT information (JSON output)
uv run python examples/sdk_demo.py -o lunaris --json get-nft \
  --token-id BATCH-2025-07-01-c9de5968

# List recent batches
uv run python examples/sdk_demo.py -o lunaris list-batches --limit 10

# Get contract statistics
uv run python examples/sdk_demo.py -o lunaris stats --period 7d
```

### NFT Information

The `get-nft` command provides comprehensive blockchain asset information:

**Verbose Output:**
```
🎨 NFT Information: BATCH-2025-07-01-c9de5968
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Basic Information:
   Token ID: BATCH-2025-07-01-c9de5968
   Owner: lunaris.testnet
   Minted: 2025-07-01 09:55:10.475000
   Organization: lunaris

🏷️  Metadata:
   Title: ETRAP Batch BATCH-2025-07-01-c9de5968
   Description: Integrity certificate for 4 transactions...
   Reference: https://s3.amazonaws.com/etrap-lunaris/...

⛓️  Blockchain Details:
   Contract: lunaris.testnet
   Network: testnet
   Standard: NEP-171
   Merkle Root: b1e52265e4fd5afaf673454fe7351cbc516bea056c08f99e3d0876217b0aacab
```

**JSON Output:** Complete structured data for programmatic use.

### Other Examples

- `examples/basic_usage.py` - Simple verification example
- `examples/list_batches.py` - Batch listing and filtering
- `examples/etrap_verify_sdk.py` - Production verification tool

## Features

### Transaction Verification

The SDK automatically normalizes transaction data to match the format used by the CDC agent:

```python
# All these formats work:
tx1 = {"amount": 999.99, "created_at": "2025-06-14 07:10:55.461133"}  # DB format
tx2 = {"amount": "999.99", "created_at": "2025-06-14T07:10:55.461"}   # Normalized

# Both will verify successfully
result1 = await client.verify_transaction(tx1)
result2 = await client.verify_transaction(tx2)
```

### Batch Verification

Verify multiple transactions efficiently:

```python
transactions = [
    {"id": 1, "amount": 100.00, ...},
    {"id": 2, "amount": 200.00, ...},
    {"id": 3, "amount": 300.00, ...}
]

results = await client.verify_batch(
    transactions,
    parallel=True,
    progress_callback=lambda current, total: print(f"Progress: {current}/{total}")
)

print(f"Verified: {results.verified}/{results.total}")
print(f"Success rate: {results.summary.success_rate:.1%}")
```

### Optimization Hints

Speed up verification with hints:

```python
from etrap_sdk import VerificationHints

hints = VerificationHints(
    table_name="financial_transactions",
    database_name="production",
    batch_id="BATCH-2025-06-14-abc123"  # If known
)

result = await client.verify_transaction(transaction_data, hints=hints)
```

### Search Capabilities

The SDK provides multiple ways to search for transactions and batches:

#### Search by Transaction Hash

```python
# Find a transaction by its hash
location = await client.find_transaction(
    transaction_hash="147236710593a5eb2f386b7fa1508bf5...",
    search_depth=500,  # Number of recent batches to search
    time_range=TimeRange(
        start=datetime(2025, 6, 1),
        end=datetime(2025, 6, 14)
    )
)

if location:
    print(f"Found in batch: {location.batch_id}")
    print(f"Position: {location.position}")
```

#### Search Batches by Multiple Criteria

```python
from etrap_sdk import SearchCriteria, DateRange

# Search by transaction hash
criteria = SearchCriteria(
    transaction_hash="abc123..."
)

# Search by merkle root
criteria = SearchCriteria(
    merkle_root="def456..."
)

# Search by date range and operation type
criteria = SearchCriteria(
    date_range=DateRange(start="2025-06-01", end="2025-06-14"),
    operation_type="INSERT"  # INSERT, UPDATE, or DELETE
)

# Execute search
results = await client.search_batches(criteria, max_results=100)
print(f"Found {len(results.matching_batches)} batches in {results.search_time_ms}ms")
```

#### List Batches with Filters

```python
from etrap_sdk import BatchFilter, TimeRange

# Filter by multiple criteria
filter = BatchFilter(
    database_name="production",
    table_name="financial_transactions",
    time_range=TimeRange(
        start=datetime(2025, 6, 1),
        end=datetime(2025, 6, 14)
    ),
    min_transactions=10  # Only batches with 10+ transactions
)

# List with pagination and sorting
batch_list = await client.list_batches(
    filter=filter,
    limit=50,
    offset=0,
    order_by="timestamp_desc"  # Options: timestamp_desc, timestamp_asc, size_desc
)

for batch in batch_list.batches:
    print(f"{batch.batch_id}: {batch.transaction_count} transactions")
```

#### Query Transaction History

```python
from etrap_sdk import TransactionFilter

# Search by operation types and time range
filter = TransactionFilter(
    time_range=TimeRange(
        start=datetime(2025, 6, 1),
        end=datetime(2025, 6, 14)
    ),
    operation_types=["INSERT", "UPDATE"],  # Filter by CDC operation types
    account_id="ACC999",  # Would need transaction data access
    min_amount=100.00     # Would need transaction data access
)

history = await client.get_transaction_history(filter, limit=1000)
print(f"Found {history.total_found} transactions")

# Note: Due to privacy-by-design, only transaction metadata is available,
# not the actual transaction data (account_id, amount, etc.)
```

#### Smart Contract Query Methods

The SDK queries the NEAR smart contract for batch information:

```python
# Get recent batches (most efficient)
recent_batches = await client._get_recent_batches(100)

# Get batches by table (if supported by contract)
table_batches = await client._get_batches_by_table("financial_transactions", 50)

# Direct NFT token query
batch = await client.get_batch("BATCH-2025-06-14-abc123")
```

### Batch Information

Get information about specific batches:

```python
batch = await client.get_batch("BATCH-2025-06-14-abc123")
print(f"Database: {batch.database_name}")
print(f"Tables: {batch.table_names}")
print(f"Transaction count: {batch.transaction_count}")
print(f"Merkle root: {batch.merkle_root}")
```

## CDC Agent Integration

The SDK provides public API methods specifically designed for the ETRAP CDC Agent to ensure consistent transaction processing:

### Transaction Processing API

These methods are used by the CDC Agent to ensure that transaction recording and verification use identical logic:

```python
# Initialize client
client = ETRAPClient(organization_id="acme", network="testnet")

# Prepare transaction data for storage (normalizes data)
prepared_data = client.prepare_transaction_for_storage(transaction_data)

# Compute deterministic hash (same algorithm as CDC Agent)
tx_hash = client.compute_transaction_hash(transaction_data)
```

This integration ensures:
- **Consistency**: Recording and verification use identical normalization and hashing
- **Maintainability**: Single source of truth for transaction processing logic
- **Compatibility**: Seamless integration between CDC Agent and SDK

## Data Normalization

The SDK automatically handles different data formats:

| Field Type | Database Format | Normalized Format |
|------------|----------------|-------------------|
| Amounts | `999.99` (number) | `"999.99"` (string) |
| Timestamps | `2025-06-14 07:10:55` | `2025-06-14T07:10:55` |
| Precision | `.461133` (6 decimals) | `.461` (3 decimals) |

## Error Handling

```python
from etrap_sdk import ETRAPError, VerificationError, BatchNotFoundError

try:
    result = await client.verify_transaction(tx_data)
except VerificationError as e:
    print(f"Verification failed: {e}")
    print(f"Transaction hash: {e.transaction_hash}")
except BatchNotFoundError as e:
    print(f"Batch not found: {e.batch_id}")
except ETRAPError as e:
    print(f"ETRAP error: {e}")
```

## Configuration

```python
# Update configuration
client.update_config({
    "cache_ttl": 600,      # 10 minutes
    "max_retries": 5,      # Retry failed requests
    "timeout": 60          # 60 second timeout
})

# Get current configuration
config = client.get_config()
```

## API Reference

### ETRAPClient

The main client class for interacting with the ETRAP system.

#### Constructor

```python
ETRAPClient(
    organization_id: str,
    network: str = "testnet",
    rpc_endpoint: Optional[str] = None,
    s3_config: Optional[S3Config] = None,
    cache_ttl: int = 300,
    max_retries: int = 3,
    timeout: int = 30
)
```

**Parameters:**
- `organization_id` (str): Your organization identifier (e.g., 'acme')
- `network` (str): NEAR network - 'testnet', 'mainnet', or 'localnet' (default: 'testnet')
- `rpc_endpoint` (Optional[str]): Custom RPC endpoint URL (default: auto-selected based on network)
- `s3_config` (Optional[S3Config]): S3 configuration for batch data access
- `cache_ttl` (int): Cache lifetime in seconds (default: 300)
- `max_retries` (int): Number of retry attempts for network operations (default: 3)
- `timeout` (int): Request timeout in seconds (default: 30)

**Example:**
```python
client = ETRAPClient(
    organization_id="acme",
    network="testnet",
    s3_config=S3Config(region="us-west-2")
)
```

### Transaction Verification Methods

#### verify_transaction

```python
async def verify_transaction(
    transaction_data: Dict[str, Any],
    hints: Optional[VerificationHints] = None,
    timeout: Optional[int] = None
) -> VerificationResult
```

Verifies a single transaction against blockchain records.

**Parameters:**
- `transaction_data` (Dict[str, Any]): Transaction data to verify (must include all original fields)
- `hints` (Optional[VerificationHints]): Optimization hints for faster verification
- `timeout` (Optional[int]): Override default timeout for this request

**Returns:**
- `VerificationResult`: Object containing verification status and proof details

**Raises:**
- `VerificationError`: If verification process fails
- `InvalidTransactionError`: If transaction data is invalid or incomplete
- `NetworkError`: If network communication fails

**Example:**
```python
result = await client.verify_transaction({
    "id": 123,
    "amount": 100.50,
    "account_id": "ACC001",
    "created_at": "2024-01-01 10:00:00"
})

if result.verified:
    print(f"Verified in batch: {result.batch_id}")
    print(f"Merkle proof: {result.merkle_proof}")
```

#### verify_batch

```python
async def verify_batch(
    transactions: List[Dict[str, Any]],
    parallel: bool = True,
    fail_fast: bool = False,
    progress_callback: Optional[Callable] = None
) -> BatchVerificationResult
```

Verifies multiple transactions efficiently.

**Parameters:**
- `transactions` (List[Dict[str, Any]]): List of transactions to verify
- `parallel` (bool): Process transactions in parallel (default: True)
- `fail_fast` (bool): Stop on first failure (default: False)
- `progress_callback` (Optional[Callable]): Callback function for progress updates `(current: int, total: int)`

**Returns:**
- `BatchVerificationResult`: Summary and individual verification results

**Example:**
```python
def progress(current, total):
    print(f"Progress: {current}/{total}")

results = await client.verify_batch(
    transactions=[tx1, tx2, tx3],
    parallel=True,
    progress_callback=progress
)

print(f"Success rate: {results.summary.success_rate:.1%}")
```

### Batch Information Methods

#### get_batch

```python
async def get_batch(batch_id: str) -> Optional[BatchInfo]
```

Retrieves information about a specific batch.

**Parameters:**
- `batch_id` (str): Batch identifier (e.g., "BATCH-2024-01-01-abc123")

**Returns:**
- `Optional[BatchInfo]`: Batch information or None if not found

**Example:**
```python
batch = await client.get_batch("BATCH-2024-01-01-abc123")
if batch:
    print(f"Transactions: {batch.transaction_count}")
    print(f"Merkle root: {batch.merkle_root}")
```

#### list_batches

```python
async def list_batches(
    filter: Optional[BatchFilter] = None,
    limit: int = 100,
    offset: int = 0,
    order_by: str = "timestamp_desc"
) -> BatchList
```

Lists batches with optional filtering and pagination.

**Parameters:**
- `filter` (Optional[BatchFilter]): Filter criteria
- `limit` (int): Maximum number of results (default: 100)
- `offset` (int): Pagination offset (default: 0)
- `order_by` (str): Sort order - 'timestamp_desc', 'timestamp_asc', or 'size_desc' (default: 'timestamp_desc')

**Returns:**
- `BatchList`: List of batches with pagination info

**Example:**
```python
filter = BatchFilter(
    database_name="production",
    table_name="transactions",
    time_range=TimeRange(
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 31)
    )
)

batch_list = await client.list_batches(filter=filter, limit=50)
for batch in batch_list.batches:
    print(f"{batch.batch_id}: {batch.transaction_count} transactions")
```

#### search_batches

```python
async def search_batches(
    criteria: SearchCriteria,
    max_results: int = 1000
) -> SearchResults
```

Searches for batches matching specific criteria.

**Parameters:**
- `criteria` (SearchCriteria): Search criteria including transaction hash, merkle root, date range, etc.
- `max_results` (int): Maximum results to return (default: 1000)

**Returns:**
- `SearchResults`: Matching batches and search time

**Example:**
```python
criteria = SearchCriteria(
    transaction_hash="abc123...",
    date_range=DateRange(start="2024-01-01", end="2024-01-31")
)

results = await client.search_batches(criteria)
print(f"Found {len(results.matching_batches)} batches")
```

### Batch Data Access Methods

#### get_batch_data

```python
async def get_batch_data(
    batch_id: str,
    include_merkle_tree: bool = True,
    include_indices: bool = False,
    decrypt: bool = False
) -> Optional[BatchData]
```

Retrieves complete batch data from S3 storage.

**Parameters:**
- `batch_id` (str): Batch identifier
- `include_merkle_tree` (bool): Include Merkle tree structure (default: True)
- `include_indices` (bool): Include batch indices (default: False)
- `decrypt` (bool): Decrypt data if encrypted (default: False)

**Returns:**
- `Optional[BatchData]`: Complete batch data or None if not found

**Raises:**
- `S3AccessError`: If S3 access fails or credentials are missing
- `BatchNotFoundError`: If batch doesn't exist

**Example:**
```python
batch_data = await client.get_batch_data(
    "BATCH-2024-01-01-abc123",
    include_merkle_tree=True,
    include_indices=True
)

if batch_data:
    print(f"Tree height: {batch_data.merkle_tree.height}")
    print(f"Transaction count: {batch_data.transaction_count}")
```

#### get_merkle_proof

```python
async def get_merkle_proof(
    batch_id: str,
    transaction_hash: str
) -> Optional[MerkleProof]
```

Gets the Merkle proof for a specific transaction in a batch.

**Parameters:**
- `batch_id` (str): Batch containing the transaction
- `transaction_hash` (str): Transaction hash

**Returns:**
- `Optional[MerkleProof]`: Merkle proof or None if transaction not found

**Example:**
```python
proof = await client.get_merkle_proof(
    "BATCH-2024-01-01-abc123",
    "def456..."
)

if proof:
    print(f"Proof path length: {len(proof.proof_path)}")
    print(f"Root: {proof.merkle_root}")
```

### Transaction Search Methods

#### find_transaction

```python
async def find_transaction(
    transaction_hash: str,
    search_depth: int = 100,
    time_range: Optional[TimeRange] = None
) -> Optional[TransactionLocation]
```

Finds a transaction by its hash.

**Parameters:**
- `transaction_hash` (str): Transaction hash to find
- `search_depth` (int): Number of recent batches to search (default: 100)
- `time_range` (Optional[TimeRange]): Time range to limit search

**Returns:**
- `Optional[TransactionLocation]`: Location information or None if not found

**Example:**
```python
location = await client.find_transaction(
    "abc123...",
    search_depth=200,
    time_range=TimeRange(
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 31)
    )
)

if location:
    print(f"Found in batch: {location.batch_id}")
    print(f"Position: {location.position}")
```

#### get_transaction_history

```python
async def get_transaction_history(
    filter: TransactionFilter,
    limit: int = 1000
) -> TransactionHistory
```

Retrieves transaction history matching filter criteria.

**Parameters:**
- `filter` (TransactionFilter): Filter criteria
- `limit` (int): Maximum transactions to return (default: 1000)

**Returns:**
- `TransactionHistory`: Matching transactions and metadata

**Note:** Due to privacy-by-design, only transaction metadata is available, not the actual transaction data.

**Example:**
```python
filter = TransactionFilter(
    time_range=TimeRange(
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 31)
    ),
    operation_types=["INSERT", "UPDATE"]
)

history = await client.get_transaction_history(filter, limit=500)
print(f"Found {history.total_found} transactions")
```

### Contract Information Methods

#### get_contract_info

```python
async def get_contract_info() -> ContractInfo
```

Gets information about the ETRAP smart contract.

**Returns:**
- `ContractInfo`: Contract details including statistics

**Example:**
```python
info = await client.get_contract_info()
print(f"Contract: {info.contract_id}")
print(f"Total batches: {info.total_batches}")
print(f"Supported tables: {', '.join(info.supported_tables)}")
```

#### get_contract_stats

```python
async def get_contract_stats(
    time_period: Optional[str] = "24h"
) -> ContractStats
```

Gets contract usage statistics.

**Parameters:**
- `time_period` (Optional[str]): Time period - '1h', '24h', '7d', '30d', or 'all' (default: '24h')

**Returns:**
- `ContractStats`: Usage statistics for the period

**Example:**
```python
stats = await client.get_contract_stats("7d")
print(f"Batches created: {stats.batches_created}")
print(f"Transactions recorded: {stats.transactions_recorded}")
```

### NFT Information Methods

#### get_nft_info

```python
async def get_nft_info(nft_token_id: str) -> Optional[NFTInfo]
```

Gets comprehensive NFT information for a batch token.

**Parameters:**
- `nft_token_id` (str): NFT token identifier (same as batch_id in ETRAP)

**Returns:**
- `Optional[NFTInfo]`: NFT information including metadata, ownership, and blockchain details, or None if not found

**Example:**
```python
nft_info = await client.get_nft_info("BATCH-2025-07-01-c9de5968")
if nft_info:
    print(f"Owner: {nft_info.owner_id}")
    print(f"Title: {nft_info.metadata.get('title')}")
    print(f"Merkle Root: {nft_info.merkle_root}")
    print(f"Contract: {nft_info.blockchain_details['contract_id']}")
```

### Utility Methods

#### normalize_transaction

```python
def normalize_transaction(
    transaction_data: Dict[str, Any],
    source_format: str = "database"
) -> Dict[str, Any]
```

Normalizes transaction data for verification.

**Parameters:**
- `transaction_data` (Dict[str, Any]): Raw transaction data
- `source_format` (str): Source format - 'database', 'api', or 'csv' (default: 'database')

**Returns:**
- `Dict[str, Any]`: Normalized transaction data

**Example:**
```python
normalized = client.normalize_transaction({
    "amount": 100.50,
    "created_at": "2024-01-01 10:00:00"
})
# Returns: {"amount": "100.50", "created_at": "2024-01-01T10:00:00.000"}
```

#### prepare_transaction_for_storage

```python
def prepare_transaction_for_storage(
    transaction_data: Dict[str, Any]
) -> Dict[str, Any]
```

Prepares transaction data for storage by normalizing it according to ETRAP standards.
This method ensures consistent formatting of transaction data before it's hashed and stored,
matching CDC agent requirements. This is an alias for `normalize_transaction()` for clarity.

**Parameters:**
- `transaction_data` (Dict[str, Any]): Raw transaction data from database

**Returns:**
- `Dict[str, Any]`: Normalized transaction data ready for hashing

**Example:**
```python
# Used by CDC Agent for consistent data processing
prepared_data = client.prepare_transaction_for_storage({
    "id": 123,
    "amount": 100.50,
    "created_at": 1718351455461  # Epoch timestamp
})
# Returns normalized data with consistent formatting
```

#### compute_transaction_hash

```python
def compute_transaction_hash(
    transaction_data: Dict[str, Any],
    normalize: bool = True
) -> str
```

Computes the hash of transaction data.

**Parameters:**
- `transaction_data` (Dict[str, Any]): Transaction data
- `normalize` (bool): Whether to normalize data first (default: True)

**Returns:**
- `str`: SHA256 hash as hex string

**Example:**
```python
tx_hash = client.compute_transaction_hash({
    "id": 123,
    "amount": 100.50
})
print(f"Hash: {tx_hash}")
```

#### validate_merkle_proof

```python
def validate_merkle_proof(
    leaf_hash: str,
    proof: MerkleProof,
    root: str
) -> bool
```

Validates a Merkle proof.

**Parameters:**
- `leaf_hash` (str): Leaf hash
- `proof` (MerkleProof): Merkle proof to validate
- `root` (str): Expected root hash

**Returns:**
- `bool`: True if proof is valid

**Example:**
```python
is_valid = client.validate_merkle_proof(
    leaf_hash="abc123...",
    proof=merkle_proof,
    root="def456..."
)
```

#### update_config

```python
def update_config(config: Dict[str, Any]) -> None
```

Updates client configuration.

**Parameters:**
- `config` (Dict[str, Any]): Configuration updates

**Example:**
```python
client.update_config({
    "cache_ttl": 600,
    "max_retries": 5,
    "timeout": 60
})
```

#### get_config

```python
def get_config() -> ClientConfig
```

Gets current client configuration.

**Returns:**
- `ClientConfig`: Current configuration

**Example:**
```python
config = client.get_config()
print(f"Cache TTL: {config.cache_ttl} seconds")
```

## Common Exceptions

- **ETRAPError**: Base exception for all ETRAP errors
- **VerificationError**: Transaction verification failed
- **BatchNotFoundError**: Requested batch not found
- **NetworkError**: Network communication error
- **ContractError**: Smart contract interaction error
- **S3AccessError**: S3 access or permissions error
- **InvalidTransactionError**: Invalid transaction data provided

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## 🪪 License

MIT. See `./LICENSE`


## 📄 Copyright

Copyright (c) 2025 Graziano Labs Corp. All rights reserved.


## 📧 Contact

For questions or support, please open an issue in the GitHub repository.

---