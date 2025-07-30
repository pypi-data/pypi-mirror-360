#!/usr/bin/env python3
"""
================================================================================
ETRAP SDK - Data Models Example
================================================================================

This example demonstrates the data structures and models used by the ETRAP SDK
for filtering, searching, and organizing blockchain transaction data.

What this example shows:
- BatchInfo: Metadata about transaction batches stored on blockchain
- S3Location: Configuration for AWS S3 storage of detailed batch data  
- BatchFilter: Criteria for filtering batches by database, table, and time
- SearchCriteria: Parameters for searching transactions by hash and operations
- TransactionFilter: Filters for transactions by account, amount, and type
- TimeRange & DateRange: Time-based constraints for queries
- AmountRange: Numeric range filters for transaction amounts

The example creates instances of each model and displays their properties,
showing how to construct filters and search criteria for the ETRAP SDK.

Usage: python data_models.py

No parameters required - this is a self-contained demonstration.
"""

from datetime import datetime
from etrap_sdk import (
    BatchInfo, S3Location, BatchFilter, TimeRange,
    SearchCriteria, DateRange, TransactionFilter, AmountRange
)


def main():
    # Create a BatchInfo object
    batch = BatchInfo(
        batch_id="BATCH-2025-06-14-abc123",
        database_name="production",
        table_names=["financial_transactions", "audit_logs"],
        transaction_count=1000,
        merkle_root="abcd1234567890",
        timestamp=datetime(2025, 6, 14, 7, 10, 55),
        s3_location=S3Location(
            bucket="etrap-data",
            key="production/BATCH-2025-06-14-abc123/",
            region="us-west-2"
        ),
        size_bytes=500000
    )
    
    print("Batch Information:")
    print(f"  ID: {batch.batch_id}")
    print(f"  Database: {batch.database_name}")
    print(f"  Tables: {', '.join(batch.table_names)}")
    print(f"  Transactions: {batch.transaction_count:,}")
    print(f"  Timestamp: {batch.timestamp}")
    print(f"  S3 Location: s3://{batch.s3_location.bucket}/{batch.s3_location.key}")
    
    # Create filter for querying batches
    batch_filter = BatchFilter(
        database_name="production",
        table_name="financial_transactions",
        time_range=TimeRange(
            start=datetime(2025, 6, 1),
            end=datetime(2025, 6, 30)
        ),
        min_transactions=100
    )
    
    print("\n\nBatch Filter:")
    print(f"  Database: {batch_filter.database_name}")
    print(f"  Table: {batch_filter.table_name}")
    print(f"  Time range: {batch_filter.time_range.start} to {batch_filter.time_range.end}")
    print(f"  Min transactions: {batch_filter.min_transactions}")
    
    # Create search criteria
    search = SearchCriteria(
        transaction_hash="8684c656d2addf8abb8408699d81eeed3576da03254364bc1e9ca614d0eff8ab",
        date_range=DateRange(start="2025-06-14", end="2025-06-14"),
        operation_type=["INSERT", "UPDATE"]
    )
    
    print("\n\nSearch Criteria:")
    print(f"  Transaction hash: {search.transaction_hash}")
    print(f"  Date range: {search.date_range.start} to {search.date_range.end}")
    print(f"  Operations: {', '.join(search.operation_type)}")
    
    # Create transaction filter
    tx_filter = TransactionFilter(
        account_id="ACC999",
        transaction_type="C",
        amount_range=AmountRange(
            min_amount="100.00",
            max_amount="10000.00"
        ),
        operation_types=["INSERT"],
        time_range=TimeRange(
            start=datetime(2025, 6, 14, 0, 0, 0),
            end=datetime(2025, 6, 14, 23, 59, 59)
        )
    )
    
    print("\n\nTransaction Filter:")
    print(f"  Account: {tx_filter.account_id}")
    print(f"  Type: {tx_filter.transaction_type}")
    print(f"  Amount range: ${tx_filter.amount_range.min_amount} - ${tx_filter.amount_range.max_amount}")
    print(f"  Operations: {', '.join(tx_filter.operation_types)}")


if __name__ == "__main__":
    main()