"""
ETRAP SDK Client - Main entry point for the SDK.

This module provides the ETRAPClient class which handles all interactions
with the ETRAP system for transaction verification and audit operations.
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable

import boto3
from py_near import account

from .models import (
    VerificationHints, VerificationResult, BatchVerificationResult,
    BatchInfo, BatchFilter, BatchList, BatchData, SearchCriteria,
    SearchResults, TransactionLocation, TransactionFilter, TransactionHistory,
    ContractInfo, ContractStats, S3Config, ClientConfig, MerkleProof,
    VerificationSummary, S3Location, TimeRange, MerkleTree, BatchIndices,
    TransactionRecord, OperationCounts, NFTInfo
)
from .exceptions import (
    ETRAPError, VerificationError, BatchNotFoundError, NetworkError,
    ContractError, S3AccessError, InvalidTransactionError
)
from .utils import (
    normalize_transaction_data, compute_transaction_hash,
    validate_merkle_proof, parse_timestamp
)


logger = logging.getLogger(__name__)


class ETRAPClient:
    """
    Main client for interacting with the ETRAP system.
    
    This client provides methods for verifying transactions, searching batches,
    and accessing audit trail data stored on NEAR blockchain and S3.
    """
    
    def __init__(
        self,
        organization_id: str,
        network: str = "testnet",
        rpc_endpoint: Optional[str] = None,
        s3_config: Optional[S3Config] = None,
        cache_ttl: int = 300,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Initialize ETRAP client.
        
        Args:
            organization_id: Organization identifier (e.g., 'acme')
            network: NEAR network (testnet/mainnet/localnet)
            rpc_endpoint: Custom RPC endpoint (optional)
            s3_config: S3 configuration for batch data access
            cache_ttl: Cache lifetime in seconds
            max_retries: Retry attempts for network operations
            timeout: Request timeout in seconds
        """
        self.organization_id = organization_id
        self.network = network
        
        # Derive contract ID from organization ID and network
        if network == "mainnet":
            self.contract_id = f"{organization_id}.near"
        else:
            self.contract_id = f"{organization_id}.{network}"
        
        self.config = ClientConfig(
            cache_ttl=cache_ttl,
            max_retries=max_retries,
            timeout=timeout
        )
        
        # Setup NEAR connection
        if not rpc_endpoint:
            rpc_endpoint = self._get_default_rpc_endpoint(network)
        
        self.near_account = account.Account(
            account_id=self.contract_id,
            rpc_addr=rpc_endpoint
        )
        
        # Setup S3 client if configured
        self.s3_client = None
        if s3_config:
            self._setup_s3_client(s3_config)
        
        # Cache for frequently accessed data
        self._cache = {}
        self._cache_timestamps = {}
        
        logger.info(f"ETRAP Client initialized for organization '{organization_id}' (contract: {self.contract_id}, bucket: etrap-{organization_id})")
    
    def _get_default_rpc_endpoint(self, network: str) -> str:
        """Get default RPC endpoint for network."""
        endpoints = {
            "testnet": "https://test.rpc.fastnear.com",  # FastNear RPC (higher rate limits)
            "mainnet": "https://rpc.mainnet.near.org",
            "localnet": "http://localhost:3030"
        }
        return endpoints.get(network, endpoints["testnet"])
    
    def _setup_s3_client(self, s3_config: S3Config):
        """Setup S3 client with provided configuration."""
        session_config = {}
        if s3_config.access_key_id and s3_config.secret_access_key:
            session_config = {
                'aws_access_key_id': s3_config.access_key_id,
                'aws_secret_access_key': s3_config.secret_access_key,
                'region_name': s3_config.region
            }
        
        self.s3_client = boto3.client('s3', **session_config)
        # Use bucket from config if provided, otherwise derive from organization ID
        self.s3_bucket = s3_config.bucket_name or f"etrap-{self.organization_id}"
    
    async def verify_transaction(
        self,
        transaction_data: Dict[str, Any],
        hints: Optional[VerificationHints] = None,
        timeout: Optional[int] = None,
        use_contract_verification: bool = False
    ) -> VerificationResult:
        """
        Verify a single transaction.
        
        Args:
            transaction_data: Transaction to verify
            hints: Optimization hints for faster verification
            timeout: Override default timeout
            use_contract_verification: If True, use smart contract for verification
            
        Returns:
            VerificationResult with verification status and proof
            
        Raises:
            VerificationError: If verification fails
            InvalidTransactionError: If transaction data is invalid
        """
        # Validate transaction data
        if not transaction_data:
            raise InvalidTransactionError("Transaction data cannot be empty")
        
        # Normalize and compute hash
        normalized = normalize_transaction_data(transaction_data)
        tx_hash = compute_transaction_hash(normalized, normalize=False)
        
        logger.debug(f"Verifying transaction with hash: {tx_hash[:16]}...")
        
        try:
            # Search for the transaction
            if hints and hints.batch_id:
                # Direct batch lookup - most specific hint
                logger.debug(f"Using batch hint: {hints.batch_id}")
                batch = await self.get_batch(hints.batch_id)
                if batch:
                    result = await self._verify_in_batch(tx_hash, batch, use_contract_verification, hints.expected_operation if hints else None)
                    if result:
                        return result
                    # If not in the specified batch, don't search further
                    return VerificationResult(
                        verified=False,
                        transaction_hash=tx_hash,
                        error=f"Transaction not found in specified batch {hints.batch_id}"
                    )
            
            # Time range search if provided
            time_range_attempted = False
            if hints and hints.time_range:
                logger.debug(f"Using time range hint: {hints.time_range.start} to {hints.time_range.end}")
                time_range_attempted = True
                try:
                    batches = await self._get_batches_by_time_range(
                        hints.time_range.start,
                        hints.time_range.end,
                        database=hints.database_name if hints else None,
                        limit=100
                    )
                    for batch in batches:
                        try:
                            result = await self._verify_in_batch(tx_hash, batch, use_contract_verification, hints.expected_operation if hints else None)
                            if result:
                                return result
                        except VerificationError:
                            # Skip this batch and continue searching
                            continue
                    
                    # Time range search completed but didn't find transaction
                    logger.debug(f"Time range search found {len(batches)} batches but transaction not verified")
                    
                except Exception as e:
                    logger.warning(f"Time range search failed: {e}")
                
                # If time range specified with other hints, don't fall back to full search
                if hints.table_name or hints.database_name:
                    # Continue to other hint-based searches
                    pass
                else:
                    # Time range was the only hint - fall back to recent batches as safety net
                    # This handles cases where network issues prevent the contract query from completing
                    logger.debug("Time range search incomplete, falling back to recent batches search")
                    recent_batches = await self._get_recent_batches(100)
                    
                    # Filter recent batches by time range for consistency
                    filtered_batches = [
                        b for b in recent_batches 
                        if hints.time_range.start <= b.timestamp <= hints.time_range.end
                    ]
                    
                    logger.debug(f"Fallback found {len(filtered_batches)} batches in time range")
                    
                    for batch in filtered_batches:
                        try:
                            result = await self._verify_in_batch(tx_hash, batch, use_contract_verification, hints.expected_operation if hints else None)
                            if result:
                                return result
                        except VerificationError:
                            # Skip this batch and continue searching
                            continue
                    
                    # Both time range and fallback search failed
                    return VerificationResult(
                        verified=False,
                        transaction_hash=tx_hash,
                        error="Transaction not found in specified time range"
                    )
            
            # Database search if hinted
            if hints and hints.database_name and not hints.time_range:
                logger.debug(f"Using database hint: {hints.database_name}")
                batches = await self._get_batches_by_database(hints.database_name, limit=100)
                for batch in batches:
                    try:
                        result = await self._verify_in_batch(tx_hash, batch, use_contract_verification, hints.expected_operation if hints else None)
                        if result:
                            return result
                    except VerificationError:
                        # Skip this batch and continue searching
                        continue
            
            # Table search if hinted
            if hints and hints.table_name:
                logger.debug(f"Using table hint: {hints.table_name}")
                batches = await self._get_batches_by_table(hints.table_name, limit=50)
                for batch in batches:
                    try:
                        result = await self._verify_in_batch(tx_hash, batch, use_contract_verification, hints.expected_operation if hints else None)
                        if result:
                            return result
                    except VerificationError:
                        # Skip this batch and continue searching
                        continue
            
            # Fall back to recent batches only if no hints provided and time range wasn't attempted
            if not hints or (not any([hints.batch_id, hints.table_name, hints.database_name, hints.time_range]) and not time_range_attempted):
                logger.debug("No hints provided, searching recent batches")
                recent_batches = await self._get_recent_batches(100)
                for batch in recent_batches:
                    try:
                        result = await self._verify_in_batch(tx_hash, batch, use_contract_verification, hints.expected_operation if hints else None)
                        if result:
                            return result
                    except VerificationError:
                        # Skip this batch and continue searching
                        continue
            
            # Not found
            return VerificationResult(
                verified=False,
                transaction_hash=tx_hash,
                error="Transaction not found in blockchain records"
            )
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return VerificationResult(
                verified=False,
                transaction_hash=tx_hash,
                error=str(e)
            )
    
    async def verify_batch(
        self,
        transactions: List[Dict[str, Any]],
        hints: Optional[VerificationHints] = None,
        parallel: bool = True,
        fail_fast: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> BatchVerificationResult:
        """
        Verify multiple transactions.
        
        Args:
            transactions: List of transactions to verify
            hints: Optional optimization hints to speed up verification:
                - batch_id: Direct batch lookup (fastest method)
                - database_name: Limit search to specific database
                - table_name: Limit search to specific table
                - time_range: Search within time range for better performance
                - expected_operation: Expected operation type (INSERT, UPDATE, DELETE)
                  to disambiguate hash collisions between different operations
            parallel: Process transactions in parallel
            fail_fast: Stop on first failure
            progress_callback: Callback for progress updates
            
        Returns:
            BatchVerificationResult with summary and individual results
            
        Note:
            The expected_operation hint is crucial when verifying transactions where
            the same data might appear in both INSERT and DELETE operations, as these
            would produce identical hashes but represent different database events.
        """
        results = []
        start_time = datetime.now()
        
        if parallel:
            # Verify in parallel
            tasks = [
                self.verify_transaction(tx, hints=hints)
                for tx in transactions
            ]
            
            if progress_callback:
                # Track progress
                for i, task in enumerate(asyncio.as_completed(tasks)):
                    result = await task
                    results.append(result)
                    progress_callback(i + 1, len(transactions))
                    
                    if fail_fast and not result.verified:
                        # Cancel remaining tasks
                        break
            else:
                results = await asyncio.gather(*tasks)
        else:
            # Verify sequentially
            for i, tx in enumerate(transactions):
                result = await self.verify_transaction(tx, hints=hints)
                results.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, len(transactions))
                
                if fail_fast and not result.verified:
                    break
        
        # Calculate summary
        verified_count = sum(1 for r in results if r.verified)
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        
        summary = VerificationSummary(
            success_rate=verified_count / len(results) if results else 0,
            average_verification_time_ms=total_time / len(results) if results else 0,
            blockchain_confirmations=verified_count
        )
        
        return BatchVerificationResult(
            total=len(transactions),
            verified=verified_count,
            failed=len(results) - verified_count,
            results=results,
            summary=summary
        )
    
    async def get_batch(self, batch_id: str) -> Optional[BatchInfo]:
        """
        Get information about a specific batch.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            BatchInfo or None if not found
        """
        try:
            # Try direct NFT query first for efficiency
            logger.debug(f"Direct lookup for batch {batch_id}")
            result = await self.near_account.view_function(
                self.contract_id,
                "nft_token",
                {"token_id": batch_id}
            )
            
            # Handle ViewFunctionResult object
            if hasattr(result, 'result'):
                result = result.result
            
            if result:
                batch_info = self._parse_batch_info(result)
                if batch_info:
                    # Try to get enhanced batch summary if available
                    try:
                        summary_result = await self.near_account.view_function(
                            self.contract_id,
                            "get_batch_summary",
                            {"token_id": batch_id}
                        )
                        if hasattr(summary_result, 'result'):
                            summary_result = summary_result.result
                        if summary_result:
                            # Enhance batch info with summary data
                            batch_info.merkle_root = summary_result.get('merkle_root', batch_info.merkle_root)
                            batch_info.size_bytes = summary_result.get('size_bytes', batch_info.size_bytes)
                            batch_info.database_name = summary_result.get('database_name', batch_info.database_name)
                            # Update table names if provided
                            if 'table_names' in summary_result:
                                batch_info.table_names = summary_result.get('table_names', batch_info.table_names)
                    except:
                        pass  # Use basic info if summary not available
                    
                    return batch_info
            
            # If direct lookup fails, try recent batches (for compatibility)
            logger.debug(f"Direct lookup failed, searching recent batches")
            recent_batches = await self._get_recent_batches(20)  # Reduced limit
            for batch in recent_batches:
                if batch.batch_id == batch_id:
                    return batch
            
        except Exception as e:
            logger.debug(f"Error getting batch {batch_id}: {e}")
            # Return None for not found, but raise for actual errors
            if "not found" in str(e).lower() or "NoSuchKey" in str(e):
                return None
            else:
                raise NetworkError(f"Failed to retrieve batch {batch_id}: {e}")
    
    async def list_batches(
        self,
        filter: Optional[BatchFilter] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "timestamp_desc"
    ) -> BatchList:
        """
        List batches with optional filtering.
        
        Args:
            filter: Filter criteria
            limit: Maximum number of results
            offset: Pagination offset
            order_by: Sort order
            
        Returns:
            BatchList with batches and pagination info
        """
        try:
            # Use optimized queries based on filter criteria
            if filter:
                # Use time range query if provided
                if filter.time_range:
                    all_batches = await self._get_batches_by_time_range(
                        filter.time_range.start,
                        filter.time_range.end,
                        database=filter.database_name,
                        limit=min(limit + offset, 1000)
                    )
                # Use database query if only database filter provided
                elif filter.database_name and not filter.table_name:
                    all_batches = await self._get_batches_by_database(
                        filter.database_name,
                        limit=min(limit + offset, 1000)
                    )
                # Use table query if table filter provided
                elif filter.table_name:
                    all_batches = await self._get_batches_by_table(
                        filter.table_name,
                        limit=min(limit + offset, 1000)
                    )
                else:
                    # General query with manual filtering
                    all_batches = await self._get_recent_batches(min(limit + offset, 1000))
            else:
                # No filter, get recent batches
                all_batches = await self._get_recent_batches(min(limit + offset, 1000))
            
            # Apply any additional filters not handled by queries
            filtered_batches = all_batches
            if filter:
                # Apply min_transactions filter if needed
                if filter.min_transactions:
                    filtered_batches = [
                        b for b in filtered_batches 
                        if b.transaction_count >= filter.min_transactions
                    ]
                
                # Apply additional filtering if using combined criteria
                if filter.database_name and filter.table_name and not filter.time_range:
                    # Table query might return batches from other databases
                    filtered_batches = [
                        b for b in filtered_batches 
                        if b.database_name == filter.database_name
                    ]
                
                if filter.time_range:
                    filtered_batches = [
                        b for b in filtered_batches 
                        if filter.time_range.start <= b.timestamp <= filter.time_range.end
                    ]
                
                if filter.min_transactions:
                    filtered_batches = [
                        b for b in filtered_batches 
                        if b.transaction_count >= filter.min_transactions
                    ]
            
            # Sort
            if order_by == "timestamp_desc":
                filtered_batches.sort(key=lambda b: b.timestamp, reverse=True)
            elif order_by == "timestamp_asc":
                filtered_batches.sort(key=lambda b: b.timestamp)
            elif order_by == "size_desc":
                filtered_batches.sort(key=lambda b: b.size_bytes, reverse=True)
            
            # Apply pagination
            total_count = len(filtered_batches)
            paginated_batches = filtered_batches[offset:offset + limit]
            
            return BatchList(
                batches=paginated_batches,
                total_count=total_count,
                has_more=(offset + limit) < total_count
            )
            
        except Exception as e:
            logger.error(f"Error listing batches: {e}")
            return BatchList(batches=[], total_count=0, has_more=False)
    
    async def search_batches(
        self,
        criteria: SearchCriteria,
        max_results: int = 1000
    ) -> SearchResults:
        """
        Search for batches matching criteria.
        
        Args:
            criteria: Search criteria
            max_results: Maximum results to return
            
        Returns:
            SearchResults with matching batches
        """
        start_time = datetime.now()
        matching_batches = []
        
        try:
            # Get recent batches to search
            all_batches = await self._get_recent_batches(max_results)
            
            for batch in all_batches:
                # Check transaction hash
                if criteria.transaction_hash:
                    result = await self._verify_in_batch(criteria.transaction_hash, batch, False)
                    if result and result.verified:
                        matching_batches.append(batch)
                        continue
                
                # Check merkle root
                if criteria.merkle_root and batch.merkle_root == criteria.merkle_root:
                    matching_batches.append(batch)
                    continue
                
                # Check date range
                if criteria.date_range:
                    start_date = datetime.strptime(criteria.date_range.start, "%Y-%m-%d")
                    end_date = datetime.strptime(criteria.date_range.end, "%Y-%m-%d")
                    end_date = end_date.replace(hour=23, minute=59, second=59)
                    
                    if start_date <= batch.timestamp <= end_date:
                        # Check operation type if specified
                        if criteria.operation_type:
                            # Would need to fetch batch data to check operations
                            # For now, include the batch
                            matching_batches.append(batch)
                        else:
                            matching_batches.append(batch)
                
                if len(matching_batches) >= max_results:
                    break
            
            search_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return SearchResults(
                matching_batches=matching_batches[:max_results],
                search_time_ms=search_time_ms
            )
            
        except Exception as e:
            logger.error(f"Error searching batches: {e}")
            return SearchResults(matching_batches=[], search_time_ms=0)
    
    async def get_batch_data(
        self,
        batch_id: str,
        include_merkle_tree: bool = True,
        include_indices: bool = False,
        decrypt: bool = False
    ) -> Optional[BatchData]:
        """
        Get complete batch data from S3.
        
        Args:
            batch_id: Batch identifier
            include_merkle_tree: Include Merkle tree data
            include_indices: Include batch indices
            decrypt: Decrypt data if encrypted
            
        Returns:
            BatchData or None if not found
            
        Raises:
            S3AccessError: If S3 access fails
        """
        if not self.s3_client:
            raise S3AccessError("S3 client not configured")
        
        # Get batch info first
        batch_info = await self.get_batch(batch_id)
        if not batch_info:
            return None
        
        try:
            # Download batch data from S3
            s3_key = f"{batch_info.s3_location.key}batch-data.json"
            logger.debug(f"Fetching from S3: bucket={batch_info.s3_location.bucket}, key={s3_key}")
            
            try:
                response = self.s3_client.get_object(
                    Bucket=batch_info.s3_location.bucket,
                    Key=s3_key
                )
            except Exception as e:
                if "NoSuchKey" in str(e):
                    # Fallback: try the correct CDC agent path structure
                    table_name = batch_info.table_names[0] if batch_info.table_names else 'unknown'
                    fallback_key = f"{batch_info.database_name}/{table_name}/{batch_id}/batch-data.json"
                    logger.debug(f"Primary path failed, trying fallback: {fallback_key}")
                    
                    response = self.s3_client.get_object(
                        Bucket=batch_info.s3_location.bucket,
                        Key=fallback_key
                    )
                else:
                    raise
            
            batch_json = json.loads(response['Body'].read())
            
            # Parse Merkle tree if requested
            merkle_tree = None
            if include_merkle_tree and 'merkle_tree' in batch_json:
                mt = batch_json['merkle_tree']
                merkle_tree = MerkleTree(
                    algorithm=mt.get('algorithm', 'sha256'),
                    root=mt.get('root', ''),
                    height=mt.get('height', 0),
                    nodes=mt.get('nodes', []),
                    proof_index=mt.get('proof_index', {})
                )
            
            # Parse indices if requested
            indices = None
            if include_indices and 'indices' in batch_json:
                idx = batch_json['indices']
                indices = BatchIndices(
                    by_timestamp=idx.get('by_timestamp', {}),
                    by_operation=idx.get('by_operation', {}),
                    by_date=idx.get('by_date', {})
                )
            
            # Compute operation counts from batch data
            operation_counts = None
            if 'transactions' in batch_json:
                # Try to use efficient indices-based counting first
                if 'indices' in batch_json and 'by_operation' in batch_json['indices']:
                    by_operation = batch_json['indices']['by_operation']
                    operation_counts = OperationCounts(
                        inserts=len(by_operation.get('INSERT', [])),
                        updates=len(by_operation.get('UPDATE', [])),
                        deletes=len(by_operation.get('DELETE', []))
                    )
                else:
                    # Fallback: count by iterating through transactions
                    inserts = updates = deletes = 0
                    for tx in batch_json['transactions']:
                        op_type = tx.get('metadata', {}).get('operation_type', '')
                        if op_type == 'INSERT':
                            inserts += 1
                        elif op_type == 'UPDATE':
                            updates += 1
                        elif op_type == 'DELETE':
                            deletes += 1
                    
                    operation_counts = OperationCounts(
                        inserts=inserts,
                        updates=updates,
                        deletes=deletes
                    )
            
            # Store raw batch data for transaction access
            self._cache[f"batch_data_{batch_id}"] = batch_json
            self._cache_timestamps[f"batch_data_{batch_id}"] = datetime.now()
            
            return BatchData(
                batch_info=batch_info,
                merkle_tree=merkle_tree,
                transaction_count=len(batch_json.get('transactions', [])),
                indices=indices,
                operation_counts=operation_counts
            )
            
        except Exception as e:
            # Create a more descriptive error that can be caught appropriately
            if "NoSuchKey" in str(e):
                raise S3AccessError(f"Batch data not found in S3: {e}", 
                                  bucket=batch_info.s3_location.bucket,
                                  key=s3_key)
            else:
                raise S3AccessError(f"Failed to get batch data: {e}", 
                                  bucket=batch_info.s3_location.bucket,
                                  key=s3_key)
    
    async def get_merkle_proof(
        self,
        batch_id: str,
        transaction_hash: str
    ) -> Optional[MerkleProof]:
        """
        Get Merkle proof for a transaction.
        
        Args:
            batch_id: Batch containing the transaction
            transaction_hash: Transaction hash
            
        Returns:
            MerkleProof or None if not found
        """
        # Check cache first
        cache_key = f"batch_data_{batch_id}"
        if cache_key in self._cache:
            batch_json = self._cache[cache_key]
        else:
            # Get batch data
            batch_data = await self.get_batch_data(batch_id, include_merkle_tree=True)
            if not batch_data or not batch_data.merkle_tree:
                return None
            batch_json = self._cache.get(cache_key)
            if not batch_json:
                return None
        
        # Find transaction by hash
        transaction_index = None
        for i, tx in enumerate(batch_json.get('transactions', [])):
            if tx.get('metadata', {}).get('hash') == transaction_hash:
                transaction_index = i
                break
        
        if transaction_index is None:
            return None
        
        # Extract proof from merkle tree
        merkle_tree = batch_json.get('merkle_tree', {})
        proof_index = merkle_tree.get('proof_index', {})
        
        # Get proof for this transaction
        tx_key = f"tx-{transaction_index}"
        if tx_key not in proof_index:
            return None
        
        proof_data = proof_index[tx_key]
        
        # Get total transaction count to handle edge cases
        total_transactions = len(batch_json.get('transactions', []))
        
        # Validate the proof
        is_valid = self._validate_merkle_proof_with_context(
            transaction_hash,
            proof_data.get('proof_path', []),
            proof_data.get('sibling_positions', []),
            merkle_tree.get('root', ''),
            transaction_index,
            total_transactions
        )
        
        return MerkleProof(
            leaf_hash=transaction_hash,
            proof_path=proof_data.get('proof_path', []),
            sibling_positions=proof_data.get('sibling_positions', []),
            merkle_root=merkle_tree.get('root', ''),
            is_valid=is_valid
        )
    
    async def find_transaction(
        self,
        transaction_hash: str,
        search_depth: int = 100,
        time_range: Optional[TimeRange] = None
    ) -> Optional[TransactionLocation]:
        """
        Find a transaction by its hash.
        
        Args:
            transaction_hash: Transaction hash to find
            search_depth: Number of recent batches to search (max 100 due to contract limit)
            time_range: Optional time range to limit search
            
        Returns:
            TransactionLocation or None if not found
        """
        # Warn about contract limitations
        if search_depth > 100:
            logger.warning(f"Requested search_depth={search_depth} exceeds contract limit of 100. Only 100 recent batches will be searched.")
        
        # Get recent batches
        batches = await self._get_recent_batches(search_depth)
        
        # Filter by time range if provided
        if time_range:
            batches = [
                b for b in batches 
                if time_range.start <= b.timestamp <= time_range.end
            ]
        
        # Search each batch
        for batch in batches:
            # Check if transaction might be in this batch (optimization)
            result = await self._verify_in_batch(transaction_hash, batch, False)
            if result and result.verified:
                # Get position in batch
                cache_key = f"batch_data_{batch.batch_id}"
                if cache_key in self._cache:
                    batch_json = self._cache[cache_key]
                    for i, tx in enumerate(batch_json.get('transactions', [])):
                        if tx.get('metadata', {}).get('hash') == transaction_hash:
                            return TransactionLocation(
                                batch_id=batch.batch_id,
                                position=i,
                                batch_info=batch
                            )
                else:
                    # Position 0 if we can't determine exact position
                    return TransactionLocation(
                        batch_id=batch.batch_id,
                        position=0,
                        batch_info=batch
                    )
        
        return None
    
    async def get_transaction_history(
        self,
        filter: TransactionFilter,
        limit: int = 1000
    ) -> TransactionHistory:
        """
        Get transaction history matching filter.
        
        Args:
            filter: Filter criteria
            limit: Maximum transactions to return
            
        Returns:
            TransactionHistory with matching transactions
        """
        transactions = []
        start_time = None
        end_time = None
        
        try:
            # Get batches that might contain matching transactions
            batch_filter = BatchFilter()
            if filter.time_range:
                batch_filter.time_range = filter.time_range
                start_time = filter.time_range.start
                end_time = filter.time_range.end
            
            batch_list = await self.list_batches(batch_filter, limit=100)
            
            # Search through batches
            for batch in batch_list.batches:
                if len(transactions) >= limit:
                    break
                
                # Get batch data
                try:
                    batch_data = await self.get_batch_data(batch.batch_id)
                    if not batch_data:
                        continue
                    
                    # Get cached batch JSON
                    cache_key = f"batch_data_{batch.batch_id}"
                    batch_json = self._cache.get(cache_key, {})
                    
                    # Filter transactions
                    for tx in batch_json.get('transactions', []):
                        metadata = tx.get('metadata', {})
                        
                        # Apply filters
                        if filter.operation_types:
                            if metadata.get('operation_type') not in filter.operation_types:
                                continue
                        
                        # For account_id and amount filtering, we'd need the actual
                        # transaction data which is not stored (privacy by design)
                        # So we can only filter by metadata
                        
                        # Create transaction record
                        tx_record = TransactionRecord(
                            transaction_id=metadata.get('transaction_id', ''),
                            timestamp=datetime.fromtimestamp(metadata.get('timestamp', 0) / 1000),
                            operation_type=metadata.get('operation_type', ''),
                            database_name=metadata.get('database_name', ''),
                            table_affected=metadata.get('table_affected', ''),
                            transaction_hash=metadata.get('hash', ''),
                            metadata=metadata
                        )
                        
                        transactions.append(tx_record)
                        
                        if len(transactions) >= limit:
                            break
                            
                except Exception as e:
                    logger.error(f"Error processing batch {batch.batch_id}: {e}")
                    continue
            
            # Determine time range covered
            if transactions:
                if not start_time:
                    start_time = min(t.timestamp for t in transactions)
                if not end_time:
                    end_time = max(t.timestamp for t in transactions)
            else:
                start_time = end_time = datetime.now()
            
            return TransactionHistory(
                transactions=transactions[:limit],
                total_found=len(transactions),
                time_range_covered=TimeRange(start=start_time, end=end_time)
            )
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return TransactionHistory(
                transactions=[],
                total_found=0,
                time_range_covered=TimeRange(start=datetime.now(), end=datetime.now())
            )
    
    async def get_contract_info(self) -> ContractInfo:
        """
        Get information about the smart contract.
        
        Returns:
            ContractInfo with contract details
        """
        try:
            # Get contract metadata if available
            metadata = await self.near_account.view_function(
                self.contract_id,
                "nft_metadata",
                {}
            )
            
            # Handle ViewFunctionResult object
            if hasattr(metadata, 'result'):
                metadata = metadata.result
            
            # Get recent batches to determine stats
            recent_batches = await self._get_recent_batches(1000)
            
            # Calculate statistics
            total_batches = len(recent_batches)
            total_transactions = sum(b.transaction_count for b in recent_batches)
            
            # Extract unique tables and databases
            databases = set()
            tables = set()
            earliest = None
            latest = None
            
            for batch in recent_batches:
                databases.add(batch.database_name)
                tables.update(batch.table_names)
                
                if not earliest or batch.timestamp < earliest:
                    earliest = batch.timestamp
                if not latest or batch.timestamp > latest:
                    latest = batch.timestamp
            
            return ContractInfo(
                contract_id=self.contract_id,
                total_batches=total_batches,
                total_transactions=total_transactions,
                earliest_batch=earliest or datetime.now(),
                latest_batch=latest or datetime.now(),
                supported_tables=sorted(list(tables)),
                supported_databases=sorted(list(databases))
            )
            
        except Exception as e:
            logger.error(f"Error getting contract info: {e}")
            # Return minimal info
            return ContractInfo(
                contract_id=self.contract_id,
                total_batches=0,
                total_transactions=0,
                earliest_batch=datetime.now(),
                latest_batch=datetime.now(),
                supported_tables=[],
                supported_databases=[]
            )
    
    async def get_contract_stats(
        self,
        time_period: Optional[str] = "24h"
    ) -> ContractStats:
        """
        Get contract statistics.
        
        Args:
            time_period: Time period for stats (1h/24h/7d/30d/all)
            
        Returns:
            ContractStats with usage statistics
        """
        try:
            # Calculate time range
            end_time = datetime.now()
            if time_period == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_period == "24h":
                start_time = end_time - timedelta(days=1)
            elif time_period == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_period == "30d":
                start_time = end_time - timedelta(days=30)
            else:  # all
                start_time = datetime(2020, 1, 1)  # Arbitrary old date
            
            # Get batches in time range
            filter = BatchFilter(time_range=TimeRange(start=start_time, end=end_time))
            batch_list = await self.list_batches(filter, limit=1000)
            
            # Calculate statistics
            batches_created = batch_list.total_count
            transactions_recorded = sum(b.transaction_count for b in batch_list.batches)
            
            # Unique tables and databases
            unique_tables = set()
            unique_databases = set()
            
            for batch in batch_list.batches:
                unique_databases.add(batch.database_name)
                unique_tables.update(batch.table_names)
            
            return ContractStats(
                batches_created=batches_created,
                transactions_recorded=transactions_recorded,
                unique_tables=len(unique_tables),
                unique_databases=len(unique_databases),
                gas_consumed="0",  # Would need to query blockchain for this
                storage_used="0",  # Would need to query blockchain for this
                time_period=time_period
            )
            
        except Exception as e:
            logger.error(f"Error getting contract stats: {e}")
            return ContractStats(
                batches_created=0,
                transactions_recorded=0,
                unique_tables=0,
                unique_databases=0,
                gas_consumed="0",
                storage_used="0",
                time_period=time_period
            )
    
    async def get_nft_info(self, nft_token_id: str) -> Optional[NFTInfo]:
        """
        Get NFT information for a specific batch token.
        
        Args:
            nft_token_id: NFT token ID (same as batch_id in ETRAP)
            
        Returns:
            NFTInfo with NFT metadata and blockchain details, or None if not found
        """
        try:
            # Get NFT token info from NEAR contract
            nft_token = await self.near_account.view_function(
                self.contract_id,
                "nft_token",
                {"token_id": nft_token_id}
            )
            
            # Handle ViewFunctionResult object
            if hasattr(nft_token, 'result'):
                nft_token = nft_token.result
            
            if not nft_token:
                return None
            
            # Extract metadata
            metadata = nft_token.get('metadata', {})
            owner_id = nft_token.get('owner_id', '')
            
            # Get batch info for additional details
            batch_info = await self.get_batch(nft_token_id)
            
            # Build NFT info
            return NFTInfo(
                token_id=nft_token_id,
                owner_id=owner_id,
                metadata=metadata,
                minted_timestamp=batch_info.timestamp if batch_info else datetime.now(),
                batch_id=nft_token_id,  # In ETRAP, batch_id = token_id
                organization_id=self.organization_id,
                merkle_root=batch_info.merkle_root if batch_info else '',
                blockchain_details={
                    'contract_id': self.contract_id,
                    'network': self.network,
                    'token_standard': 'NEP-171',
                    'approved_account_ids': nft_token.get('approved_account_ids', [])
                }
            )
            
        except Exception as e:
            logger.debug(f"Error getting NFT info for {nft_token_id}: {e}")
            return None
    
    def normalize_transaction(
        self,
        transaction_data: Dict[str, Any],
        source_format: str = "database"
    ) -> Dict[str, Any]:
        """
        Normalize transaction data for verification.
        
        Args:
            transaction_data: Raw transaction data
            source_format: Source format (database/api/csv)
            
        Returns:
            Normalized transaction data
        """
        return normalize_transaction_data(transaction_data)
    
    def prepare_transaction_for_storage(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare transaction data for storage by normalizing it.
        
        This method ensures consistent formatting of transaction data
        before it's hashed and stored, matching CDC agent requirements.
        This is an alias for normalize_transaction() for clarity.
        
        Args:
            transaction_data: Raw transaction data from database
            
        Returns:
            Normalized transaction data ready for hashing
        """
        return self.normalize_transaction(transaction_data)
    
    def compute_transaction_hash(
        self,
        transaction_data: Dict[str, Any],
        normalize: bool = True
    ) -> str:
        """
        Compute hash of transaction data.
        
        Args:
            transaction_data: Transaction data
            normalize: Whether to normalize first
            
        Returns:
            Transaction hash
        """
        return compute_transaction_hash(transaction_data, normalize)
    
    def validate_merkle_proof(
        self,
        leaf_hash: str,
        proof: MerkleProof,
        root: str
    ) -> bool:
        """
        Validate a Merkle proof.
        
        Args:
            leaf_hash: Leaf hash
            proof: Merkle proof to validate
            root: Expected root hash
            
        Returns:
            True if proof is valid
        """
        return validate_merkle_proof(
            leaf_hash,
            proof.proof_path,
            proof.sibling_positions,
            root
        )
    
    def update_config(self, config: Dict[str, Any]):
        """Update client configuration."""
        for key, value in config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def get_config(self) -> ClientConfig:
        """Get current configuration."""
        return self.config
    
    # Private helper methods
    
    async def _verify_document_in_batch_contract(
        self,
        token_id: str,
        document_hash: str,
        merkle_proof: List[str],
        leaf_index: int
    ) -> bool:
        """
        Call smart contract's verify_document_in_batch method.
        
        Args:
            token_id: NFT token ID (batch ID)
            document_hash: Hash of the document/transaction
            merkle_proof: List of sibling hashes in the proof path
            leaf_index: Index of the leaf in the merkle tree
            
        Returns:
            True if verification succeeds
        """
        try:
            result = await self.near_account.view_function(
                self.contract_id,
                "verify_document_in_batch",
                {
                    "token_id": token_id,
                    "document_hash": document_hash,
                    "merkle_proof": merkle_proof,
                    "leaf_index": leaf_index
                }
            )
            
            # Handle ViewFunctionResult object
            if hasattr(result, 'result'):
                result = result.result
                
            return bool(result)
            
        except Exception as e:
            logger.error(f"Contract verification failed: {e}")
            return False
    
    async def _verify_in_batch(self, tx_hash: str, batch: BatchInfo, use_contract_verification: bool = False, expected_operation: Optional[str] = None) -> Optional[VerificationResult]:
        """Verify if transaction exists in a specific batch."""
        try:
            # First check if this is a single-transaction batch where tx_hash == merkle_root
            # This allows verification without S3 access
            if batch.merkle_root and tx_hash == batch.merkle_root:
                logger.debug(f"Transaction hash matches merkle root in batch {batch.batch_id}")
                
                # If expected_operation is specified, we need to verify the operation type
                # even for single-transaction batches
                verified_operation_type = None
                if expected_operation:
                    logger.debug(f"Expected operation specified: {expected_operation}, checking S3 data for operation type")
                    # Need to get batch data to check operation type
                    batch_data = await self.get_batch_data(
                        batch.batch_id,
                        include_merkle_tree=False,
                        include_indices=False
                    )
                    
                    if batch_data:
                        # Check operation type in batch data
                        cache_key = f"batch_data_{batch.batch_id}"
                        batch_json = self._cache.get(cache_key, {})
                        
                        for tx in batch_json.get('transactions', []):
                            if tx.get('metadata', {}).get('hash') == tx_hash:
                                tx_operation = tx.get('metadata', {}).get('operation_type', 'INSERT')
                                if tx_operation != expected_operation:
                                    logger.debug(f"Operation type mismatch: found {tx_operation}, expected {expected_operation}")
                                    return None  # Hash matches but operation type doesn't
                                verified_operation_type = tx_operation
                                break
                        else:
                            # Transaction not found in batch data (shouldn't happen)
                            logger.warning(f"Transaction {tx_hash} not found in batch data for {batch.batch_id}")
                    else:
                        # Can't verify operation type without batch data
                        logger.warning(f"Cannot verify operation type for batch {batch.batch_id} - no S3 data available")
                        # In this case, we'll proceed with verification but note the limitation
                
                return VerificationResult(
                    verified=True,
                    transaction_hash=tx_hash,
                    batch_id=batch.batch_id,
                    merkle_proof=MerkleProof(
                        leaf_hash=tx_hash,
                        proof_path=[],  # Single transaction, no proof needed
                        sibling_positions=[],
                        merkle_root=batch.merkle_root,
                        is_valid=True
                    ),
                    blockchain_timestamp=batch.timestamp,
                    gas_used=None,
                    operation_type=verified_operation_type
                )
            
            # Otherwise, try to get batch data from S3 for full verification
            batch_data = await self.get_batch_data(
                batch.batch_id,
                include_merkle_tree=True,
                include_indices=False
            )
            
            if not batch_data:
                return None
            
            # Search for transaction in batch using cached batch JSON
            cache_key = f"batch_data_{batch.batch_id}"
            batch_json = self._cache.get(cache_key, {})
            
            for tx in batch_json.get('transactions', []):
                if tx.get('metadata', {}).get('hash') == tx_hash:
                    # Check operation type if expected_operation is specified
                    tx_operation = tx.get('metadata', {}).get('operation_type', 'INSERT')
                    if expected_operation and tx_operation != expected_operation:
                        # Hash matches but operation type doesn't - continue searching
                        continue
                    
                    # Found the transaction with matching hash and operation type
                    tx_id = tx['metadata']['transaction_id']
                    tx_index = int(tx_id.split('-')[-1])
                    
                    # Get Merkle proof
                    merkle_proof = await self.get_merkle_proof(batch.batch_id, tx_hash)
                    
                    # Determine verification status
                    if use_contract_verification and merkle_proof:
                        # Use smart contract for verification
                        # Handle the odd leaf duplication case for contract compatibility
                        contract_document_hash = tx_hash
                        contract_proof_path = merkle_proof.proof_path
                        contract_leaf_index = tx_index
                        
                        # Check if this is the last leaf in an odd-numbered batch (duplication case)
                        if (batch.transaction_count % 2 == 1 and 
                            tx_index == batch.transaction_count - 1):
                            # For odd leaf case, the proof assumes duplication already happened
                            # So we need to duplicate the hash and adjust the index for the contract
                            import hashlib
                            contract_document_hash = hashlib.sha256((tx_hash + tx_hash).encode()).hexdigest()
                            # After duplication, this becomes index 1 at the parent level for 3-leaf tree
                            contract_leaf_index = 1
                        
                        verified = await self._verify_document_in_batch_contract(
                            token_id=batch.batch_id,
                            document_hash=contract_document_hash,
                            merkle_proof=contract_proof_path,
                            leaf_index=contract_leaf_index
                        )
                    else:
                        # Use local verification
                        verified = merkle_proof.is_valid if merkle_proof else False
                    
                    return VerificationResult(
                        verified=verified,
                        transaction_hash=tx_hash,
                        batch_id=batch.batch_id,
                        merkle_proof=merkle_proof,
                        blockchain_timestamp=batch.timestamp,
                        gas_used=None,  # Could be extracted from batch metadata
                        operation_type=tx_operation
                    )
            
            return None
            
        except S3AccessError:
            # S3 access errors are expected during batch searches when batches
            # exist on blockchain but don't have detailed data in S3
            logger.debug(f"Batch {batch.batch_id} not accessible in S3 (expected during search)")
            return None
        except Exception as e:
            # Unexpected errors should be logged and re-raised for proper error handling
            logger.error(f"Unexpected error verifying in batch {batch.batch_id}: {e}")
            raise VerificationError(f"Failed to verify transaction in batch {batch.batch_id}: {e}")
    
    async def _get_recent_batches(self, limit: int) -> List[BatchInfo]:
        """Get recent batches from contract."""
        try:
            # Query NEAR contract for recent batches
            result = await self.near_account.view_function(
                self.contract_id,
                "get_recent_batches",
                {"limit": limit}
            )
            
            # Handle ViewFunctionResult object
            if hasattr(result, 'result'):
                result = result.result
            
            if not result:
                return []
            
            batches = []
            for batch_data in result:
                batch_info = self._parse_batch_info(batch_data)
                if batch_info:
                    batches.append(batch_info)
            
            return batches
            
        except Exception as e:
            logger.error(f"Error getting recent batches: {e}")
            # Fallback to NFT tokens method
            try:
                result = await self.near_account.view_function(
                    self.contract_id,
                    "nft_tokens",
                    {"from_index": "0", "limit": limit}
                )
                
                # Handle ViewFunctionResult object
                if hasattr(result, 'result'):
                    result = result.result
                
                batches = []
                if result:
                    for token in result:
                        batch_info = self._parse_batch_info(token)
                        if batch_info:
                            batches.append(batch_info)
                
                return batches
                
            except Exception as e2:
                logger.error(f"Fallback method also failed: {e2}")
                return []
    
    async def _get_batches_by_table(self, table_name: str, limit: int) -> List[BatchInfo]:
        """Get batches for a specific table."""
        # Note: The contract's get_batches_by_table method is unreliable and may return
        # incomplete results. Always use the fallback logic of getting recent batches
        # and filtering by table name.
        
        # Get all recent batches and filter
        all_batches = await self._get_recent_batches(limit * 2)  # Get more to filter
        
        # Filter by table name
        table_batches = []
        for batch in all_batches:
            if table_name in batch.table_names:
                table_batches.append(batch)
                if len(table_batches) >= limit:
                    break
        
        return table_batches
    
    async def _get_batches_by_database(self, database_name: str, limit: int = 100) -> List[BatchInfo]:
        """Get batches for a specific database."""
        # Note: The contract's get_batches_by_database method is unreliable and may return
        # incomplete results. Always use the fallback logic of getting recent batches
        # and filtering by database name.
        
        # Get recent batches and filter by database
        all_batches = await self._get_recent_batches(limit * 2)
        return [b for b in all_batches if b.database_name == database_name][:limit]
    
    async def _get_batches_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        database: Optional[str] = None,
        limit: int = 100
    ) -> List[BatchInfo]:
        """Get batches created on blockchain within a time range (blockchain creation time, not transaction time)."""
        try:
            # Convert to milliseconds timestamp for smart contract query (blockchain time)
            start_timestamp = int(start_time.timestamp() * 1000)
            end_timestamp = int(end_time.timestamp() * 1000)
            
            # Build parameters
            params = {
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "limit": limit
            }
            if database:
                params["database"] = database
            
            # Use contract method for time-based search
            result = await self.near_account.view_function(
                self.contract_id,
                "get_batches_by_time_range",
                params
            )
            
            # Handle ViewFunctionResult object
            if hasattr(result, 'result'):
                result = result.result
            
            if result:
                batches = []
                for batch_data in result:
                    batch_info = self._parse_batch_info(batch_data)
                    if batch_info:
                        batches.append(batch_info)
                return batches
                
        except Exception as e:
            logger.warning(f"Time range query failed: {e}")
        
        # Fallback: filter from recent batches
        all_batches = await self._get_recent_batches(limit * 2)
        filtered = [
            b for b in all_batches 
            if start_time <= b.timestamp <= end_time
            and (not database or b.database_name == database)
        ]
        return filtered[:limit]
    
    def _parse_batch_info(self, contract_data: Dict) -> Optional[BatchInfo]:
        """Parse contract response into BatchInfo."""
        try:
            # Handle NFT token format
            token_id = contract_data.get('token_id', '')
            metadata = contract_data.get('metadata', {})
            
            # Check if batch_summary is at the top level (from etrap_verify format)
            batch_summary_top = contract_data.get('batch_summary', {})
            
            # If we have batch_summary at top level with merkle_root, use it directly
            if batch_summary_top and 'merkle_root' in batch_summary_top:
                return BatchInfo(
                    batch_id=token_id,
                    database_name=batch_summary_top.get('database_name', 'unknown'),
                    table_names=batch_summary_top.get('table_names', []),
                    transaction_count=batch_summary_top.get('tx_count', 0),
                    merkle_root=batch_summary_top.get('merkle_root', ''),
                    timestamp=datetime.fromtimestamp(batch_summary_top.get('timestamp', 0) / 1000),  # Blockchain batch creation time
                    s3_location=S3Location(
                        bucket=batch_summary_top.get('s3_bucket', f"etrap-{self.organization_id}"),
                        key=batch_summary_top.get('s3_key', ''),
                        region='us-west-2'
                    ),
                    size_bytes=batch_summary_top.get('size_bytes', 0)
                )
            
            # Check if batch info is in reference URL
            reference = metadata.get('reference', '')
            if reference and reference.startswith('https://s3'):
                # Parse S3 URL: https://s3.amazonaws.com/bucket/key
                import re
                match = re.match(r'https://s3[.-]([^.]+\.)?amazonaws\.com/([^/]+)/(.+)', reference)
                if match:
                    bucket = match.group(2)
                    key_path = match.group(3)
                    # Use the full key path, removing only the filename if present
                    if key_path.endswith('/batch-data.json'):
                        batch_key = key_path[:-len('batch-data.json')]
                    elif key_path.endswith('batch-data.json'):
                        batch_key = key_path[:-len('batch-data.json')]
                    else:
                        # If no batch-data.json, assume key_path is the directory
                        batch_key = key_path if key_path.endswith('/') else key_path + '/'
                    
                    logger.debug(f"Parsed S3 reference: bucket={bucket}, key_path={key_path}, batch_key={batch_key}")
                        
                    # Extract info from description
                    description = metadata.get('description', '')
                    tx_count_match = re.search(r'(\d+) transactions', description)
                    tx_count = int(tx_count_match.group(1)) if tx_count_match else 0
                    
                    table_match = re.search(r'from table (\w+)', description)
                    table_name = table_match.group(1) if table_match else 'unknown'
                    
                    # Parse timestamp
                    issued_at = metadata.get('issued_at', '0')
                    if issued_at:
                        timestamp = datetime.fromtimestamp(int(issued_at) / 1000)
                    else:
                        timestamp = datetime.now()
                    
                    return BatchInfo(
                        batch_id=token_id,
                        database_name='unknown',  # Not in this metadata format
                        table_names=[table_name] if table_name != 'unknown' else [],
                        transaction_count=tx_count,
                        merkle_root='',  # Not in this metadata format
                        timestamp=timestamp,
                        s3_location=S3Location(
                            bucket=bucket,
                            key=batch_key,
                            region='us-west-2'
                        ),
                        size_bytes=0  # Not in this metadata format
                    )
            
            # Extract batch summary from metadata
            if isinstance(metadata.get('extra'), str):
                import json
                batch_summary = json.loads(metadata['extra'])
            else:
                batch_summary = metadata.get('extra', {})
            
            # If no extra field, try direct fields
            if not batch_summary:
                batch_summary = {
                    'database_name': metadata.get('database_name', 'unknown'),
                    'table_names': metadata.get('table_names', []),
                    'timestamp': metadata.get('timestamp', 0),
                    'tx_count': metadata.get('tx_count', 0),
                    'merkle_root': metadata.get('merkle_root', ''),
                    's3_location': metadata.get('s3_location', {})
                }
            
            # Parse S3 location
            s3_loc = batch_summary.get('s3_location', {})
            # Get table name for S3 path (use first table if multiple)
            table_names = batch_summary.get('table_names', [])
            table_name = table_names[0] if table_names else 'unknown'
            
            if isinstance(s3_loc, dict) and s3_loc.get('key'):
                # Use the exact S3 location from NFT metadata (preferred)
                s3_location = S3Location(
                    bucket=s3_loc.get('bucket', self.s3_bucket if hasattr(self, 's3_bucket') else f"etrap-{self.organization_id}"),
                    key=s3_loc.get('key'),  # Use exact key from metadata
                    region=s3_loc.get('region', 'us-west-2')
                )
            else:
                # Legacy format - construct path
                s3_location = S3Location(
                    bucket=self.s3_bucket if hasattr(self, 's3_bucket') else f"etrap-{self.organization_id}",
                    key=f"{batch_summary.get('database_name', 'unknown')}/{table_name}/{token_id}/",
                    region='us-west-2'
                )
            
            # Convert timestamp
            timestamp_ms = batch_summary.get('timestamp', 0)
            if timestamp_ms:
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
            else:
                timestamp = datetime.now()
            
            return BatchInfo(
                batch_id=token_id,
                database_name=batch_summary.get('database_name', 'unknown'),
                table_names=batch_summary.get('table_names', []),
                transaction_count=batch_summary.get('tx_count', 0),
                merkle_root=batch_summary.get('merkle_root', ''),
                timestamp=timestamp,
                s3_location=s3_location,
                size_bytes=batch_summary.get('size_bytes', 0)
            )
            
        except Exception as e:
            logger.error(f"Error parsing batch info: {e}")
            return None
    
    def _validate_merkle_proof_with_context(
        self,
        leaf_hash: str,
        proof_path: list,
        sibling_positions: list,
        root: str,
        leaf_index: int,
        total_leaves: int
    ) -> bool:
        """
        Validate a merkle proof with context about the tree structure.
        
        This handles the edge case where the last leaf in an odd-numbered
        set needs to be duplicated before applying the proof path.
        
        Supports both position-based (with sibling_positions) and index-based
        verification for backward compatibility during migration.
        """
        current_hash = leaf_hash
        
        # Check if we have sibling_positions (old format)
        if sibling_positions and len(sibling_positions) > 0:
            # Use position-based verification for backward compatibility
            from .utils import validate_merkle_proof
            
            # CDC Agent now uses power-of-2 padding, so no odd-leaf duplication needed
            return validate_merkle_proof(current_hash, proof_path, sibling_positions, root)
        else:
            # Use index-based verification for new format (matches smart contract)
            
            # CDC Agent now uses power-of-2 padding, so no odd-leaf duplication needed
            from .utils import validate_merkle_proof_indexed
            return validate_merkle_proof_indexed(current_hash, proof_path, leaf_index, root)