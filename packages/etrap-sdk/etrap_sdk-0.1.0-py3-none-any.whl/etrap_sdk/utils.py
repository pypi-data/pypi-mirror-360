"""
Utility functions for ETRAP SDK.

Common functions used throughout the SDK for data manipulation and validation.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional, List


def normalize_transaction_data(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize transaction data to match CDC agent format.
    
    This allows users to input data exactly as returned by the database.
    
    Args:
        transaction_data: Raw transaction data from database
        
    Returns:
        Normalized transaction data ready for hashing
    """
    normalized = transaction_data.copy()
    
    # Auto-detect numeric fields and normalize based on type and field name
    # ID fields remain as integers, other numeric fields become strings
    for field, value in list(normalized.items()):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if field == 'id' or field.endswith('_id'):
                # Keep ID fields as integers (primary/foreign keys)
                normalized[field] = value
            elif field.endswith('_at') and isinstance(value, (int, float)) and value > 1000000000:
                # Convert numeric _at fields to ISO format (matching CDC agent behavior)
                # This handles epoch timestamps in seconds or milliseconds
                if value > 1000000000000000:  # Microseconds (16+ digits)
                    dt = datetime.fromtimestamp(value / 1000000)
                elif value > 1000000000000:  # Milliseconds (13+ digits)
                    dt = datetime.fromtimestamp(value / 1000)
                else:  # Seconds (10+ digits)
                    dt = datetime.fromtimestamp(value)
                
                # Format to match PostgreSQL timestamp format
                iso_str = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
                # Remove trailing zeros but keep at least milliseconds
                iso_str = iso_str.rstrip('0').rstrip('.')
                if '.' not in iso_str:
                    iso_str += '.000'
                normalized[field] = iso_str
            else:
                # Convert other numeric fields to strings with database-compatible precision
                if isinstance(value, float):
                    # For floats, preserve decimal precision to match CDC agent behavior
                    # Check if it's a whole number or has decimals
                    if value == int(value):
                        # Whole number float (e.g., 1000.0) - preserve as .00 for database compatibility
                        normalized[field] = f"{int(value):.2f}"
                    else:
                        # Has decimal places - preserve them with appropriate formatting
                        # Use minimal decimal places but ensure at least 2 for monetary values
                        decimal_str = f"{value:.10f}".rstrip('0')
                        if decimal_str.endswith('.'):
                            decimal_str += '00'
                        elif '.' in decimal_str and len(decimal_str.split('.')[1]) == 1:
                            decimal_str += '0'
                        normalized[field] = decimal_str
                else:
                    # For integers, keep as-is to match CDC agent behavior
                    normalized[field] = value
    
    # Normalize timestamps
    for field, value in list(normalized.items()):
        if field.endswith('_at') and isinstance(value, str):
            # Replace space with T separator if present
            if ' ' in value and 'T' not in value:
                value = value.replace(' ', 'T')
            
            # Parse and reformat to ensure consistent precision
            try:
                # Handle various timestamp formats
                if '.' in value:
                    # Has fractional seconds
                    dt_part, frac_part = value.rsplit('.', 1)
                    # Normalize to 3 decimal places (milliseconds)
                    frac_part = frac_part[:3].ljust(3, '0')
                    normalized[field] = f"{dt_part}.{frac_part}"
                else:
                    # No fractional seconds, add .000
                    normalized[field] = f"{value}.000"
            except Exception:
                # If parsing fails, keep original
                pass
    
    return normalized


def compute_transaction_hash(transaction_data: Dict[str, Any], normalize: bool = True) -> str:
    """
    Compute deterministic hash of transaction data.
    
    This must match exactly how the CDC agent computes hashes.
    
    Args:
        transaction_data: Transaction data to hash
        normalize: Whether to normalize the data first
        
    Returns:
        SHA256 hash as hex string
    """
    if normalize:
        data = normalize_transaction_data(transaction_data)
    else:
        data = transaction_data.copy()
    
    # Keep null values - CDC agent includes them in hashing
    # data = {k: v for k, v in data.items() if v is not None}
    
    # Sort keys to ensure deterministic JSON (matching CDC agent)
    normalized_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(normalized_json.encode()).hexdigest()


def validate_merkle_proof(leaf_hash: str, proof_path: list, sibling_positions: list, root: str) -> bool:
    """
    Validate a Merkle proof.
    
    Args:
        leaf_hash: Hash of the transaction
        proof_path: List of sibling hashes
        sibling_positions: List of positions ('left' or 'right')
        root: Expected Merkle root
        
    Returns:
        True if the proof is valid
    """
    current_hash = leaf_hash
    
    for sibling_hash, position in zip(proof_path, sibling_positions):
        if position == 'left':
            combined = sibling_hash + current_hash
        else:
            combined = current_hash + sibling_hash
        
        current_hash = hashlib.sha256(combined.encode()).hexdigest()
    
    return current_hash == root


def validate_merkle_proof_indexed(leaf_hash: str, proof_path: list, leaf_index: int, root: str) -> bool:
    """
    Validate a Merkle proof using index-based positioning (matches smart contract).
    
    Args:
        leaf_hash: Hash of the transaction
        proof_path: List of sibling hashes
        leaf_index: Index of the leaf in the tree
        root: Expected Merkle root
        
    Returns:
        True if the proof is valid
    """
    current_hash = leaf_hash
    current_index = leaf_index
    
    for sibling_hash in proof_path:
        if current_index % 2 == 0:
            # Current node is left child
            combined = current_hash + sibling_hash
        else:
            # Current node is right child
            combined = sibling_hash + current_hash
        
        current_hash = hashlib.sha256(combined.encode()).hexdigest()
        current_index = current_index // 2
    
    return current_hash == root


def parse_timestamp(timestamp: Any) -> Optional[datetime]:
    """
    Parse various timestamp formats.
    
    Args:
        timestamp: Timestamp in various formats
        
    Returns:
        datetime object or None if parsing fails
    """
    if isinstance(timestamp, datetime):
        return timestamp
    
    if isinstance(timestamp, (int, float)):
        # Assume milliseconds if > 1e12
        if timestamp > 1e12:
            return datetime.fromtimestamp(timestamp / 1000)
        else:
            return datetime.fromtimestamp(timestamp)
    
    if isinstance(timestamp, str):
        # Try ISO format
        try:
            # Handle both space and T separator
            ts = timestamp.replace(' ', 'T')
            # Handle various fractional second precisions
            if '.' in ts:
                dt_part, frac_part = ts.split('.')
                # Standardize fractional seconds
                frac_part = frac_part.rstrip('Z').ljust(6, '0')[:6]
                ts = f"{dt_part}.{frac_part}"
            return datetime.fromisoformat(ts)
        except:
            pass
    
    return None


def format_transaction_summary(
    transaction_data: Dict[str, Any],
    primary_fields: Optional[List[str]] = None,
    max_fields: int = 5
) -> str:
    """
    Format a transaction for display in a generic way.
    
    This function creates a human-readable summary of transaction data,
    adapting to different table schemas automatically.
    
    Args:
        transaction_data: Transaction data to format
        primary_fields: Optional list of field names to prioritize in display.
                       If not provided, will auto-detect important fields.
        max_fields: Maximum number of fields to display (default: 5)
        
    Returns:
        Human-readable summary string
    """
    if not transaction_data:
        return "Empty transaction"
    
    # Default primary fields to look for (in order of preference)
    if primary_fields is None:
        primary_fields = ['id', 'transaction_id', 'tx_id', 'record_id', 'pk']
    
    # Common field patterns to prioritize
    priority_patterns = [
        # ID fields
        ('id', 'ID'),
        ('_id', 'ID'),
        ('transaction_id', 'Transaction'),
        ('tx_id', 'TX'),
        ('record_id', 'Record'),
        # Account/user fields
        ('account_id', 'Account'),
        ('user_id', 'User'),
        ('customer_id', 'Customer'),
        ('client_id', 'Client'),
        # Amount/value fields
        ('amount', 'Amount'),
        ('value', 'Value'),
        ('total', 'Total'),
        ('balance', 'Balance'),
        # Type/status fields
        ('type', 'Type'),
        ('status', 'Status'),
        ('state', 'State'),
        ('action', 'Action'),
        ('operation', 'Operation'),
        # Name/description fields
        ('name', 'Name'),
        ('description', 'Desc'),
        ('title', 'Title'),
        # Timestamp fields
        ('created_at', 'Created'),
        ('updated_at', 'Updated'),
        ('timestamp', 'Time'),
        ('date', 'Date')
    ]
    
    parts = []
    used_fields = set()
    
    # First, add any explicitly requested primary fields
    for field in primary_fields:
        if field in transaction_data and field not in used_fields:
            value = _format_field_value(field, transaction_data[field])
            label = _format_field_label(field)
            parts.append(f"{label}: {value}")
            used_fields.add(field)
    
    # Then add fields based on priority patterns
    for pattern, label in priority_patterns:
        if len(parts) >= max_fields:
            break
            
        # Find fields matching this pattern
        matching_fields = [
            f for f in transaction_data.keys()
            if pattern in f.lower() and f not in used_fields
        ]
        
        for field in matching_fields[:1]:  # Take first match only
            if len(parts) >= max_fields:
                break
            value = _format_field_value(field, transaction_data[field])
            parts.append(f"{label}: {value}")
            used_fields.add(field)
    
    # If we still have room, add any remaining fields
    if len(parts) < max_fields:
        remaining_fields = [
            f for f in transaction_data.keys()
            if f not in used_fields and not f.startswith('_')
        ]
        
        for field in sorted(remaining_fields)[:max_fields - len(parts)]:
            value = _format_field_value(field, transaction_data[field])
            label = _format_field_label(field)
            parts.append(f"{label}: {value}")
    
    return " | ".join(parts) if parts else "No displayable fields"


def _format_field_label(field_name: str) -> str:
    """Convert field name to human-readable label."""
    # Remove common prefixes/suffixes
    label = field_name
    for prefix in ['fk_', 'pk_', 'id_']:
        if label.startswith(prefix):
            label = label[len(prefix):]
    for suffix in ['_id', '_at', '_on']:
        if label.endswith(suffix) and len(label) > len(suffix):
            label = label[:-len(suffix)]
    
    # Convert to title case
    label = label.replace('_', ' ').title()
    
    # Special cases
    label_map = {
        'Id': 'ID',
        'Tx': 'TX',
        'Pk': 'PK',
        'Fk': 'FK',
        'Uid': 'UID',
        'Uuid': 'UUID',
        'Api': 'API',
        'Url': 'URL',
        'Uri': 'URI'
    }
    
    for old, new in label_map.items():
        label = label.replace(old, new)
    
    return label


def _format_field_value(field_name: str, value: Any) -> str:
    """Format a field value for display."""
    if value is None:
        return "null"
    
    # Handle numeric fields that might be amounts
    if isinstance(value, (int, float)):
        field_lower = field_name.lower()
        if any(term in field_lower for term in ['amount', 'price', 'cost', 'total', 'balance', 'value']):
            # Format as currency
            return f"${value:,.2f}"
        elif any(term in field_lower for term in ['percent', 'rate', 'ratio']):
            # Format as percentage
            return f"{value:.2f}%"
        else:
            # Format as regular number
            if isinstance(value, float):
                return f"{value:,.2f}" if value != int(value) else f"{int(value):,}"
            else:
                return f"{value:,}"
    
    # Handle boolean values
    if isinstance(value, bool):
        return "Yes" if value else "No"
    
    # Handle datetime strings
    if isinstance(value, str):
        # Check if it looks like a datetime
        if len(value) >= 10 and value[4] == '-' and value[7] == '-':
            try:
                # Try to parse and format nicely
                if 'T' in value or ' ' in value:
                    # Full datetime
                    dt = parse_timestamp(value)
                    if dt:
                        return dt.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # Just date
                    return value
            except:
                pass
        
        # Truncate long strings
        if len(value) > 50:
            return value[:47] + "..."
    
    # Handle lists/arrays
    if isinstance(value, list):
        if len(value) == 0:
            return "[]"
        elif len(value) <= 3:
            return f"[{', '.join(str(v) for v in value)}]"
        else:
            return f"[{len(value)} items]"
    
    # Handle dicts/objects
    if isinstance(value, dict):
        if len(value) == 0:
            return "{}"
        else:
            return f"{{object with {len(value)} fields}}"
    
    # Default: convert to string
    return str(value)