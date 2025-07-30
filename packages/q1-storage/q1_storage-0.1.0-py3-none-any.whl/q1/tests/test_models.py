"""
Tests for data models.
"""
from __future__ import annotations

import json
import time

import pytest

from q1._internal.utils import timestamp_ms
from q1.models import FileInfo, Stats


def test_file_info_creation() -> None:
    """Test creating a FileInfo object."""
    file_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Create a minimal FileInfo
    file_info = FileInfo(
        id=file_id,
        name="test.txt",
        size=1024,
        created_at=timestamp_ms(),
    )
    
    # Check basic properties
    assert file_info.id == file_id
    assert file_info.name == "test.txt"
    assert file_info.size == 1024
    assert isinstance(file_info.created_at, int)
    assert file_info.extension is None
    assert file_info.is_encrypted is False
    assert file_info.is_deleted is False
    assert file_info.deleted_at is None
    assert file_info.meta == {}
    
    # Create a more complete FileInfo
    full_info = FileInfo(
        id=file_id,
        name="test.txt",
        size=1024,
        created_at=timestamp_ms(),
        extension="txt",
        sha256_hex="a" * 64,
        path="00/aa/test.txt",
        is_encrypted=True,
        is_deleted=True,
        deleted_at=timestamp_ms(),
        meta={"test": "metadata"}
    )
    
    # Check additional properties
    assert full_info.extension == "txt"
    assert full_info.sha256_hex == "a" * 64
    assert full_info.path == "00/aa/test.txt"
    assert full_info.is_encrypted is True
    assert full_info.is_deleted is True
    assert isinstance(full_info.deleted_at, int)
    assert full_info.meta == {"test": "metadata"}


def test_file_info_immutability() -> None:
    """Test that FileInfo objects are immutable."""
    file_info = FileInfo(
        id="test-id",
        name="test.txt",
        size=1024,
        created_at=timestamp_ms(),
    )
    
    # Attempt to modify properties should fail
    with pytest.raises(AttributeError):
        file_info.id = "new-id"
    
    with pytest.raises(AttributeError):
        file_info.name = "new.txt"


def test_file_info_formatted_properties() -> None:
    """Test the formatted properties of FileInfo."""
    # Use a fixed timestamp for consistent testing
    ts = 1577880000000  # 2020-01-01 00:00:00 UTC
    
    file_info = FileInfo(
        id="test-id",
        name="test.txt",
        size=1024 * 1024,  # 1 MB
        created_at=ts,
        deleted_at=ts + 3600000,  # 1 hour later
    )
    
    # Check formatted size
    assert file_info.formatted_size == "1.0 MB"
    
    # Check date formatting
    assert "2020" in file_info.created_date
    assert file_info.deleted_date is not None
    assert "2020" in file_info.deleted_date


def test_file_info_serialization() -> None:
    """Test serializing FileInfo to dict and JSON."""
    file_info = FileInfo(
        id="test-id",
        name="test.txt",
        size=1024,
        created_at=timestamp_ms(),
        extension="txt",
        meta={"key": "value"}
    )
    
    # Test dictionary serialization
    info_dict = file_info.to_dict()
    assert info_dict["id"] == "test-id"
    assert info_dict["name"] == "test.txt"
    assert info_dict["size"] == 1024
    assert "formatted_size" in info_dict
    assert info_dict["extension"] == "txt"
    assert info_dict["meta"] == {"key": "value"}
    
    # Test JSON serialization
    info_json = file_info.to_json()
    assert isinstance(info_json, str)
    
    # Should be valid JSON
    parsed = json.loads(info_json)
    assert parsed["id"] == "test-id"


def test_stats_creation() -> None:
    """Test creating a Stats object."""
    # Create a basic Stats object
    stats = Stats(
        total_files=100,
        total_size=1024 * 1024 * 100,  # 100 MB
        deleted_files=20,
        deleted_size=1024 * 1024 * 10,  # 10 MB
        encrypted_files=30,
        encrypted_size=1024 * 1024 * 30,  # 30 MB
    )
    
    # Check properties
    assert stats.total_files == 100
    assert stats.total_size == 1024 * 1024 * 100
    assert stats.deleted_files == 20
    assert stats.deleted_size == 1024 * 1024 * 10
    assert stats.encrypted_files == 30
    assert stats.encrypted_size == 1024 * 1024 * 30
    assert stats.extensions == {}
    
    # Create with extensions
    stats_with_ext = Stats(
        total_files=100,
        total_size=1024 * 1024 * 100,
        deleted_files=20,
        deleted_size=1024 * 1024 * 10,
        encrypted_files=30,
        encrypted_size=1024 * 1024 * 30,
        extensions={"txt": 50, "pdf": 30, "jpg": 20}
    )
    
    assert stats_with_ext.extensions == {"txt": 50, "pdf": 30, "jpg": 20}


def test_stats_immutability() -> None:
    """Test that Stats objects are immutable."""
    stats = Stats(
        total_files=100,
        total_size=1024 * 1024 * 100,
        deleted_files=20,
        deleted_size=1024 * 1024 * 10,
        encrypted_files=30,
        encrypted_size=1024 * 1024 * 30,
    )
    
    # Attempt to modify properties should fail
    with pytest.raises(AttributeError):
        stats.total_files = 200
    
    with pytest.raises(AttributeError):
        stats.total_size = 0


def test_stats_formatted_properties() -> None:
    """Test the formatted properties of Stats."""
    stats = Stats(
        total_files=100,
        total_size=1024 * 1024 * 100,  # 100 MB
        deleted_files=20,
        deleted_size=1024 * 1024 * 10,  # 10 MB
        encrypted_files=30,
        encrypted_size=1024 * 1024 * 30,  # 30 MB
    )
    
    # Check formatted sizes
    assert stats.formatted_total_size == "100.0 MB"
    assert stats.formatted_deleted_size == "10.0 MB"
    assert stats.formatted_encrypted_size == "30.0 MB"


def test_stats_serialization() -> None:
    """Test serializing Stats to dict and JSON."""
    stats = Stats(
        total_files=100,
        total_size=1024 * 1024 * 100,
        deleted_files=20,
        deleted_size=1024 * 1024 * 10,
        encrypted_files=30,
        encrypted_size=1024 * 1024 * 30,
        extensions={"txt": 50, "pdf": 30, "jpg": 20}
    )
    
    # Test dictionary serialization
    stats_dict = stats.to_dict()
    assert stats_dict["total_files"] == 100
    assert stats_dict["total_size"] == 1024 * 1024 * 100
    assert stats_dict["formatted_total_size"] == "100.0 MB"
    assert stats_dict["extensions"] == {"txt": 50, "pdf": 30, "jpg": 20}
    
    # Test JSON serialization
    stats_json = stats.to_json()
    assert isinstance(stats_json, str)
    
    # Should be valid JSON
    parsed = json.loads(stats_json)
    assert parsed["total_files"] == 100
    assert parsed["extensions"]["txt"] == 50
