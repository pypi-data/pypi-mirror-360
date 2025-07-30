"""
Pytest configuration and fixtures for ETRAP SDK tests.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, List

from etrap_sdk import (
    ETRAPClient, S3Config, BatchInfo, S3Location,
    MerkleTree, TransactionRecord
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_s3_config():
    """Mock S3 configuration."""
    return S3Config(
        bucket_name="test-etrap-bucket",
        region="us-west-2",
        access_key_id="test-key",
        secret_access_key="test-secret"
    )


@pytest.fixture
def mock_client(mock_s3_config):
    """Create a mock ETRAP client."""
    return ETRAPClient(
        organization_id="test",
        network="testnet",
        s3_config=mock_s3_config
    )


@pytest.fixture
def sample_transaction():
    """Sample transaction data."""
    return {
        "id": 123,
        "account_id": "ACC999",
        "amount": 999.99,
        "type": "C",
        "created_at": "2025-06-14 07:10:55.461133",
        "reference": "TEST-123"
    }


@pytest.fixture
def normalized_transaction():
    """Normalized transaction data."""
    return {
        "id": "123",
        "account_id": "ACC999",
        "amount": "999.99",
        "type": "C",
        "created_at": "2025-06-14T07:10:55.461",
        "reference": "TEST-123"
    }


@pytest.fixture
def sample_batch_info():
    """Sample batch info."""
    return BatchInfo(
        batch_id="BATCH-2025-06-14-test123",
        database_name="test_db",
        table_names=["financial_transactions"],
        transaction_count=100,
        merkle_root="abcd1234567890",
        timestamp=datetime(2025, 6, 14, 7, 10, 55),
        s3_location=S3Location(
            bucket="test-etrap-bucket",
            key="test_db/BATCH-2025-06-14-test123/",
            region="us-west-2"
        ),
        size_bytes=50000
    )


@pytest.fixture
def sample_batch_data():
    """Sample batch data from S3."""
    return {
        "batch_id": "BATCH-2025-06-14-test123",
        "database_name": "test_db",
        "merkle_tree": {
            "algorithm": "sha256",
            "root": "abcd1234567890",
            "height": 7,
            "nodes": {
                "0-0": {"hash": "tx0_hash", "data": {"tx_id": "tx-0"}},
                "0-1": {"hash": "tx1_hash", "data": {"tx_id": "tx-1"}},
                "1-0": {"hash": "node1_hash"},
                "1-1": {"hash": "node2_hash"}
            },
            "proof_index": {
                "tx-0": {
                    "proof_path": ["tx1_hash", "node2_hash"],
                    "sibling_positions": ["right", "right"]
                }
            }
        },
        "transactions": [
            {
                "tx_id": "tx-0",
                "metadata": {
                    "hash": "test_tx_hash_123",
                    "transaction_id": "tx-0",
                    "timestamp": 1734161455461,
                    "operation_type": "INSERT",
                    "database_name": "test_db",
                    "table_affected": "financial_transactions"
                }
            }
        ],
        "indices": {
            "by_timestamp": {"1734161455461": ["0"]},
            "by_operation": {"INSERT": ["0"]},
            "by_date": {"2025-06-14": ["0"]}
        }
    }


@pytest.fixture
def mock_near_response():
    """Mock NEAR contract response."""
    return {
        "token_id": "BATCH-2025-06-14-test123",
        "metadata": {
            "title": "ETRAP Batch NFT",
            "description": "Batch of CDC transactions",
            "extra": {
                "database_name": "test_db",
                "table_names": ["financial_transactions"],
                "timestamp": 1734161455461,
                "tx_count": 100,
                "merkle_root": "abcd1234567890",
                "s3_location": {
                    "bucket": "test-etrap-bucket",
                    "key": "test_db/BATCH-2025-06-14-test123/",
                    "region": "us-west-2"
                },
                "size_bytes": 50000
            }
        }
    }