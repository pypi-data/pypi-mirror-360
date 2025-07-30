#!/usr/bin/env python3
"""
================================================================================
ETRAP SDK - Batch Structure Analysis Tool
================================================================================

This tool analyzes the structure of ETRAP batch data files to show how 
multi-transaction batches are organized and how Merkle proofs work.

What this tool shows:
- Complete batch metadata and organization
- Individual transaction records with their hashes
- Merkle tree structure and proof paths for each transaction
- Search indices for efficient transaction lookup
- Compliance and verification data
- How to verify individual transactions within a batch

This helps understand the complete ETRAP batch data structure stored in S3
and how cryptographic verification works for multi-transaction batches.

Usage: python analyze_batch_structure.py [batch_file.json]

Arguments:
  batch_file.json - Optional path to batch JSON file
                   If not provided, uses examples/batch-multi.json

Example: python analyze_batch_structure.py examples/batch-multi.json

The tool will display detailed analysis of the batch structure and demonstrate
how individual transaction verification works within the batch.
"""

import json
import sys
import os
from pathlib import Path

def analyze_batch_structure(batch_file):
    """Analyze and display the structure of an ETRAP batch file."""
    
    try:
        with open(batch_file, 'r') as f:
            batch_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {batch_file} not found")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return
    
    print("=" * 80)
    print("ETRAP BATCH STRUCTURE ANALYSIS")
    print("=" * 80)
    
    # Batch Info
    batch_info = batch_data.get('batch_info', {})
    print(f"\n📦 BATCH INFORMATION")
    print(f"   Batch ID: {batch_info.get('batch_id', 'N/A')}")
    print(f"   Organization: {batch_info.get('organization_id', 'N/A')}")
    print(f"   Database: {batch_info.get('database_name', 'N/A')}")
    print(f"   Created: {batch_info.get('created_at', 'N/A')}")
    print(f"   Agent Version: {batch_info.get('etrap_agent_version', 'N/A')}")
    
    # Transactions
    transactions = batch_data.get('transactions', [])
    print(f"\n📄 TRANSACTIONS ({len(transactions)} total)")
    for i, tx in enumerate(transactions):
        metadata = tx.get('metadata', {})
        merkle_leaf = tx.get('merkle_leaf', {})
        print(f"   Transaction {i}:")
        print(f"     ID: {metadata.get('transaction_id', 'N/A')}")
        print(f"     Operation: {metadata.get('operation_type', 'N/A')}")
        print(f"     Table: {metadata.get('table_affected', 'N/A')}")
        print(f"     Hash: {metadata.get('hash', 'N/A')[:16]}...")
        print(f"     Merkle Index: {merkle_leaf.get('index', 'N/A')}")
    
    # Merkle Tree
    merkle_tree = batch_data.get('merkle_tree', {})
    print(f"\n🌳 MERKLE TREE")
    print(f"   Algorithm: {merkle_tree.get('algorithm', 'N/A')}")
    print(f"   Root: {merkle_tree.get('root', 'N/A')[:16]}...")
    print(f"   Height: {merkle_tree.get('height', 'N/A')}")
    
    nodes = merkle_tree.get('nodes', [])
    print(f"   Nodes: {len(nodes)} total")
    
    # Show tree structure
    levels = {}
    for node in nodes:
        level = node.get('level', 0)
        if level not in levels:
            levels[level] = []
        levels[level].append(node)
    
    for level in sorted(levels.keys()):
        level_nodes = levels[level]
        print(f"     Level {level}: {len(level_nodes)} nodes")
        for node in level_nodes:
            node_hash = node.get('hash', '')[:8]
            if 'left_child' in node:
                print(f"       Node {node.get('index')}: {node_hash}... (internal)")
            else:
                print(f"       Node {node.get('index')}: {node_hash}... (leaf)")
    
    # Proof paths
    proof_index = merkle_tree.get('proof_index', {})
    print(f"\n🔐 MERKLE PROOFS")
    for tx_id, proof in proof_index.items():
        proof_path = proof.get('proof_path', [])
        positions = proof.get('sibling_positions', [])
        print(f"   {tx_id}:")
        print(f"     Leaf Index: {proof.get('leaf_index', 'N/A')}")
        print(f"     Proof Steps: {len(proof_path)}")
        for i, (hash_val, pos) in enumerate(zip(proof_path, positions)):
            print(f"       Step {i}: {hash_val[:8]}... ({pos})")
    
    # Indices
    indices = batch_data.get('indices', {})
    print(f"\n📇 SEARCH INDICES")
    for index_type, index_data in indices.items():
        print(f"   {index_type}: {len(index_data)} entries")
        if index_type == 'by_timestamp' and index_data:
            # Show timestamp range
            timestamps = list(index_data.keys())
            if timestamps:
                print(f"     Range: {min(timestamps)} to {max(timestamps)}")
        elif index_type == 'by_operation' and index_data:
            operations = list(index_data.keys())
            print(f"     Operations: {', '.join(operations)}")
    
    # Compliance
    compliance = batch_data.get('compliance', {})
    if compliance:
        print(f"\n⚖️  COMPLIANCE DATA")
        rules = compliance.get('rules_applied', [])
        if rules:
            print(f"   Rules Applied: {', '.join(rules)}")
        classifications = compliance.get('data_classifications', [])
        if classifications:
            print(f"   Data Classifications: {', '.join(classifications)}")
        retention = compliance.get('retention_policy')
        if retention:
            print(f"   Retention Policy: {retention}")
    
    # Verification
    verification = batch_data.get('verification', {})
    if verification:
        print(f"\n✅ VERIFICATION DATA")
        print(f"   Batch Signature: {verification.get('batch_signature', 'N/A')[:16]}...")
        print(f"   Signing Algorithm: {verification.get('signing_algorithm', 'N/A')}")
        anchoring = verification.get('anchoring_data', {})
        if anchoring:
            print(f"   Blockchain Transaction: {anchoring.get('tx_hash', 'N/A')[:16]}...")
            print(f"   Gas Used: {anchoring.get('gas_used', 'N/A')}")
    
    print(f"\n" + "=" * 80)
    print("VERIFICATION EXAMPLE")
    print("=" * 80)
    
    # Show how to verify the first transaction
    if transactions and merkle_tree.get('root') and proof_index:
        first_tx = transactions[0]
        tx_id = f"tx-0"
        if tx_id in proof_index:
            tx_hash = first_tx['metadata']['hash']
            proof_data = proof_index[tx_id]
            merkle_root = merkle_tree['root']
            
            print(f"\nTo verify transaction {tx_id}:")
            print(f"1. Start with transaction hash: {tx_hash[:16]}...")
            print(f"2. Apply proof path:")
            
            current_hash = tx_hash
            proof_path = proof_data['proof_path']
            positions = proof_data['sibling_positions']
            
            for i, (sibling, position) in enumerate(zip(proof_path, positions)):
                print(f"   Step {i+1}: Combine with {sibling[:8]}... ({position})")
                # Note: This is pseudocode - actual hash combination would need crypto
                current_hash = f"combined_hash_step_{i+1}"
            
            print(f"3. Final result should equal Merkle root: {merkle_root[:16]}...")
            print(f"\nThis cryptographically proves the transaction was included in the batch.")

def main():
    # Default to batch-multi.json if no argument provided
    if len(sys.argv) > 1:
        batch_file = sys.argv[1]
    else:
        # Look for batch-multi.json in the same directory as this script
        script_dir = Path(__file__).parent
        batch_file = script_dir / "batch-multi.json"
    
    if not os.path.exists(batch_file):
        print(f"Error: Batch file {batch_file} not found")
        print("Usage: python analyze_batch_structure.py [batch_file.json]")
        sys.exit(1)
    
    analyze_batch_structure(batch_file)

if __name__ == "__main__":
    main()