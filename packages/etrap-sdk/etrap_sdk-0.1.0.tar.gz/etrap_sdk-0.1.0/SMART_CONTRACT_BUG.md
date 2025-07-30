# Potential NEAR Smart Contract Bug Investigation

## Issue Summary
The ETRAP smart contract methods `get_batches_by_table` and `get_batches_by_database` appear to return incomplete results, causing transaction verification failures when using these optimization hints.

## Observed Behavior

### Contract Method: `get_batches_by_table`
- **Expected**: Return all batches containing transactions for the specified table
- **Actual**: Returns only 1 batch even when multiple batches exist for the table
- **Example**: 
  - Table `financial_transactions` has 41 batches
  - Contract returns only `BATCH-2025-07-05-eda7fe02` (the most recent)
  - Missing `BATCH-2025-07-05-1bc51d96` and 39 others

### Contract Method: `get_batches_by_database`
- **Expected**: Return all batches for the specified database
- **Actual**: Returns limited results (often just 1-3 batches)
- **Example**:
  - Database `etrapdb` has many batches
  - Contract returns only the most recent batch(es)

### Contract Method: `get_batches_by_time_range` (Working Correctly)
- **Expected**: Return all batches within the specified time range
- **Actual**: Returns complete results as expected
- **Example**:
  - Time range covering 7 days returned 18 batches correctly
  - This method appears to be implemented correctly in the contract

## Impact
When the SDK relied on these contract methods:
- Transactions in older batches couldn't be verified
- `verify_batch` would fail for 9 out of 10 transactions
- Individual `verify_transaction` calls would work (different search path)

## Current Workaround
The SDK now bypasses these contract methods entirely:
```python
# In client.py
async def _get_batches_by_table(self, table_name: str, limit: int) -> List[BatchInfo]:
    # Always use fallback logic instead of contract method
    all_batches = await self._get_recent_batches(limit * 2)
    # Filter locally
    return [b for b in all_batches if table_name in b.table_names][:limit]
```

## Evidence Collected

### Direct Contract Queries
```python
# Contract returned 1 batch for table query
result = await client.near_account.view_function(
    "lunaris.testnet",
    "get_batches_by_table",
    {"table_name": "financial_transactions", "limit": 50}
)
# Result: Only BATCH-2025-07-05-eda7fe02

# But get_recent_batches returns many
result = await client.near_account.view_function(
    "lunaris.testnet", 
    "get_recent_batches",
    {"limit": 100}
)
# Result: 41 batches for the same table
```

## Hypotheses

1. **Intentional Design**: Contract might limit results for gas optimization
2. **Index Limitation**: The table/database indices might have size limits
3. **Query Bug**: The contract's filtering logic might be incorrect
4. **State Issue**: Contract state might be corrupted or incomplete

## Investigation Steps

1. **Review Contract Code**:
   - Check implementation of `get_batches_by_table`
   - Look for any hardcoded limits or early returns
   - Verify index data structures

2. **Check Contract State**:
   - Query the indices directly if possible
   - Verify all batches are properly indexed

3. **Test Different Scenarios**:
   - Try different tables/databases
   - Test with various limit values
   - Check if issue is consistent or intermittent

4. **Gas Analysis**:
   - Measure gas usage for full results
   - Determine if limitation is for gas optimization

## Long-term Solutions

1. **Fix Contract**: Update the contract methods to return complete results
2. **Pagination**: Implement proper pagination in contract methods
3. **Alternative Indices**: Create more efficient indexing structures
4. **SDK Enhancement**: Add smarter caching to reduce contract queries
