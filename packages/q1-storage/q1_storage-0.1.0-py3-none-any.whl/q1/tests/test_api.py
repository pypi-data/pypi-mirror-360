"""
Tests for the Q1 main API.
"""
from __future__ import annotations

import json
import os
from io import BytesIO
from pathlib import Path

import pytest

from q1 import Q1
from q1.crypto import AesGcmCrypto
from q1.errors import (
    FileExists,
    FileMissing,
    IntegrityError,
    InvalidRoot,
    PathSecurityError,
    Q1Error,
)
from q1.models import FileInfo, Stats


def test_q1_initialization(temp_dir: Path) -> None:
    """Test initializing the Q1 storage."""
    # Initialize with an existing directory
    store = Q1(temp_dir)
    
    # Should create directories
    assert (temp_dir / "q1.db").exists()
    assert (temp_dir / ".tmp").is_dir()
    assert (temp_dir / ".trash").is_dir()
    
    store.close()
    
    # Initialize with a non-existent directory (should create it)
    new_dir = temp_dir / "new_storage"
    store2 = Q1(new_dir)
    
    assert new_dir.exists()
    assert (new_dir / "q1.db").exists()
    
    store2.close()
    
    # Initialize with a file (should raise error)
    file_path = temp_dir / "file.txt"
    with open(file_path, "w") as f:
        f.write("test")
    
    with pytest.raises(InvalidRoot):
        Q1(file_path)
    
    # Initialize with create=False on a non-existent directory
    non_existent = temp_dir / "does_not_exist"
    with pytest.raises(InvalidRoot):
        Q1(non_existent, create=False)


def test_q1_context_manager(temp_dir: Path) -> None:
    """Test using Q1 as a context manager."""
    # Should work with context manager
    with Q1(temp_dir) as store:
        assert isinstance(store, Q1)
        
        # Store should be usable
        file_id = store.put("test.txt", b"test content")
        assert isinstance(file_id, str)
    
    # Store should be closed after context
    with pytest.raises(Exception):
        # This will fail because the store is closed
        store.info(file_id)


def test_q1_put_get(q1_store: Q1) -> None:
    """Test basic put and get operations."""
    # Put a simple text file
    content = b"Hello, world!"
    file_id = q1_store.put("test.txt", content)
    
    # Get the file back
    retrieved = q1_store.get(file_id)
    assert retrieved == content
    
    # Check file info
    info = q1_store.info(file_id)
    assert isinstance(info, FileInfo)
    assert info.name == "test.txt"
    assert info.size == len(content)
    assert info.extension == "txt"
    assert not info.is_encrypted
    assert not info.is_deleted
    
    # Put with a file-like object
    bio = BytesIO(b"File-like content")
    file_id2 = q1_store.put("filelike.txt", bio)
    
    retrieved2 = q1_store.get(file_id2)
    assert retrieved2 == b"File-like content"


def test_q1_put_get_with_path(q1_store: Q1, temp_dir: Path) -> None:
    """Test put and get with file paths."""
    # Create a source file
    source_file = temp_dir / "source.txt"
    with open(source_file, "wb") as f:
        f.write(b"Path content")
    
    # Put using a Path
    file_id = q1_store.put("my_file.txt", source_file)
    
    # Get to a file path
    output_file = temp_dir / "output.txt"
    q1_store.get(file_id, output=output_file)
    
    # Should have created the output file
    assert output_file.exists()
    
    # Content should match
    with open(output_file, "rb") as f:
        content = f.read()
    assert content == b"Path content"


def test_q1_deduplication(q1_store: Q1) -> None:
    """Test file deduplication."""
    # Put the same content twice
    content = b"Duplicate content"
    file_id1 = q1_store.put("file1.txt", content)
    file_id2 = q1_store.put("file2.txt", content)
    
    # Should return the same ID
    assert file_id1 == file_id2
    
    # Info should show the original name
    info = q1_store.info(file_id1)
    assert info.name == "file1.txt"


def test_q1_stream(q1_store: Q1) -> None:
    """Test streaming file content."""
    # Create a larger file
    content = b"chunk" * 1000  # 5000 bytes
    file_id = q1_store.put("large.txt", content)
    
    # Stream in chunks
    chunks = list(q1_store.stream(file_id, chunk_size=1000))
    
    # Should have gotten 5 chunks
    assert len(chunks) == 5
    
    # Concatenated chunks should equal original
    assert b"".join(chunks) == content


def test_q1_delete_undelete(q1_store: Q1) -> None:
    """Test deleting and undeleting files."""
    content = b"Delete test"
    file_id = q1_store.put("delete.txt", content)
    
    # Soft delete
    q1_store.delete(file_id)
    
    # File should still be available by ID
    info = q1_store.info(file_id)
    assert info.is_deleted
    assert info.deleted_at is not None
    
    # But not in the default listing
    files = list(q1_store.list())
    assert file_id not in [f.id for f in files]
    
    # Should be in listing when include_deleted=True
    deleted_files = list(q1_store.list(include_deleted=True))
    assert file_id in [f.id for f in deleted_files]
    
    # Undelete
    q1_store.undelete(file_id)
    
    # Should no longer be marked deleted
    info = q1_store.info(file_id)
    assert not info.is_deleted
    assert info.deleted_at is None
    
    # Hard delete
    q1_store.delete(file_id, hard=True)
    
    # Should be completely gone
    with pytest.raises(FileMissing):
        q1_store.info(file_id)


def test_q1_list_and_filter(q1_store: Q1) -> None:
    """Test listing and filtering files."""
    # Add some files of different types
    q1_store.put("doc1.txt", b"Text file 1")
    q1_store.put("doc2.txt", b"Text file 2")
    q1_store.put("image.jpg", b"JPEG data")
    q1_store.put("data.bin", b"Binary data")
    
    # List all files
    all_files = list(q1_store.list())
    assert len(all_files) == 4
    
    # Filter by extension
    txt_files = list(q1_store.list(extension="txt"))
    assert len(txt_files) == 2
    assert all(f.extension == "txt" for f in txt_files)
    
    # Filter by name pattern
    doc_files = list(q1_store.list(name_like="doc"))
    assert len(doc_files) == 2
    assert all("doc" in f.name for f in doc_files)
    
    # Test pagination
    page1 = list(q1_store.list(limit=2))
    page2 = list(q1_store.list(limit=2, offset=2))
    assert len(page1) == 2
    assert len(page2) == 2
    
    # Should have different files
    page1_ids = [f.id for f in page1]
    page2_ids = [f.id for f in page2]
    assert not set(page1_ids).intersection(set(page2_ids))


def test_q1_metadata(q1_store: Q1) -> None:
    """Test file metadata."""
    # Store with metadata
    metadata = {"key": "value", "tags": ["test", "example"], "count": 42}
    file_id = q1_store.put("meta.txt", b"Content", metadata=metadata)
    
    # Get info and check metadata
    info = q1_store.info(file_id)
    assert info.meta == metadata
    
    # JSON serialization should include metadata
    json_str = info.to_json()
    data = json.loads(json_str)
    assert "meta" in data
    assert data["meta"] == metadata


@pytest.mark.skipif(not hasattr(AesGcmCrypto, "encrypt"), reason="cryptography not available")
def test_q1_encryption(encrypted_store: Q1) -> None:
    """Test file encryption."""
    content = b"Super secret content"
    file_id = encrypted_store.put("secret.txt", content)
    
    # Info should show encryption is used
    info = encrypted_store.info(file_id)
    assert info.is_encrypted
    
    # Retrieval should decrypt automatically
    retrieved = encrypted_store.get(file_id)
    assert retrieved == content
    
    # Streaming should also work with encrypted files
    chunks = list(encrypted_store.stream(file_id))
    assert b"".join(chunks) == content
    
    # Check that the data is actually encrypted on disk
    db = encrypted_store.db
    record = db.get_file_by_id(file_id)
    file_path = encrypted_store.root / record["path"]
    
    # Read raw data from disk
    with open(file_path, "rb") as f:
        raw_data = f.read()
    
    # Raw content should not contain the original text
    assert content not in raw_data


def test_q1_stats(q1_store: Q1) -> None:
    """Test storage statistics."""
    # Add some files of different types
    q1_store.put("doc1.txt", b"Text file 1")
    q1_store.put("doc2.txt", b"Text file 2")
    q1_store.put("image.jpg", b"JPEG data")
    q1_store.put("data.bin", b"Binary data")
    
    # Delete one file
    file_id = q1_store.put("to_delete.txt", b"Will be deleted")
    q1_store.delete(file_id)
    
    # Get stats
    stats = q1_store.stats()
    
    # Check basic stats
    assert isinstance(stats, Stats)
    assert stats.total_files == 4
    assert stats.deleted_files == 1
    assert stats.total_size > 0
    assert stats.deleted_size > 0
    
    # Check extensions
    assert "txt" in stats.extensions
    assert "jpg" in stats.extensions
    assert "bin" in stats.extensions
    assert stats.extensions["txt"] == 2  # Two active txt files


def test_q1_integrity_check(q1_store: Q1) -> None:
    """Test integrity checking."""
    # Add a file
    content = b"Test content for integrity check"
    file_id = q1_store.put("integrity.txt", content)
    
    # Run integrity check - should pass
    issues = q1_store.integrity_check()
    assert len(issues) == 0
    
    # Corrupt the file
    file_record = q1_store.db.get_file_by_id(file_id)
    file_path = q1_store.root / file_record["path"]
    with open(file_path, "wb") as f:
        f.write(b"Corrupted content")
    
    # Integrity check should now detect the issue
    issues = q1_store.integrity_check()
    assert len(issues) == 1
    assert "Integrity check failed" in issues[0]
    
    # Accessing the file should raise an error
    with pytest.raises(IntegrityError):
        q1_store.get(file_id)
    
    # Unless we don't verify
    info = q1_store.info(file_id, verify=False)  # Should not raise
    
    # But with verify=True it should raise
    with pytest.raises(IntegrityError):
        q1_store.info(file_id, verify=True)
    
    # Run integrity check with repair
    issues = q1_store.integrity_check(repair=True)
    assert len(issues) >= 1  # Should include the repair action
    
    # File should now be marked deleted
    info = q1_store.info(file_id)
    assert info.is_deleted


def test_q1_commit_rollback(storage_path: Path) -> None:
    """Test transaction operations."""
    # Create a new store
    store = Q1(storage_path)
    
    # Add a file
    file_id = store.put("test.txt", b"Test content")
    
    # File should be retrievable
    assert store.get(file_id) == b"Test content"
    
    # Close and reopen to verify persistence
    store.close()
    store2 = Q1(storage_path)
    
    # File should still be there
    assert store2.get(file_id) == b"Test content"
    
    # Explicit commit should work too
    file_id2 = store2.put("test2.txt", b"More content")
    store2.commit()
    
    store2.close()


def test_q1_vacuum(q1_store: Q1) -> None:
    """Test database and storage vacuuming."""
    # Add and delete some files
    for i in range(5):
        file_id = q1_store.put(f"file_{i}.txt", f"Content {i}".encode())
        if i % 2 == 0:
            q1_store.delete(file_id, hard=True)
    
    # Execute vacuum
    q1_store.vacuum()
    
    # Should still have files
    files = list(q1_store.list())
    assert len(files) == 2  # Files with odd i values
