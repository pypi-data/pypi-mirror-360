"""
Utility functions for the Q1 storage library.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Tuple, Union

from q1.errors import IntegrityError


def generate_uuid() -> str:
    """Generate a random UUID string.
    
    Returns:
        A random UUID string
    """
    return str(uuid.uuid4())


def get_extension(filename: str) -> Optional[str]:
    """Extract the extension from a filename.
    
    Args:
        filename: The filename
        
    Returns:
        The extension without the dot, or None if no extension
    """
    parts = filename.rsplit(".", 1)
    if len(parts) > 1 and parts[1]:
        return parts[1].lower()
    return None


def calculate_sha256(file_path: Path) -> bytes:
    """Calculate the SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The 32-byte SHA-256 hash
        
    Raises:
        OSError: If the file cannot be read
    """
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.digest()


def verify_sha256(file_path: Path, expected_hash: bytes) -> bool:
    """Verify the SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        expected_hash: The expected SHA-256 hash
        
    Returns:
        True if the hash matches
        
    Raises:
        IntegrityError: If the hash does not match
        OSError: If the file cannot be read
    """
    actual_hash = calculate_sha256(file_path)
    if actual_hash != expected_hash:
        # Get hex representations for error message
        actual_hex = actual_hash.hex()
        expected_hex = expected_hash.hex()
        raise IntegrityError(f"File integrity check failed: expected {expected_hex}, got {actual_hex}")
    return True


def timestamp_ms() -> int:
    """Get the current timestamp in milliseconds.
    
    Returns:
        Current timestamp in milliseconds
    """
    return int(time.time() * 1000)


def format_timestamp(ts_ms: int) -> str:
    """Format a millisecond timestamp as a human-readable string.
    
    Args:
        ts_ms: Timestamp in milliseconds
        
    Returns:
        Formatted timestamp string
    """
    ts_sec = ts_ms / 1000
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts_sec))


def parse_metadata(metadata: Optional[Union[str, Dict[str, Any], bytes]]) -> Optional[str]:
    """Parse metadata to a JSON string.
    
    Args:
        metadata: Metadata as a string, dictionary, or bytes
        
    Returns:
        JSON-encoded metadata string, or None if metadata is None
        
    Raises:
        ValueError: If the metadata cannot be parsed
    """
    if metadata is None:
        return None
    
    if isinstance(metadata, bytes):
        metadata = metadata.decode("utf-8")
    
    if isinstance(metadata, str):
        # Validate that it's valid JSON
        try:
            json.loads(metadata)
            return metadata
        except json.JSONDecodeError:
            raise ValueError(f"Invalid metadata JSON: {metadata}")
    
    # Assume it's a dictionary or similar and encode it
    try:
        return json.dumps(metadata)
    except TypeError:
        raise ValueError(f"Metadata must be a JSON-serializable object, got {type(metadata)}")


def parse_size(size_str: str) -> int:
    """Parse a human-readable size string to bytes.
    
    Args:
        size_str: Size string (e.g., "1KB", "2.5MB")
        
    Returns:
        Size in bytes
        
    Raises:
        ValueError: If the size string cannot be parsed
    """
    size_str = size_str.strip()
    if not size_str:
        raise ValueError("Empty size string")
    
    # Handle bytes with no suffix
    if size_str.isdigit():
        return int(size_str)
    
    # Define unit multipliers
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
        "TB": 1024 * 1024 * 1024 * 1024,
    }
    
    # Regular expression to match number + unit pattern (e.g., "1KB", "2.5MB")
    pattern = r'^([\d.]+)\s*([A-Za-z]+)$'
    match = re.match(pattern, size_str, re.IGNORECASE)
    
    if match:
        number_str, unit_str = match.groups()
        unit_str = unit_str.upper()
        
        if unit_str in units:
            try:
                value = float(number_str)
                return int(value * units[unit_str])
            except ValueError:
                pass
    
    raise ValueError(f"Unknown size format: {size_str}")


def format_size(size_bytes: int) -> str:
    """Format a byte count as a human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes < 1024 * 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024 * 1024):.1f} TB"


def chunk_iterator(file_path: Path, chunk_size: int = 65536) -> Generator[bytes, None, None]:
    """Read a file in chunks.
    
    Args:
        file_path: Path to the file to read
        chunk_size: Size of each chunk in bytes
        
    Yields:
        File chunks
        
    Raises:
        OSError: If the file cannot be read
    """
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk
