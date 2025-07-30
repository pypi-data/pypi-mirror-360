"""
Tests for ETRAP SDK exceptions.
"""

import pytest

from etrap_sdk.exceptions import (
    ETRAPError, VerificationError, BatchNotFoundError, NetworkError,
    ContractError, S3AccessError, InvalidTransactionError,
    ConfigurationError, TimeoutError
)


class TestExceptions:
    """Test exception hierarchy and behavior."""
    
    def test_base_exception(self):
        """Test base ETRAPError."""
        error = ETRAPError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_verification_error(self):
        """Test VerificationError with transaction details."""
        error = VerificationError(
            "Verification failed",
            transaction_hash="hash123",
            batch_id="BATCH-123"
        )
        
        assert str(error) == "Verification failed"
        assert error.transaction_hash == "hash123"
        assert error.batch_id == "BATCH-123"
        assert isinstance(error, ETRAPError)
    
    def test_batch_not_found_error(self):
        """Test BatchNotFoundError."""
        error = BatchNotFoundError(
            "Batch not found",
            batch_id="BATCH-123"
        )
        
        assert error.batch_id == "BATCH-123"
        assert isinstance(error, ETRAPError)
    
    def test_network_error(self):
        """Test NetworkError with details."""
        error = NetworkError(
            "Connection failed",
            endpoint="https://rpc.testnet.near.org",
            status_code=500
        )
        
        assert error.endpoint == "https://rpc.testnet.near.org"
        assert error.status_code == 500
        assert isinstance(error, ETRAPError)
    
    def test_contract_error(self):
        """Test ContractError."""
        error = ContractError(
            "Contract call failed",
            contract_id="test.testnet",
            method="get_batch"
        )
        
        assert error.contract_id == "test.testnet"
        assert error.method == "get_batch"
        assert isinstance(error, ETRAPError)
    
    def test_s3_access_error(self):
        """Test S3AccessError."""
        error = S3AccessError(
            "Access denied",
            bucket="test-bucket",
            key="test/key"
        )
        
        assert error.bucket == "test-bucket"
        assert error.key == "test/key"
        assert isinstance(error, ETRAPError)
    
    def test_invalid_transaction_error(self):
        """Test InvalidTransactionError."""
        error = InvalidTransactionError(
            "Invalid transaction data",
            field="amount",
            value="invalid"
        )
        
        assert error.field == "amount"
        assert error.value == "invalid"
        assert isinstance(error, ETRAPError)
    
    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError(
            "Invalid configuration",
            parameter="cache_ttl",
            value=-1
        )
        
        assert error.parameter == "cache_ttl"
        assert error.value == -1
        assert isinstance(error, ETRAPError)
    
    def test_timeout_error(self):
        """Test TimeoutError."""
        error = TimeoutError(
            "Request timed out",
            operation="verify_transaction",
            timeout_seconds=30
        )
        
        assert error.operation == "verify_transaction"
        assert error.timeout_seconds == 30
        assert isinstance(error, ETRAPError)
    
    def test_exception_inheritance(self):
        """Test that all exceptions inherit from ETRAPError."""
        exceptions = [
            VerificationError("test"),
            BatchNotFoundError("test"),
            NetworkError("test"),
            ContractError("test"),
            S3AccessError("test"),
            InvalidTransactionError("test"),
            ConfigurationError("test"),
            TimeoutError("test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, ETRAPError)
            assert isinstance(exc, Exception)
    
    def test_exception_with_cause(self):
        """Test exception chaining."""
        original_error = ValueError("Original error")
        
        try:
            raise NetworkError("Network failed") from original_error
        except NetworkError as e:
            assert e.__cause__ == original_error
            assert str(e) == "Network failed"
    
    def test_exception_attributes_optional(self):
        """Test that extra attributes are optional."""
        # Should work without extra attributes
        error = VerificationError("Simple error")
        assert str(error) == "Simple error"
        assert hasattr(error, 'transaction_hash')
        assert error.transaction_hash is None
        
        # Should work with some attributes
        error = NetworkError("Network error", endpoint="test.com")
        assert error.endpoint == "test.com"
        assert error.status_code is None