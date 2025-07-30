"""
Tests for ETRAP SDK utility functions.
"""

import pytest
from datetime import datetime

from etrap_sdk.utils import (
    normalize_transaction_data,
    compute_transaction_hash,
    validate_merkle_proof,
    parse_timestamp
)


class TestNormalization:
    """Test transaction data normalization."""
    
    def test_normalize_basic_transaction(self):
        """Test basic transaction normalization."""
        input_data = {
            "id": 123,
            "amount": 999.99,
            "type": "C",
            "created_at": "2025-06-14 07:10:55.461133"
        }
        
        expected = {
            "id": 123,
            "amount": "999.99",
            "type": "C",
            "created_at": "2025-06-14T07:10:55.461"
        }
        
        result = normalize_transaction_data(input_data)
        assert result == expected
    
    def test_normalize_already_normalized(self):
        """Test that already normalized data stays the same."""
        input_data = {
            "id": 123,
            "amount": "999.99",
            "created_at": "2025-06-14T07:10:55.461"
        }
        
        expected = {
            "id": 123,
            "amount": "999.99",
            "created_at": "2025-06-14T07:10:55.461"
        }
        
        result = normalize_transaction_data(input_data)
        assert result == expected
    
    def test_normalize_different_timestamp_formats(self):
        """Test various timestamp formats."""
        test_cases = [
            ("2025-06-14 07:10:55", "2025-06-14T07:10:55.000"),
            ("2025-06-14T07:10:55", "2025-06-14T07:10:55.000"),
            ("2025-06-14 07:10:55.1", "2025-06-14T07:10:55.100"),
            ("2025-06-14T07:10:55.461133", "2025-06-14T07:10:55.461"),
            ("2025-06-14 07:10:55.000000", "2025-06-14T07:10:55.000"),
        ]
        
        for input_ts, expected_ts in test_cases:
            result = normalize_transaction_data({"created_at": input_ts})
            assert result["created_at"] == expected_ts
    
    def test_normalize_numeric_fields(self):
        """Test normalization of numeric fields."""
        input_data = {
            "id": 123,
            "amount": 999.99,
            "balance": 1234.5,
            "count": 10
        }
        
        result = normalize_transaction_data(input_data)
        assert result["id"] == 123
        assert result["amount"] == "999.99"
        assert result["balance"] == "1234.50"  # Float formatting adds trailing zero
        assert result["count"] == 10
    
    def test_normalize_null_values(self):
        """Test handling of null values."""
        input_data = {
            "id": 123,
            "amount": None,
            "reference": None
        }
        
        result = normalize_transaction_data(input_data)
        assert result["id"] == 123
        assert result["amount"] is None
        assert result["reference"] is None
    
    def test_normalize_nested_data(self):
        """Test normalization doesn't affect nested structures."""
        input_data = {
            "id": 123,
            "metadata": {
                "user_id": 456,
                "tags": ["test", "sample"]
            }
        }
        
        result = normalize_transaction_data(input_data)
        assert result["id"] == 123
        assert result["metadata"]["user_id"] == 456  # Nested data not normalized
        assert result["metadata"]["tags"] == ["test", "sample"]
    
    def test_normalize_at_fields_with_epoch(self):
        """Test that numeric _at fields convert to ISO format."""
        input_data = {
            "id": 123,
            "created_at": 1736282700000,  # Epoch milliseconds
            "updated_at": 1736282700,      # Epoch seconds
            "transaction_date_time": 1736282700000,  # Not _at field
            "amount": 100.0
        }
        
        result = normalize_transaction_data(input_data)
        assert result["id"] == 123
        # Check that created_at was converted to ISO format (exact time depends on timezone)
        assert isinstance(result["created_at"], str)
        assert result["created_at"].startswith("2025-01-07T")
        assert result["created_at"].endswith(".000")
        # Check updated_at conversion
        assert isinstance(result["updated_at"], str)
        assert result["updated_at"].startswith("2025-01-07T")
        assert result["transaction_date_time"] == 1736282700000  # Stays as number
        assert result["amount"] == "100.00"  # Float becomes string


class TestHashing:
    """Test transaction hashing functionality."""
    
    def test_compute_hash_basic(self):
        """Test basic hash computation."""
        data = {
            "id": "123",
            "amount": "999.99",
            "type": "C"
        }
        
        hash1 = compute_transaction_hash(data, normalize=False)
        hash2 = compute_transaction_hash(data, normalize=False)
        
        assert hash1 == hash2  # Same data produces same hash
        assert len(hash1) == 64  # SHA256 produces 64 hex chars
    
    def test_compute_hash_with_normalization(self):
        """Test hash computation with normalization."""
        # Test that same types produce same hash
        data1 = {"id": 123, "amount": 999.99}
        data2 = {"id": 123, "amount": 999.99}
        
        hash1 = compute_transaction_hash(data1, normalize=True)
        hash2 = compute_transaction_hash(data2, normalize=True)
        
        assert hash1 == hash2  # Same data produces same hash
        
        # Test that normalization converts floats to strings but keeps ints
        data3 = {"id": 123, "amount": 999.99, "count": 10}
        normalized = normalize_transaction_data(data3)
        assert normalized["id"] == 123  # int stays int
        assert normalized["count"] == 10  # int stays int
        assert normalized["amount"] == "999.99"  # float becomes string
    
    def test_compute_hash_order_insensitive(self):
        """Test that field order doesn't matter for hashing (uses sort_keys)."""
        data1 = {"id": "123", "amount": "999.99", "type": "C"}
        data2 = {"type": "C", "id": "123", "amount": "999.99"}
        
        hash1 = compute_transaction_hash(data1, normalize=False)
        hash2 = compute_transaction_hash(data2, normalize=False)
        
        assert hash1 == hash2  # Same hash regardless of field order
    
    def test_compute_hash_includes_nulls(self):
        """Test that null values are included in hash (matching CDC agent behavior)."""
        data1 = {"id": "123", "amount": "999.99"}
        data2 = {"id": "123", "amount": "999.99", "reference": None}
        
        hash1 = compute_transaction_hash(data1, normalize=False)
        hash2 = compute_transaction_hash(data2, normalize=False)
        
        assert hash1 != hash2  # Null fields DO affect hash (CDC agent includes them)


class TestMerkleProof:
    """Test Merkle proof validation."""
    
    def test_validate_merkle_proof_simple(self):
        """Test simple Merkle proof validation."""
        leaf_hash = "leaf123"
        proof_path = ["sibling456", "parent789"]
        sibling_positions = ["right", "left"]
        root = "expected_root"
        
        # This is a simplified test - in reality would need actual hashes
        # For now just test the function interface
        result = validate_merkle_proof(leaf_hash, proof_path, sibling_positions, root)
        assert isinstance(result, bool)
    
    def test_validate_merkle_proof_empty(self):
        """Test Merkle proof with empty path."""
        # Single leaf tree - leaf is the root
        leaf_hash = "single_leaf"
        proof_path = []
        sibling_positions = []
        root = "single_leaf"
        
        # Would need proper implementation to test this
        result = validate_merkle_proof(leaf_hash, proof_path, sibling_positions, root)
        assert isinstance(result, bool)


class TestTimestampParsing:
    """Test timestamp parsing functionality."""
    
    def test_parse_timestamp_iso(self):
        """Test parsing ISO format timestamps."""
        ts = "2025-06-14T07:10:55.461"
        result = parse_timestamp(ts)
        
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 6
        assert result.day == 14
        assert result.hour == 7
        assert result.minute == 10
        assert result.second == 55
        assert result.microsecond == 461000
    
    def test_parse_timestamp_space_separator(self):
        """Test parsing timestamps with space separator."""
        ts = "2025-06-14 07:10:55.461"
        result = parse_timestamp(ts)
        
        assert result.year == 2025
        assert result.month == 6
        assert result.day == 14
    
    def test_parse_timestamp_no_microseconds(self):
        """Test parsing timestamps without microseconds."""
        ts = "2025-06-14T07:10:55"
        result = parse_timestamp(ts)
        
        assert result.microsecond == 0
    
    def test_parse_timestamp_epoch(self):
        """Test parsing epoch timestamps."""
        # Milliseconds since epoch
        ts = 1734161455461
        result = parse_timestamp(ts)
        
        assert isinstance(result, datetime)
        assert result.year == 2024  # Adjust based on actual epoch value
    
    def test_parse_timestamp_datetime_passthrough(self):
        """Test that datetime objects pass through unchanged."""
        dt = datetime(2025, 6, 14, 7, 10, 55)
        result = parse_timestamp(dt)
        
        assert result == dt