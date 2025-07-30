"""
Data models for ETRAP SDK.

These models define the structure of data exchanged between the SDK and ETRAP system.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


# Time and Range Models
class TimeRange(BaseModel):
    """Time range for filtering operations."""
    start: datetime
    end: datetime


class DateRange(BaseModel):
    """Date range for filtering operations."""
    start: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    end: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")


class AmountRange(BaseModel):
    """Amount range for filtering transactions."""
    min_amount: Optional[str] = None
    max_amount: Optional[str] = None
    currency: str = "USD"


# Verification Models
class VerificationHints(BaseModel):
    """Hints to optimize verification process."""
    batch_id: Optional[str] = None
    table_name: Optional[str] = None
    database_name: Optional[str] = None
    time_range: Optional[TimeRange] = None
    expected_operation: Optional[str] = Field(None, pattern=r"^(INSERT|UPDATE|DELETE)$")


class MerkleProof(BaseModel):
    """Merkle proof for transaction verification."""
    leaf_hash: str
    proof_path: List[str]
    sibling_positions: List[str]
    merkle_root: str
    is_valid: bool = False


class VerificationResult(BaseModel):
    """Result of transaction verification."""
    verified: bool
    transaction_hash: str
    batch_id: Optional[str] = None
    merkle_proof: Optional[MerkleProof] = None
    blockchain_timestamp: Optional[datetime] = None
    gas_used: Optional[str] = None
    error: Optional[str] = None
    operation_type: Optional[str] = None


class VerificationSummary(BaseModel):
    """Summary statistics for batch verification."""
    success_rate: float
    average_verification_time_ms: float
    blockchain_confirmations: int


class BatchVerificationResult(BaseModel):
    """Result of batch transaction verification."""
    total: int
    verified: int
    failed: int
    results: List[VerificationResult]
    summary: VerificationSummary


# Batch Models
class S3Location(BaseModel):
    """S3 location information."""
    bucket: str
    key: str
    region: str = "us-west-2"


class OperationCounts(BaseModel):
    """Operation counts for a batch."""
    inserts: int = 0
    updates: int = 0
    deletes: int = 0


class BatchInfo(BaseModel):
    """Information about a batch stored on blockchain."""
    batch_id: str
    database_name: str
    table_names: List[str]
    transaction_count: int
    merkle_root: str
    timestamp: datetime
    s3_location: S3Location
    size_bytes: int


class BatchFilter(BaseModel):
    """Filter criteria for batch queries."""
    database_name: Optional[str] = None
    table_name: Optional[str] = None
    time_range: Optional[TimeRange] = None
    operation_types: Optional[List[str]] = None
    min_transactions: Optional[int] = None
    max_transactions: Optional[int] = None


class BatchList(BaseModel):
    """List of batches with pagination info."""
    batches: List[BatchInfo]
    total_count: int
    has_more: bool


class BatchIndices(BaseModel):
    """Indices for efficient batch data lookup."""
    by_timestamp: Dict[str, List[str]]
    by_operation: Dict[str, List[str]]
    by_date: Dict[str, List[str]]


class MerkleTree(BaseModel):
    """Complete Merkle tree structure."""
    algorithm: str = "sha256"
    root: str
    height: int
    nodes: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]
    proof_index: Dict[str, Dict[str, Any]]


class BatchData(BaseModel):
    """Complete batch data including Merkle tree."""
    batch_info: BatchInfo
    merkle_tree: Optional[MerkleTree] = None
    transaction_count: int
    indices: Optional[BatchIndices] = None
    operation_counts: Optional[OperationCounts] = None


# Search Models
class SearchCriteria(BaseModel):
    """Search criteria for finding batches."""
    transaction_hash: Optional[str] = None
    merkle_root: Optional[str] = None
    operation_type: Optional[List[str]] = None
    date_range: Optional[DateRange] = None


class SearchResults(BaseModel):
    """Results from batch search."""
    matching_batches: List[BatchInfo]
    search_time_ms: int


# Transaction Models
class TransactionLocation(BaseModel):
    """Location of a transaction within a batch."""
    batch_id: str
    position: int
    batch_info: BatchInfo


class TransactionFilter(BaseModel):
    """Filter for transaction queries."""
    account_id: Optional[str] = None
    transaction_type: Optional[str] = None
    amount_range: Optional[AmountRange] = None
    operation_types: Optional[List[str]] = None
    time_range: Optional[TimeRange] = None


class TransactionRecord(BaseModel):
    """Record of a transaction from batch data."""
    transaction_id: str
    timestamp: datetime
    operation_type: str
    database_name: str
    table_affected: str
    transaction_hash: str
    metadata: Dict[str, Any]


class TransactionHistory(BaseModel):
    """Transaction history query results."""
    transactions: List[TransactionRecord]
    total_found: int
    time_range_covered: TimeRange


# NFT Models
class NFTInfo(BaseModel):
    """Information about a NEAR NFT representing a batch."""
    token_id: str
    owner_id: str
    metadata: Dict[str, Any]
    minted_timestamp: datetime
    batch_id: str
    organization_id: str
    merkle_root: str
    blockchain_details: Dict[str, Any]


# Contract Models
class ContractInfo(BaseModel):
    """Information about the NEAR smart contract."""
    contract_id: str
    total_batches: int
    total_transactions: int
    earliest_batch: datetime
    latest_batch: datetime
    supported_tables: List[str]
    supported_databases: List[str]


class ContractStats(BaseModel):
    """Statistics from the smart contract."""
    batches_created: int
    transactions_recorded: int
    unique_tables: int
    unique_databases: int
    gas_consumed: str
    storage_used: str
    time_period: str


# Configuration Models
class S3Config(BaseModel):
    """S3 configuration for batch data access."""
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region: str = "us-west-2"
    bucket_name: Optional[str] = Field(None, min_length=1)
    endpoint_url: Optional[str] = None


class ClientConfig(BaseModel):
    """Client configuration options."""
    cache_ttl: int = 300
    max_retries: int = 3
    timeout: int = 30
    batch_size: int = 100
    verify_ssl: bool = True
    log_level: str = "INFO"