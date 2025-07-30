"""
Tests for utility functions.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from pathlib import Path

import pytest

from q1._internal.utils import (
    calculate_sha256,
    chunk_iterator,
    format_size,
    format_timestamp,
    generate_uuid,
    get_extension,
    parse_metadata,
    parse_size,
    timestamp_ms,
    verify_sha256,
)
from q1.errors import IntegrityError


def test_generate_uuid() -> None:
    """Test UUID generation."""
    uid = generate_uuid()
    assert len(uid) == 36  # Standard UUID length
    
    # Should be a valid UUID
    uuid_obj = uuid.UUID(uid)
    assert str(uuid_obj) == uid


def test_get_extension() -> None:
    """Test file extension extraction."""
    assert get_extension("file.txt") == "txt"
    assert get_extension("file.TXT") == "txt"  # Should lowercase
    assert get_extension("file.tar.gz") == "gz"  # Only last part
    assert get_extension("file") is None
    assert get_extension(".gitignore") == "gitignore"
    assert get_extension("file.") is None


def test_calculate_sha256(temp_dir: Path) -> None:
    """Test SHA-256 calculation."""
    test_file = temp_dir / "test.txt"
    
    # Create a file with known content
    with open(test_file, "wb") as f:
        f.write(b"hello world")
    
    # Calculate hash
    file_hash = calculate_sha256(test_file)
    
    # Expected hash for "hello world"
    expected = hashlib.sha256(b"hello world").digest()
    
    assert file_hash == expected


def test_verify_sha256(temp_dir: Path) -> None:
    """Test SHA-256 verification."""
    test_file = temp_dir / "test.txt"
    
    # Create a file with known content
    with open(test_file, "wb") as f:
        f.write(b"hello world")
    
    # Calculate the correct hash
    correct_hash = calculate_sha256(test_file)
    
    # Verification should pass with the correct hash
    assert verify_sha256(test_file, correct_hash) is True
    
    # Verification should fail with an incorrect hash
    wrong_hash = os.urandom(32)  # Random 32-byte hash
    with pytest.raises(IntegrityError):
        verify_sha256(test_file, wrong_hash)


def test_timestamp_ms() -> None:
    """Test millisecond timestamp generation."""
    ts = timestamp_ms()
    
    # Should be close to the current time
    assert abs(ts - int(time.time() * 1000)) < 1000  # Within 1 second
    
    # Should be a valid timestamp
    assert ts > 1500000000000  # July 2017 or later


def test_format_timestamp() -> None:
    """Test timestamp formatting."""
    # Test with a specific timestamp (January 1, 2020 12:00:00 UTC)
    ts = 1577880000000  # ms
    
    # Format the timestamp
    formatted = format_timestamp(ts)
    
    # The exact output depends on the local timezone
    # But it should contain the year
    assert "2020" in formatted
    
    # Test with the current timestamp
    now_ts = timestamp_ms()
    now_formatted = format_timestamp(now_ts)
    
    # Should be a non-empty string
    assert now_formatted


def test_parse_metadata() -> None:
    """Test metadata parsing."""
    # Dict input
    metadata = {"key": "value", "nested": {"num": 42}}
    parsed = parse_metadata(metadata)
    assert isinstance(parsed, str)
    assert json.loads(parsed) == metadata
    
    # String input (already JSON)
    json_str = '{"key": "value"}'
    parsed = parse_metadata(json_str)
    assert parsed == json_str
    
    # Bytes input
    bytes_input = b'{"key": "value"}'
    parsed = parse_metadata(bytes_input)
    assert parsed == '{"key": "value"}'
    
    # None input
    assert parse_metadata(None) is None
    
    # Invalid JSON string
    with pytest.raises(ValueError):
        parse_metadata('{"key": unclosed')
    
    # Non-serializable object
    with pytest.raises(ValueError):
        parse_metadata({1, 2, 3})  # Set is not JSON serializable


def test_parse_size() -> None:
    """Test size string parsing."""
    assert parse_size("1024") == 1024
    assert parse_size("1KB") == 1024
    assert parse_size("1kb") == 1024
    assert parse_size("1.5KB") == 1536
    assert parse_size("1MB") == 1024 * 1024
    assert parse_size("1.5GB") == int(1.5 * 1024 * 1024 * 1024)
    assert parse_size("1TB") == 1024 * 1024 * 1024 * 1024
    
    # Invalid inputs
    with pytest.raises(ValueError):
        parse_size("")
    with pytest.raises(ValueError):
        parse_size("invalid")
    with pytest.raises(ValueError):
        parse_size("1XB")  # Unknown unit


def test_format_size() -> None:
    """Test size formatting."""
    assert format_size(500) == "500 bytes"
    assert format_size(1023) == "1023 bytes"
    assert format_size(1024) == "1.0 KB"
    assert format_size(1536) == "1.5 KB"
    assert format_size(1024 * 1024) == "1.0 MB"
    assert format_size(1024 * 1024 * 1024) == "1.0 GB"
    assert format_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"


def test_chunk_iterator(temp_dir: Path) -> None:
    """Test file chunk iteration."""
    # Create a test file with some content
    test_file = temp_dir / "test.txt"
    content = b"a" * 1000 + b"b" * 1000 + b"c" * 1000
    
    with open(test_file, "wb") as f:
        f.write(content)
    
    # Read in chunks of 1000 bytes
    chunks = list(chunk_iterator(test_file, chunk_size=1000))
    
    assert len(chunks) == 3
    assert chunks[0] == b"a" * 1000
    assert chunks[1] == b"b" * 1000
    assert chunks[2] == b"c" * 1000
    
    # Read in larger chunks
    big_chunks = list(chunk_iterator(test_file, chunk_size=2000))
    
    assert len(big_chunks) == 2
    assert big_chunks[0] == b"a" * 1000 + b"b" * 1000
    assert big_chunks[1] == b"c" * 1000
