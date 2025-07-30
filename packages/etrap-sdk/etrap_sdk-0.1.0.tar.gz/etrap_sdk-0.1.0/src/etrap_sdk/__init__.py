"""
ETRAP SDK - Enterprise Transaction Recording and Audit Platform SDK

A Python SDK for interacting with the ETRAP system to verify transactions,
access audit trails, and ensure data integrity through blockchain verification.
"""

__version__ = "0.1.0"

# Main client
from .client import ETRAPClient

# Models
from .models import (
    # Verification
    VerificationHints,
    VerificationResult,
    BatchVerificationResult,
    MerkleProof,
    VerificationSummary,
    
    # Batches
    BatchInfo,
    BatchFilter,
    BatchList,
    BatchData,
    BatchIndices,
    MerkleTree,
    OperationCounts,
    
    # Search
    SearchCriteria,
    SearchResults,
    
    # Transactions
    TransactionLocation,
    TransactionFilter,
    TransactionHistory,
    TransactionRecord,
    
    # Configuration
    S3Config,
    ClientConfig,
    S3Location,
    
    # Contract
    ContractInfo,
    ContractStats,
    
    # NFT
    NFTInfo,
    
    # Time/Range
    TimeRange,
    DateRange,
    AmountRange,
)

# Exceptions
from .exceptions import (
    ETRAPError,
    VerificationError,
    BatchNotFoundError,
    NetworkError,
    ContractError,
    S3AccessError,
    InvalidTransactionError,
    ConfigurationError,
    TimeoutError,
)

# Utilities
from .utils import (
    normalize_transaction_data,
    compute_transaction_hash,
    validate_merkle_proof,
)

__all__ = [
    # Client
    "ETRAPClient",
    
    # Models
    "VerificationHints",
    "VerificationResult", 
    "BatchVerificationResult",
    "MerkleProof",
    "VerificationSummary",
    "BatchInfo",
    "BatchFilter",
    "BatchList",
    "BatchData",
    "BatchIndices",
    "MerkleTree",
    "OperationCounts",
    "SearchCriteria",
    "SearchResults",
    "TransactionLocation",
    "TransactionFilter",
    "TransactionHistory",
    "TransactionRecord",
    "S3Config",
    "ClientConfig",
    "S3Location",
    "ContractInfo",
    "ContractStats",
    "NFTInfo",
    "TimeRange",
    "DateRange",
    "AmountRange",
    
    # Exceptions
    "ETRAPError",
    "VerificationError",
    "BatchNotFoundError",
    "NetworkError",
    "ContractError",
    "S3AccessError",
    "InvalidTransactionError",
    "ConfigurationError",
    "TimeoutError",
    
    # Utilities
    "normalize_transaction_data",
    "compute_transaction_hash",
    "validate_merkle_proof",
]
