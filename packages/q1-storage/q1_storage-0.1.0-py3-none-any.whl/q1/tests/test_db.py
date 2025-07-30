"""
Tests for the database layer.
"""
from __future__ import annotations

import os
import sqlite3
import time
import uuid
from pathlib import Path

import pytest

from q1._internal.db import Database
from q1.errors import Q1Error


def test_database_initialization(temp_dir: Path) -> None:
    """Test database initialization and schema creation."""
    db = Database(temp_dir)
    
    # Check that the database file was created
    assert os.path.exists(temp_dir / "q1.db")
    
    # Check that the schema was applied
    result = db.query("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
    assert len(result) == 1
    assert result[0]["name"] == "files"
    
    # Check user_version is set (should be 1 from schema.sql)
    result = db.query("PRAGMA user_version;")
    assert result[0]["user_version"] == 1
    
    # Check that WAL is enabled
    result = db.query("PRAGMA journal_mode;")
    assert result[0]["journal_mode"].upper() == "WAL"
    
    # Verify foreign keys are enabled
    result = db.query("PRAGMA foreign_keys;")
    assert result[0]["foreign_keys"] == 1
    
    db.close()


def test_database_transaction(temp_dir: Path) -> None:
    """Test transaction support."""
    db = Database(temp_dir)
    
    # Create a temporary table for testing
    db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);")
    
    # Test a successful transaction
    with db.transaction() as conn:
        conn.execute("INSERT INTO test (value) VALUES (?)", ("test1",))
        conn.execute("INSERT INTO test (value) VALUES (?)", ("test2",))
    
    # Values should be committed
    result = db.query("SELECT value FROM test ORDER BY id;")
    assert len(result) == 2
    assert result[0]["value"] == "test1"
    assert result[1]["value"] == "test2"
    
    # Test a failed transaction
    try:
        with db.transaction() as conn:
            conn.execute("INSERT INTO test (value) VALUES (?)", ("test3",))
            # This will fail (try to insert a duplicate primary key)
            conn.execute("INSERT INTO test (id, value) VALUES (1, 'duplicate')")
    except Q1Error:
        pass  # Expected
    
    # Should still have only the first two rows
    result = db.query("SELECT value FROM test ORDER BY id;")
    assert len(result) == 2
    assert result[0]["value"] == "test1"
    assert result[1]["value"] == "test2"
    
    db.close()


def test_file_operations(temp_dir: Path) -> None:
    """Test file database operations."""
    db = Database(temp_dir)
    
    # Create a test file record
    file_id = str(uuid.uuid4())
    file_name = "test.txt"
    file_ext = "txt"
    file_size = 42
    file_hash = os.urandom(32)  # Random 32-byte SHA256 hash
    file_path = "00/aa/test.txt"
    
    # Add the file
    db.add_file(
        file_id=file_id,
        name=file_name,
        ext=file_ext,
        size=file_size,
        sha256=file_hash,
        iv=None,  # No encryption
        path=file_path,
        meta_json='{"test": "metadata"}'
    )
    
    # Retrieve and verify
    file_record = db.get_file_by_id(file_id)
    assert file_record is not None
    assert file_record["id"] == file_id
    assert file_record["name"] == file_name
    assert file_record["ext"] == file_ext
    assert file_record["size"] == file_size
    assert file_record["sha256"] == file_hash
    assert file_record["iv"] is None
    assert file_record["path"] == file_path
    assert file_record["meta_json"] == '{"test": "metadata"}'
    assert file_record["deleted"] == 0
    assert file_record["deleted_at"] is None
    
    # Test get by hash
    file_by_hash = db.get_file_by_hash(file_hash)
    assert file_by_hash is not None
    assert file_by_hash["id"] == file_id
    
    # Test update
    db.update_file(file_id, name="updated.txt", meta_json='{"updated": true}')
    
    updated_file = db.get_file_by_id(file_id)
    assert updated_file is not None
    assert updated_file["name"] == "updated.txt"
    assert updated_file["meta_json"] == '{"updated": true}'
    
    # Test soft delete
    db.soft_delete(file_id)
    
    deleted_file = db.get_file_by_id(file_id)
    assert deleted_file is not None
    assert deleted_file["deleted"] == 1
    assert deleted_file["deleted_at"] is not None
    
    # Test undelete
    db.undelete(file_id)
    
    restored_file = db.get_file_by_id(file_id)
    assert restored_file is not None
    assert restored_file["deleted"] == 0
    assert restored_file["deleted_at"] is None
    
    # Test hard delete
    db.hard_delete(file_id)
    
    # File should be gone
    assert db.get_file_by_id(file_id) is None
    
    db.close()


def test_file_listing(temp_dir: Path) -> None:
    """Test file listing with filters."""
    db = Database(temp_dir)
    
    # Add some test files
    for i in range(10):
        ext = "txt" if i % 2 == 0 else "bin"
        file_id = str(uuid.uuid4())
        db.add_file(
            file_id=file_id,
            name=f"test_{i}.{ext}",
            ext=ext,
            size=100 + i,
            sha256=os.urandom(32),
            iv=None,
            path=f"00/bb/test_{i}.{ext}",
        )
        
        # Mark some as deleted
        if i % 3 == 0:
            db.soft_delete(file_id)
    
    # Test basic listing (active files only)
    files = db.list_files()
    # 10 total - 4 deleted (for i in 0, 3, 6, 9)
    assert len(files) == 6
    
    # Test extension filter
    txt_files = db.list_files(extension="txt")
    # 5 txt files (i=0,2,4,6,8) - 2 deleted (i=0,6)
    assert len(txt_files) == 3
    
    # Test name filter
    name_files = db.list_files(name_like="test_1")
    assert len(name_files) == 1  # test_1 (not deleted)
    
    # Test include_deleted
    all_files = db.list_files(include_deleted=True)
    assert len(all_files) == 10
    
    # Test limit and offset
    limited_files = db.list_files(limit=3)
    assert len(limited_files) == 3
    
    offset_files = db.list_files(limit=3, offset=3)
    assert len(offset_files) == 3
    # Make sure we got different sets
    assert {f["id"] for f in limited_files}.isdisjoint({f["id"] for f in offset_files})
    
    db.close()


def test_error_handling(temp_dir: Path) -> None:
    """Test error conditions and handling."""
    db = Database(temp_dir)
    
    # Invalid file ID
    with pytest.raises(Q1Error):
        db.update_file("non-existent-id", name="test")
    
    # Soft delete non-existent
    with pytest.raises(Q1Error):
        db.soft_delete("non-existent-id")
    
    # Add file with existing ID
    file_id = str(uuid.uuid4())
    db.add_file(
        file_id=file_id,
        name="test.txt",
        ext="txt",
        size=100,
        sha256=os.urandom(32),
        iv=None,
        path="00/cc/test.txt",
    )
    
    # Try to add a file with the same ID (should fail)
    with pytest.raises(Exception):
        db.add_file(
            file_id=file_id,  # Same ID
            name="another.txt",
            ext="txt",
            size=200,
            sha256=os.urandom(32),
            iv=None,
            path="00/dd/another.txt",
        )
    
    # Double delete
    db.soft_delete(file_id)
    with pytest.raises(Q1Error):
        db.soft_delete(file_id)
    
    # Undelete non-deleted file
    db.undelete(file_id)
    with pytest.raises(Q1Error):
        db.undelete(file_id)
    
    db.close()


def test_integrity_check(temp_dir: Path) -> None:
    """Test database integrity check."""
    db = Database(temp_dir)
    
    # Database should be valid initially
    assert db.integrity_check()
    
    db.close()


def test_vacuum(temp_dir: Path) -> None:
    """Test database vacuum operation."""
    db = Database(temp_dir)
    
    # Add and delete some data to have something to vacuum
    for i in range(10):
        file_id = str(uuid.uuid4())
        db.add_file(
            file_id=file_id,
            name=f"test_{i}.txt",
            ext="txt",
            size=100,
            sha256=os.urandom(32),
            iv=None,
            path=f"00/ee/test_{i}.txt",
        )
        
        if i % 2 == 0:
            db.hard_delete(file_id)
    
    # Get file size before vacuum
    db_size_before = os.path.getsize(temp_dir / "q1.db")
    
    # Run vacuum
    db.vacuum()
    
    # Size might be different (typically smaller, but could be larger 
    # due to page allocation strategy)
    db_size_after = os.path.getsize(temp_dir / "q1.db")
    
    # Vacuum should have run without errors, but we don't guarantee size change
    
    db.close()
