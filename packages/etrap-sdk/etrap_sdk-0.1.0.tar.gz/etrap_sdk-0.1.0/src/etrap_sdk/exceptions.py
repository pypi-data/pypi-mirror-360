"""
Exception classes for ETRAP SDK.

These exceptions provide specific error handling for different failure scenarios.
"""

from typing import Any


class ETRAPError(Exception):
    """Base exception for all ETRAP SDK errors."""
    pass


class VerificationError(ETRAPError):
    """Raised when transaction verification fails."""
    
    def __init__(self, message: str, transaction_hash: str = None, batch_id: str = None):
        super().__init__(message)
        self.transaction_hash = transaction_hash
        self.batch_id = batch_id


class BatchNotFoundError(ETRAPError):
    """Raised when a requested batch cannot be found."""
    
    def __init__(self, message: str = None, batch_id: str = None):
        if message is None and batch_id:
            message = f"Batch not found: {batch_id}"
        elif message is None:
            message = "Batch not found"
        super().__init__(message)
        self.batch_id = batch_id


class NetworkError(ETRAPError):
    """Raised when network operations fail."""
    
    def __init__(self, message: str, endpoint: str = None, status_code: int = None, retry_after: int = None):
        super().__init__(message)
        self.endpoint = endpoint
        self.status_code = status_code
        self.retry_after = retry_after


class ContractError(ETRAPError):
    """Raised when smart contract operations fail."""
    
    def __init__(self, message: str, contract_id: str = None, method: str = None, args: dict = None):
        super().__init__(message)
        self.contract_id = contract_id
        self.method = method
        self.contract_args = args  # Rename to avoid conflict with BaseException.args


class S3AccessError(ETRAPError):
    """Raised when S3 operations fail."""
    
    def __init__(self, message: str, bucket: str = None, key: str = None):
        super().__init__(message)
        self.bucket = bucket
        self.key = key


class InvalidTransactionError(ETRAPError):
    """Raised when transaction data is invalid."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message)
        self.field = field
        self.value = value


class ConfigurationError(ETRAPError):
    """Raised when SDK configuration is invalid."""
    
    def __init__(self, message: str, parameter: str = None, value: Any = None):
        super().__init__(message)
        self.parameter = parameter
        self.value = value


class TimeoutError(ETRAPError):
    """Raised when an operation times out."""
    
    def __init__(self, message: str, operation: str = None, timeout_seconds: int = None):
        super().__init__(message)
        self.operation = operation
        self.timeout_seconds = timeout_seconds