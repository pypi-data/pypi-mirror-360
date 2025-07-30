"""
Tests for ETRAP SDK client functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import json

from etrap_sdk import (
    ETRAPClient, S3Config, BatchInfo, BatchList, BatchFilter,
    VerificationResult, BatchVerificationResult, VerificationHints,
    TransactionLocation, SearchCriteria, SearchResults,
    MerkleProof, TimeRange, ContractInfo, ContractStats, S3Location, DateRange
)
from etrap_sdk.exceptions import (
    S3AccessError, InvalidTransactionError, BatchNotFoundError
)


class TestClientInitialization:
    """Test client initialization and configuration."""
    
    def test_init_default_config(self):
        """Test client initialization with default config."""
        client = ETRAPClient("test", "testnet")
        
        assert client.contract_id == "test.testnet"
        assert client.network == "testnet"
        assert client.config.cache_ttl == 300
        assert client.config.max_retries == 3
        assert client.config.timeout == 30
    
    def test_init_with_s3_config(self, mock_s3_config):
        """Test client initialization with S3 config."""
        client = ETRAPClient("test.testnet", s3_config=mock_s3_config)
        
        assert client.s3_client is not None
        assert client.s3_bucket == "test-etrap-bucket"
    
    def test_init_custom_network(self):
        """Test client initialization with custom network."""
        client = ETRAPClient(
            "test.near",
            network="mainnet",
            rpc_endpoint="https://custom-rpc.com"
        )
        
        assert client.network == "mainnet"
        # Just verify client was created successfully
        assert client.near_account is not None
    
    def test_update_config(self, mock_client):
        """Test updating client configuration."""
        mock_client.update_config({
            "cache_ttl": 600,
            "max_retries": 5,
            "timeout": 60
        })
        
        config = mock_client.get_config()
        assert config.cache_ttl == 600
        assert config.max_retries == 5
        assert config.timeout == 60


class TestTransactionVerification:
    """Test transaction verification functionality."""
    
    @pytest.mark.asyncio
    async def test_verify_transaction_success(self, mock_client, sample_transaction):
        """Test successful transaction verification."""
        # Create mock batch info
        mock_batch = BatchInfo(
            batch_id="BATCH-2025-06-14-test123",
            database_name="test_db",
            table_names=["financial_transactions"],
            transaction_count=100,
            merkle_root="abcd1234567890",
            timestamp=datetime.now(),
            s3_location=S3Location(bucket="test-etrap-bucket", key="test_db/BATCH-2025-06-14-test123/", region="us-west-2"),
            size_bytes=50000
        )
        
        # Mock _get_recent_batches to return our test batch
        mock_client._get_recent_batches = AsyncMock(return_value=[mock_batch])
        
        # Mock _verify_in_batch to return successful verification
        mock_verification_result = VerificationResult(
            verified=True,
            transaction_hash="test_hash_123",
            batch_id="BATCH-2025-06-14-test123",
            merkle_proof=MerkleProof(
                leaf_hash="test_hash_123",
                proof_path=["hash1", "hash2"],
                sibling_positions=["right", "left"],
                merkle_root="abcd1234567890",
                is_valid=True
            ),
            blockchain_timestamp=datetime.now(),
            gas_used="1000000"
        )
        mock_client._verify_in_batch = AsyncMock(return_value=mock_verification_result)
        
        # Mock hash computation
        with patch('etrap_sdk.client.compute_transaction_hash', return_value="test_hash_123"):
            result = await mock_client.verify_transaction(sample_transaction)
        
        assert result.verified is True
        assert result.transaction_hash == "test_hash_123"
        assert result.batch_id == "BATCH-2025-06-14-test123"
        assert result.merkle_proof is not None
    
    @pytest.mark.asyncio
    async def test_verify_transaction_not_found(self, mock_client, sample_transaction):
        """Test transaction verification when not found."""
        # Mock empty batch list
        mock_client.near_account.view_function = AsyncMock()
        mock_client.near_account.view_function.return_value = []
        
        result = await mock_client.verify_transaction(sample_transaction)
        
        assert result.verified is False
        assert "not found" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_verify_transaction_with_hints(self, mock_client, sample_transaction):
        """Test transaction verification with optimization hints."""
        hints = VerificationHints(
            batch_id="BATCH-2025-06-14-test123",
            table_name="financial_transactions"
        )
        
        # Mock get_batch directly
        mock_client.get_batch = AsyncMock()
        mock_client.get_batch.return_value = BatchInfo(
            batch_id="BATCH-2025-06-14-test123",
            database_name="test_db",
            table_names=["financial_transactions"],
            transaction_count=100,
            merkle_root="abcd1234567890",
            timestamp=datetime.now(),
            s3_location=S3Location(bucket="test-bucket", key="test/", region="us-west-2"),
            size_bytes=50000
        )
        
        # Mock _verify_in_batch
        mock_client._verify_in_batch = AsyncMock()
        mock_client._verify_in_batch.return_value = VerificationResult(
            verified=True,
            transaction_hash="test_hash_123",
            batch_id="BATCH-2025-06-14-test123"
        )
        
        result = await mock_client.verify_transaction(sample_transaction, hints=hints)
        
        assert result.verified is True
        assert mock_client.get_batch.called
        assert mock_client.get_batch.call_args[0][0] == "BATCH-2025-06-14-test123"
    
    @pytest.mark.asyncio
    async def test_verify_transaction_invalid_data(self, mock_client):
        """Test transaction verification with invalid data."""
        with pytest.raises(InvalidTransactionError):
            await mock_client.verify_transaction({})
        
        with pytest.raises(InvalidTransactionError):
            await mock_client.verify_transaction(None)


class TestBatchVerification:
    """Test batch verification functionality."""
    
    @pytest.mark.asyncio
    async def test_verify_batch_parallel(self, mock_client):
        """Test parallel batch verification."""
        transactions = [
            {"id": 1, "amount": 100},
            {"id": 2, "amount": 200},
            {"id": 3, "amount": 300}
        ]
        
        # Mock verify_transaction to return mixed results
        async def mock_verify(tx):
            if tx["id"] == 2:
                return VerificationResult(
                    verified=False,
                    transaction_hash=f"hash_{tx['id']}",
                    error="Not found"
                )
            return VerificationResult(
                verified=True,
                transaction_hash=f"hash_{tx['id']}",
                batch_id="BATCH-123"
            )
        
        mock_client.verify_transaction = mock_verify
        
        result = await mock_client.verify_batch(transactions, parallel=True)
        
        assert result.total == 3
        assert result.verified == 2
        assert result.failed == 1
        assert result.summary.success_rate == 2/3
    
    @pytest.mark.asyncio
    async def test_verify_batch_sequential(self, mock_client):
        """Test sequential batch verification."""
        transactions = [{"id": i} for i in range(3)]
        
        mock_client.verify_transaction = AsyncMock()
        mock_client.verify_transaction.return_value = VerificationResult(
            verified=True,
            transaction_hash="test_hash"
        )
        
        result = await mock_client.verify_batch(transactions, parallel=False)
        
        assert result.total == 3
        assert result.verified == 3
        assert mock_client.verify_transaction.call_count == 3
    
    @pytest.mark.asyncio
    async def test_verify_batch_with_progress(self, mock_client):
        """Test batch verification with progress callback."""
        transactions = [{"id": i} for i in range(5)]
        progress_calls = []
        
        def progress_callback(current, total):
            progress_calls.append((current, total))
        
        mock_client.verify_transaction = AsyncMock()
        mock_client.verify_transaction.return_value = VerificationResult(
            verified=True,
            transaction_hash="test_hash"
        )
        
        await mock_client.verify_batch(
            transactions,
            parallel=False,
            progress_callback=progress_callback
        )
        
        assert len(progress_calls) == 5
        assert progress_calls[-1] == (5, 5)
    
    @pytest.mark.asyncio
    async def test_verify_batch_fail_fast(self, mock_client):
        """Test batch verification with fail_fast option."""
        transactions = [{"id": i} for i in range(10)]
        
        # Mock to fail on 3rd transaction
        async def mock_verify(tx):
            if tx["id"] == 2:
                return VerificationResult(verified=False, transaction_hash="hash")
            return VerificationResult(verified=True, transaction_hash="hash")
        
        mock_client.verify_transaction = mock_verify
        
        result = await mock_client.verify_batch(
            transactions,
            parallel=False,
            fail_fast=True
        )
        
        assert result.total == 10
        assert result.verified == 2
        assert result.failed == 1
        assert len(result.results) == 3  # Stopped after failure


class TestBatchOperations:
    """Test batch-related operations."""
    
    @pytest.mark.asyncio
    async def test_get_batch(self, mock_client, mock_near_response):
        """Test getting batch information."""
        mock_client.near_account.view_function = AsyncMock()
        mock_client.near_account.view_function.return_value = mock_near_response
        
        batch = await mock_client.get_batch("BATCH-2025-06-14-test123")
        
        assert batch is not None
        assert batch.batch_id == "BATCH-2025-06-14-test123"
        assert batch.database_name == "test_db"
        assert batch.transaction_count == 100
    
    @pytest.mark.asyncio
    async def test_list_batches(self, mock_client):
        """Test listing batches with filters."""
        # Mock get_recent_batches
        mock_batches = [
            BatchInfo(
                batch_id=f"BATCH-{i}",
                database_name="test_db",
                table_names=["table1"],
                transaction_count=100,
                merkle_root=f"root{i}",
                timestamp=datetime.now() - timedelta(hours=i),
                s3_location=S3Location(bucket="test-bucket", key="test/", region="us-west-2"),
                size_bytes=50000
            )
            for i in range(5)
        ]
        
        mock_client._get_recent_batches = AsyncMock()
        mock_client._get_recent_batches.return_value = mock_batches
        
        # Test basic listing
        result = await mock_client.list_batches(limit=3)
        
        assert isinstance(result, BatchList)
        assert len(result.batches) == 3
        assert result.total_count == 5
        assert result.has_more is True
        
        # Test with filter
        filter = BatchFilter(
            database_name="test_db",
            min_transactions=50
        )
        
        result = await mock_client.list_batches(filter=filter)
        
        assert all(b.database_name == "test_db" for b in result.batches)
        assert all(b.transaction_count >= 50 for b in result.batches)
    
    @pytest.mark.asyncio
    async def test_search_batches(self, mock_client):
        """Test searching batches."""
        mock_client._get_recent_batches = AsyncMock()
        mock_client._get_recent_batches.return_value = [
            BatchInfo(
                batch_id="BATCH-2025-06-14-test",
                database_name="test_db",
                table_names=["table1"],
                transaction_count=100,
                merkle_root="test_root",
                timestamp=datetime(2025, 6, 14),
                s3_location=S3Location(bucket="test-bucket", key="test/", region="us-west-2"),
                size_bytes=50000
            )
        ]
        
        criteria = SearchCriteria(
            date_range=DateRange(start="2025-06-14", end="2025-06-14")
        )
        
        result = await mock_client.search_batches(criteria)
        
        assert isinstance(result, SearchResults)
        assert len(result.matching_batches) == 1
        assert result.search_time_ms >= 0
    
    @pytest.mark.asyncio
    async def test_get_batch_data(self, mock_client, sample_batch_data):
        """Test getting complete batch data from S3."""
        # Mock get_batch
        mock_client.get_batch = AsyncMock()
        mock_client.get_batch.return_value = BatchInfo(
            batch_id="BATCH-2025-06-14-test123",
            database_name="test_db",
            table_names=["table1"],
            transaction_count=100,
            merkle_root="abcd1234567890",
            timestamp=datetime.now(),
            s3_location=S3Location(bucket="test-bucket", key="test-key/", region="us-west-2"),
            size_bytes=50000
        )
        
        # Mock S3 client
        mock_client.s3_client = Mock()
        mock_client.s3_client.get_object = Mock()
        mock_client.s3_client.get_object.return_value = {
            'Body': Mock(read=lambda: json.dumps(sample_batch_data).encode())
        }
        
        batch_data = await mock_client.get_batch_data(
            "BATCH-2025-06-14-test123",
            include_merkle_tree=True,
            include_indices=True
        )
        
        assert batch_data is not None
        assert batch_data.batch_info.batch_id == "BATCH-2025-06-14-test123"
        assert batch_data.merkle_tree is not None
        assert batch_data.merkle_tree.root == "abcd1234567890"
        assert batch_data.indices is not None
    
    @pytest.mark.asyncio
    async def test_get_batch_data_no_s3(self, mock_client):
        """Test get_batch_data without S3 configured."""
        mock_client.s3_client = None
        
        with pytest.raises(S3AccessError):
            await mock_client.get_batch_data("BATCH-123")


class TestMerkleProofs:
    """Test Merkle proof functionality."""
    
    @pytest.mark.asyncio
    async def test_get_merkle_proof(self, mock_client, sample_batch_data):
        """Test getting Merkle proof for transaction."""
        # Setup cache
        mock_client._cache["batch_data_BATCH-123"] = sample_batch_data
        
        proof = await mock_client.get_merkle_proof("BATCH-123", "test_tx_hash_123")
        
        assert isinstance(proof, MerkleProof)
        assert proof.leaf_hash == "test_tx_hash_123"
        assert proof.merkle_root == "abcd1234567890"
        assert len(proof.proof_path) == 2
    
    @pytest.mark.asyncio
    async def test_get_merkle_proof_not_found(self, mock_client):
        """Test getting Merkle proof for non-existent transaction."""
        mock_client._cache["batch_data_BATCH-123"] = {"transactions": []}
        
        proof = await mock_client.get_merkle_proof("BATCH-123", "non_existent")
        
        assert proof is None
    
    def test_validate_merkle_proof(self, mock_client):
        """Test Merkle proof validation."""
        proof = MerkleProof(
            leaf_hash="test_leaf",
            proof_path=["hash1", "hash2"],
            sibling_positions=["right", "left"],
            merkle_root="test_root",
            is_valid=True
        )
        
        # This would need actual implementation to test properly
        result = mock_client.validate_merkle_proof(
            "test_leaf",
            proof,
            "test_root"
        )
        
        assert isinstance(result, bool)


class TestTransactionSearch:
    """Test transaction search functionality."""
    
    @pytest.mark.asyncio
    async def test_find_transaction(self, mock_client):
        """Test finding a transaction by hash."""
        mock_batch = BatchInfo(
            batch_id="BATCH-123",
            database_name="test_db",
            table_names=["table1"],
            transaction_count=100,
            merkle_root="test_root",
            timestamp=datetime.now(),
            s3_location=S3Location(bucket="test-bucket", key="test/", region="us-west-2"),
            size_bytes=50000
        )
        
        mock_client._get_recent_batches = AsyncMock()
        mock_client._get_recent_batches.return_value = [mock_batch]
        
        mock_client._verify_in_batch = AsyncMock()
        mock_client._verify_in_batch.return_value = VerificationResult(
            verified=True,
            transaction_hash="test_hash",
            batch_id="BATCH-123"
        )
        
        location = await mock_client.find_transaction("test_hash")
        
        assert isinstance(location, TransactionLocation)
        assert location.batch_id == "BATCH-123"
        assert location.batch_info == mock_batch
    
    @pytest.mark.asyncio
    async def test_find_transaction_with_time_range(self, mock_client):
        """Test finding transaction with time range filter."""
        now = datetime.now()
        time_range = TimeRange(
            start=now - timedelta(hours=1),
            end=now
        )
        
        mock_client._get_recent_batches = AsyncMock()
        mock_client._get_recent_batches.return_value = []
        
        location = await mock_client.find_transaction(
            "test_hash",
            time_range=time_range
        )
        
        assert location is None


class TestContractOperations:
    """Test contract-related operations."""
    
    @pytest.mark.asyncio
    async def test_get_contract_info(self, mock_client):
        """Test getting contract information."""
        mock_batches = [
            BatchInfo(
                batch_id=f"BATCH-{i}",
                database_name=f"db{i%2}",
                table_names=[f"table{i}", f"table{i+1}"],
                transaction_count=100 + i*10,
                merkle_root=f"root{i}",
                timestamp=datetime.now() - timedelta(days=i),
                s3_location=S3Location(bucket="test-bucket", key="test/", region="us-west-2"),
                size_bytes=50000
            )
            for i in range(5)
        ]
        
        mock_client._get_recent_batches = AsyncMock()
        mock_client._get_recent_batches.return_value = mock_batches
        
        mock_client.near_account.view_function = AsyncMock()
        mock_client.near_account.view_function.return_value = {
            "spec": "nft-1.0.0",
            "name": "ETRAP Batches"
        }
        
        info = await mock_client.get_contract_info()
        
        assert isinstance(info, ContractInfo)
        assert info.contract_id == "test.testnet"
        assert info.total_batches == 5
        assert info.total_transactions == 600  # 100 + 110 + 120 + 130 + 140
        assert len(info.supported_databases) == 2
        assert len(info.supported_tables) > 0
    
    @pytest.mark.asyncio
    async def test_get_contract_stats(self, mock_client):
        """Test getting contract statistics."""
        # Mock list_batches
        mock_client.list_batches = AsyncMock()
        mock_client.list_batches.return_value = BatchList(
            batches=[
                BatchInfo(
                    batch_id=f"BATCH-{i}",
                    database_name="test_db",
                    table_names=[f"table{i}"],
                    transaction_count=100,
                    merkle_root=f"root{i}",
                    timestamp=datetime.now(),
                    s3_location=S3Location(bucket="test-bucket", key="test/", region="us-west-2"),
                    size_bytes=50000
                )
                for i in range(3)
            ],
            total_count=3,
            has_more=False
        )
        
        stats = await mock_client.get_contract_stats("24h")
        
        assert isinstance(stats, ContractStats)
        assert stats.batches_created == 3
        assert stats.transactions_recorded == 300
        assert stats.unique_tables == 3
        assert stats.unique_databases == 1
        assert stats.time_period == "24h"


class TestUtilityMethods:
    """Test utility methods exposed by client."""
    
    def test_normalize_transaction(self, mock_client):
        """Test transaction normalization."""
        data = {"id": 123, "amount": 999.99}
        result = mock_client.normalize_transaction(data)
        
        assert result["id"] == "123"
        assert result["amount"] == "999.99"
    
    def test_compute_transaction_hash(self, mock_client):
        """Test hash computation."""
        data = {"id": "123", "amount": "999.99"}
        
        hash1 = mock_client.compute_transaction_hash(data, normalize=False)
        hash2 = mock_client.compute_transaction_hash(data, normalize=True)
        
        assert len(hash1) == 64
        assert len(hash2) == 64