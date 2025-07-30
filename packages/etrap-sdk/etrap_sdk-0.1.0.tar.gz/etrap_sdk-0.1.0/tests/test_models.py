"""
Tests for ETRAP SDK data models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from etrap_sdk.models import (
    VerificationHints, VerificationResult, BatchVerificationResult,
    MerkleProof, BatchInfo, BatchFilter, BatchList, BatchData,
    SearchCriteria, SearchResults, TransactionLocation, TransactionFilter,
    TransactionHistory, TransactionRecord, ContractInfo, ContractStats,
    S3Config, ClientConfig, S3Location, TimeRange, DateRange,
    AmountRange, MerkleTree, BatchIndices, VerificationSummary
)


class TestVerificationModels:
    """Test verification-related models."""
    
    def test_verification_hints(self):
        """Test VerificationHints model."""
        time_range = TimeRange(start=datetime.now(), end=datetime.now())
        hints = VerificationHints(
            batch_id="BATCH-123",
            table_name="transactions",
            database_name="production",
            time_range=time_range
        )
        
        assert hints.batch_id == "BATCH-123"
        assert hints.table_name == "transactions"
        assert hints.database_name == "production"
        assert hints.time_range is not None
    
    def test_verification_result_success(self):
        """Test successful VerificationResult."""
        result = VerificationResult(
            verified=True,
            transaction_hash="hash123",
            batch_id="BATCH-123",
            merkle_proof=MerkleProof(
                leaf_hash="leaf123",
                proof_path=["hash1", "hash2"],
                sibling_positions=["left", "right"],
                merkle_root="root123",
                is_valid=True
            ),
            blockchain_timestamp=datetime.now(),
            gas_used="100000"
        )
        
        assert result.verified is True
        assert result.batch_id == "BATCH-123"
        assert result.merkle_proof is not None
        assert result.error is None
    
    def test_verification_result_failure(self):
        """Test failed VerificationResult."""
        result = VerificationResult(
            verified=False,
            transaction_hash="hash123",
            error="Transaction not found"
        )
        
        assert result.verified is False
        assert result.error == "Transaction not found"
        assert result.batch_id is None
        assert result.merkle_proof is None
    
    def test_batch_verification_result(self):
        """Test BatchVerificationResult model."""
        summary = VerificationSummary(
            success_rate=0.8,
            average_verification_time_ms=100.5,
            blockchain_confirmations=8
        )
        
        result = BatchVerificationResult(
            total=10,
            verified=8,
            failed=2,
            results=[],
            summary=summary
        )
        
        assert result.total == 10
        assert result.verified == 8
        assert result.failed == 2
        assert result.summary.success_rate == 0.8


class TestBatchModels:
    """Test batch-related models."""
    
    def test_batch_info(self):
        """Test BatchInfo model."""
        s3_location = S3Location(
            bucket="test-bucket",
            key="test/key/",
            region="us-west-2"
        )
        
        batch = BatchInfo(
            batch_id="BATCH-123",
            database_name="test_db",
            table_names=["table1", "table2"],
            transaction_count=100,
            merkle_root="root123",
            timestamp=datetime.now(),
            s3_location=s3_location,
            size_bytes=50000
        )
        
        assert batch.batch_id == "BATCH-123"
        assert len(batch.table_names) == 2
        assert batch.transaction_count == 100
        assert batch.s3_location.bucket == "test-bucket"
    
    def test_batch_filter(self):
        """Test BatchFilter model."""
        time_range = TimeRange(
            start=datetime(2025, 1, 1),
            end=datetime(2025, 12, 31)
        )
        
        filter = BatchFilter(
            database_name="production",
            table_name="users",
            time_range=time_range,
            operation_types=["INSERT", "UPDATE"],
            min_transactions=10,
            max_transactions=1000
        )
        
        assert filter.database_name == "production"
        assert filter.table_name == "users"
        assert len(filter.operation_types) == 2
        assert filter.min_transactions == 10
    
    def test_batch_list(self):
        """Test BatchList model."""
        batches = [
            BatchInfo(
                batch_id=f"BATCH-{i}",
                database_name="test_db",
                table_names=["table1"],
                transaction_count=100,
                merkle_root=f"root{i}",
                timestamp=datetime.now(),
                s3_location=S3Location(
                    bucket="test",
                    key=f"key{i}",
                    region="us-west-2"
                ),
                size_bytes=50000
            )
            for i in range(3)
        ]
        
        batch_list = BatchList(
            batches=batches,
            total_count=10,
            has_more=True
        )
        
        assert len(batch_list.batches) == 3
        assert batch_list.total_count == 10
        assert batch_list.has_more is True
    
    def test_batch_data(self):
        """Test BatchData model."""
        batch_info = BatchInfo(
            batch_id="BATCH-123",
            database_name="test_db",
            table_names=["table1"],
            transaction_count=100,
            merkle_root="root123",
            timestamp=datetime.now(),
            s3_location=S3Location(
                bucket="test",
                key="key",
                region="us-west-2"
            ),
            size_bytes=50000
        )
        
        merkle_tree = MerkleTree(
            algorithm="sha256",
            root="root123",
            height=5,
            nodes={"0-0": {"hash": "leaf1"}},
            proof_index={}
        )
        
        indices = BatchIndices(
            by_timestamp={},
            by_operation={},
            by_date={}
        )
        
        batch_data = BatchData(
            batch_info=batch_info,
            merkle_tree=merkle_tree,
            transaction_count=100,
            indices=indices
        )
        
        assert batch_data.batch_info.batch_id == "BATCH-123"
        assert batch_data.merkle_tree.algorithm == "sha256"
        assert batch_data.transaction_count == 100


class TestSearchModels:
    """Test search-related models."""
    
    def test_search_criteria(self):
        """Test SearchCriteria model."""
        criteria = SearchCriteria(
            transaction_hash="hash123",
            merkle_root="root123",
            date_range=DateRange(start="2025-01-01", end="2025-12-31"),
            operation_type=["INSERT"]  # Should be a list
        )
        
        assert criteria.transaction_hash == "hash123"
        assert criteria.merkle_root == "root123"
        assert criteria.date_range.start == "2025-01-01"
        assert criteria.date_range.end == "2025-12-31"
        assert criteria.operation_type == ["INSERT"]
    
    def test_search_results(self):
        """Test SearchResults model."""
        batches = [
            BatchInfo(
                batch_id="BATCH-1",
                database_name="test_db",
                table_names=["table1"],
                transaction_count=100,
                merkle_root="root1",
                timestamp=datetime.now(),
                s3_location=S3Location(
                    bucket="test",
                    key="key1",
                    region="us-west-2"
                ),
                size_bytes=50000
            )
        ]
        
        results = SearchResults(
            matching_batches=batches,
            search_time_ms=150
        )
        
        assert len(results.matching_batches) == 1
        assert results.search_time_ms == 150


class TestTransactionModels:
    """Test transaction-related models."""
    
    def test_transaction_location(self):
        """Test TransactionLocation model."""
        batch_info = BatchInfo(
            batch_id="BATCH-123",
            database_name="test_db",
            table_names=["table1"],
            transaction_count=100,
            merkle_root="root123",
            timestamp=datetime.now(),
            s3_location=S3Location(
                bucket="test",
                key="key",
                region="us-west-2"
            ),
            size_bytes=50000
        )
        
        location = TransactionLocation(
            batch_id="BATCH-123",
            position=42,
            batch_info=batch_info
        )
        
        assert location.batch_id == "BATCH-123"
        assert location.position == 42
        assert location.batch_info.database_name == "test_db"
    
    def test_transaction_filter(self):
        """Test TransactionFilter model."""
        time_range = TimeRange(
            start=datetime(2025, 1, 1),
            end=datetime(2025, 12, 31)
        )
        
        amount_range = AmountRange(
            min_amount="100.00",
            max_amount="1000.00"
        )
        
        filter = TransactionFilter(
            account_id="ACC123",
            transaction_type="C",
            operation_types=["INSERT", "UPDATE"],
            time_range=time_range,
            amount_range=amount_range
        )
        
        assert filter.account_id == "ACC123"
        assert filter.transaction_type == "C"
        assert len(filter.operation_types) == 2
        assert filter.amount_range.min_amount == "100.00"
    
    def test_transaction_record(self):
        """Test TransactionRecord model."""
        record = TransactionRecord(
            transaction_id="tx-123",
            timestamp=datetime.now(),
            operation_type="INSERT",
            database_name="test_db",
            table_affected="users",
            transaction_hash="hash123",
            metadata={"key": "value"}
        )
        
        assert record.transaction_id == "tx-123"
        assert record.operation_type == "INSERT"
        assert record.database_name == "test_db"
        assert record.table_affected == "users"
        assert record.metadata["key"] == "value"
    
    def test_transaction_history(self):
        """Test TransactionHistory model."""
        transactions = [
            TransactionRecord(
                transaction_id=f"tx-{i}",
                timestamp=datetime.now(),
                operation_type="INSERT",
                database_name="test_db",
                table_affected="users",
                transaction_hash=f"hash{i}",
                metadata={}
            )
            for i in range(3)
        ]
        
        time_range = TimeRange(
            start=datetime(2025, 1, 1),
            end=datetime(2025, 12, 31)
        )
        
        history = TransactionHistory(
            transactions=transactions,
            total_found=10,
            time_range_covered=time_range
        )
        
        assert len(history.transactions) == 3
        assert history.total_found == 10
        assert history.time_range_covered.start.year == 2025


class TestContractModels:
    """Test contract-related models."""
    
    def test_contract_info(self):
        """Test ContractInfo model."""
        info = ContractInfo(
            contract_id="test.testnet",
            total_batches=100,
            total_transactions=10000,
            earliest_batch=datetime(2025, 1, 1),
            latest_batch=datetime(2025, 6, 1),
            supported_tables=["users", "transactions"],
            supported_databases=["production", "staging"]
        )
        
        assert info.contract_id == "test.testnet"
        assert info.total_batches == 100
        assert info.total_transactions == 10000
        assert len(info.supported_tables) == 2
        assert len(info.supported_databases) == 2
    
    def test_contract_stats(self):
        """Test ContractStats model."""
        stats = ContractStats(
            batches_created=50,
            transactions_recorded=5000,
            unique_tables=10,
            unique_databases=2,
            gas_consumed="1000000000",
            storage_used="500MB",
            time_period="24h"
        )
        
        assert stats.batches_created == 50
        assert stats.transactions_recorded == 5000
        assert stats.unique_tables == 10
        assert stats.time_period == "24h"


class TestConfigurationModels:
    """Test configuration models."""
    
    def test_s3_config(self):
        """Test S3Config model."""
        config = S3Config(
            bucket_name="test-bucket",
            region="us-west-2",
            access_key_id="test-key",
            secret_access_key="test-secret",
            endpoint_url="https://s3.custom.com"
        )
        
        assert config.bucket_name == "test-bucket"
        assert config.region == "us-west-2"
        assert config.access_key_id == "test-key"
        assert config.endpoint_url == "https://s3.custom.com"
    
    def test_client_config(self):
        """Test ClientConfig model."""
        config = ClientConfig(
            cache_ttl=600,
            max_retries=5,
            timeout=60,
            batch_size=100,
            verify_ssl=True
        )
        
        assert config.cache_ttl == 600
        assert config.max_retries == 5
        assert config.timeout == 60
        assert config.batch_size == 100
        assert config.verify_ssl is True


class TestRangeModels:
    """Test range models."""
    
    def test_time_range(self):
        """Test TimeRange model."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 12, 31)
        
        time_range = TimeRange(start=start, end=end)
        
        assert time_range.start == start
        assert time_range.end == end
    
    def test_date_range(self):
        """Test DateRange model."""
        date_range = DateRange(
            start="2025-01-01",
            end="2025-12-31"
        )
        
        assert date_range.start == "2025-01-01"
        assert date_range.end == "2025-12-31"
    
    def test_amount_range(self):
        """Test AmountRange model."""
        amount_range = AmountRange(
            min_amount="100.00",
            max_amount="1000.00"
        )
        
        assert amount_range.min_amount == "100.00"
        assert amount_range.max_amount == "1000.00"


class TestModelValidation:
    """Test model validation."""
    
    def test_invalid_s3_config(self):
        """Test S3Config validation."""
        with pytest.raises(ValidationError):
            S3Config(
                bucket_name="",  # Empty bucket name
                region="us-west-2"
            )
    
    def test_invalid_time_range(self):
        """Test TimeRange validation."""
        # This should work - no built-in validation for start < end
        time_range = TimeRange(
            start=datetime(2025, 12, 31),
            end=datetime(2025, 1, 1)
        )
        assert time_range.start > time_range.end
    
    def test_optional_fields(self):
        """Test models with optional fields."""
        # Minimal BatchInfo
        batch = BatchInfo(
            batch_id="BATCH-123",
            database_name="test_db",
            table_names=[],
            transaction_count=0,
            merkle_root="",
            timestamp=datetime.now(),
            s3_location=S3Location(
                bucket="test",
                key="key",
                region="us-west-2"
            ),
            size_bytes=0
        )
        
        assert batch.batch_id == "BATCH-123"
        assert len(batch.table_names) == 0
        
        # Minimal VerificationHints
        hints = VerificationHints()
        assert hints.batch_id is None
        assert hints.table_name is None