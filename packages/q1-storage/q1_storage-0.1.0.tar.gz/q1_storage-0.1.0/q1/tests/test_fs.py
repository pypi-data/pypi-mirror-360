"""
Tests for the filesystem helpers.
"""
from __future__ import annotations

import os
import stat
import tempfile
import threading
import uuid
from pathlib import Path

import pytest

from q1._internal.fs import (
    check_path_safety,
    ensure_directory,
    file_lock,
    get_shard_path,
    get_temp_dir,
    get_trash_dir,
    list_files,
    move_file,
    secure_delete,
    store_file,
)
from q1.errors import PathSecurityError, Q1Error


def test_path_safety(temp_dir: Path) -> None:
    """Test path safety checks."""
    # Same directory is safe
    safe_path = check_path_safety(temp_dir, temp_dir)
    assert safe_path == temp_dir.resolve()
    
    # Subdirectory is safe
    subdir = temp_dir / "subdir"
    safe_path = check_path_safety(temp_dir, subdir)
    assert safe_path == subdir.resolve()
    
    # Path outside of root should raise an error
    with pytest.raises(PathSecurityError):
        parent_dir = temp_dir.parent
        check_path_safety(temp_dir, parent_dir)
    
    # Path with symlink traversal should raise an error
    symlink_target = temp_dir.parent / "target"
    symlink_target.mkdir(exist_ok=True)
    symlink_path = temp_dir / "symlink"
    os.symlink(str(symlink_target), str(symlink_path))
    
    with pytest.raises(PathSecurityError):
        check_path_safety(temp_dir, symlink_path)


def test_ensure_directory(temp_dir: Path) -> None:
    """Test directory creation with permissions."""
    # Create a new directory
    new_dir = temp_dir / "new_dir"
    created_dir = ensure_directory(new_dir)
    
    assert created_dir == new_dir
    assert new_dir.exists()
    assert new_dir.is_dir()
    
    # Check permissions (should be 0o700 by default)
    mode = stat.S_IMODE(os.stat(new_dir).st_mode)
    assert mode == 0o700
    
    # Create with custom permissions
    custom_dir = temp_dir / "custom_dir"
    custom_created = ensure_directory(custom_dir, mode=0o755)
    
    assert custom_created == custom_dir
    mode = stat.S_IMODE(os.stat(custom_dir).st_mode)
    assert mode == 0o755
    
    # Creating an existing directory should not raise an error
    ensure_directory(new_dir)
    assert new_dir.exists()


def test_shard_path(temp_dir: Path) -> None:
    """Test sharded path generation."""
    root = temp_dir / "store"
    file_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
    
    shard_path = get_shard_path(root, file_id)
    
    # First two chars of UUID (without dashes): 12
    # Next two chars: 3e
    expected_path = root / "12" / "3e"
    
    assert shard_path == expected_path
    assert shard_path.exists()
    
    # Check that the directories were created
    first_level = root / "12"
    second_level = root / "12" / "3e"
    
    assert first_level.is_dir()
    assert second_level.is_dir()


def test_special_directories(temp_dir: Path) -> None:
    """Test temp and trash directory creation."""
    root = temp_dir / "store"
    
    temp_dir_path = get_temp_dir(root)
    trash_dir_path = get_trash_dir(root)
    
    assert temp_dir_path == root / ".tmp"
    assert trash_dir_path == root / ".trash"
    
    assert temp_dir_path.exists() and temp_dir_path.is_dir()
    assert trash_dir_path.exists() and trash_dir_path.is_dir()


def test_file_lock(temp_dir: Path) -> None:
    """Test file locking mechanism."""
    lock_file = temp_dir / "lock.file"
    
    # Basic locking should work
    with file_lock(lock_file):
        # File should exist after acquiring lock
        assert lock_file.exists()
    
    # Test conflicting locks
    lock_acquired = [False, False]
    
    def try_lock(index: int) -> None:
        try:
            with file_lock(lock_file):
                # Remember this thread acquired the lock
                lock_acquired[index] = True
                # Hold the lock for a moment
                threading.Event().wait(0.1)
        except Q1Error:
            # Lock acquisition failed, which is expected for one thread
            pass
    
    # Start two threads trying to acquire the same lock
    t1 = threading.Thread(target=try_lock, args=(0,))
    t2 = threading.Thread(target=try_lock, args=(1,))
    
    t1.start()
    # Give first thread a chance to acquire the lock
    threading.Event().wait(0.05)
    t2.start()
    
    t1.join()
    t2.join()
    
    # Verify that only one thread got the lock
    assert sum(lock_acquired) == 1


def test_store_file(temp_dir: Path) -> None:
    """Test storing files."""
    source_dir = temp_dir / "source"
    target_dir = temp_dir / "target"
    
    ensure_directory(source_dir)
    ensure_directory(target_dir)
    
    # Create a source file
    source_file = source_dir / "test.txt"
    with open(source_file, "w") as f:
        f.write("test content")
    
    # Store the file
    stored_path = store_file(source_file, target_dir, "stored.txt")
    
    assert stored_path == target_dir / "stored.txt"
    assert stored_path.exists()
    
    # Check content
    with open(stored_path, "r") as f:
        content = f.read()
    assert content == "test content"
    
    # Check permissions (should be 0o600 by default)
    mode = stat.S_IMODE(os.stat(stored_path).st_mode)
    assert mode == 0o600
    
    # Test overwrite behavior
    with pytest.raises(Q1Error):
        store_file(source_file, target_dir, "stored.txt", overwrite=False)
    
    # Should succeed with overwrite=True
    stored_path2 = store_file(source_file, target_dir, "stored.txt", overwrite=True)
    assert stored_path2 == stored_path
    
    # Test with custom mode
    custom_path = store_file(source_file, target_dir, "custom.txt", mode=0o644)
    custom_mode = stat.S_IMODE(os.stat(custom_path).st_mode)
    assert custom_mode == 0o644


def test_move_file(temp_dir: Path) -> None:
    """Test moving files."""
    source_dir = temp_dir / "source"
    target_dir = temp_dir / "target"
    
    ensure_directory(source_dir)
    ensure_directory(target_dir)
    
    # Create a source file
    source_file = source_dir / "test.txt"
    with open(source_file, "w") as f:
        f.write("test content")
    
    # Move the file
    moved_path = move_file(source_file, target_dir, "moved.txt")
    
    assert moved_path == target_dir / "moved.txt"
    assert moved_path.exists()
    assert not source_file.exists()
    
    # Check content
    with open(moved_path, "r") as f:
        content = f.read()
    assert content == "test content"
    
    # Create a new source file for overwrite testing
    with open(source_file, "w") as f:
        f.write("new content")
    
    # Test overwrite behavior
    with pytest.raises(Q1Error):
        move_file(source_file, target_dir, "moved.txt", overwrite=False)
    
    # Source file should still exist
    assert source_file.exists()
    
    # Should succeed with overwrite=True
    moved_path2 = move_file(source_file, target_dir, "moved.txt", overwrite=True)
    assert moved_path2 == moved_path
    assert not source_file.exists()
    
    # Check that content was updated
    with open(moved_path2, "r") as f:
        content = f.read()
    assert content == "new content"


def test_secure_delete(temp_dir: Path) -> None:
    """Test secure file deletion."""
    # Create a test file
    test_file = temp_dir / "test.txt"
    with open(test_file, "w") as f:
        f.write("sensitive data")
    
    # Make file read-only
    os.chmod(test_file, 0o400)
    
    # Delete the file
    secure_delete(test_file)
    
    # File should be gone
    assert not test_file.exists()
    
    # Deleting a non-existent file should not raise an error
    secure_delete(test_file)


def test_list_files(temp_dir: Path) -> None:
    """Test listing files in a directory."""
    # Create some files
    for i in range(5):
        with open(temp_dir / f"test_{i}.txt", "w") as f:
            f.write(f"content {i}")
    
    # Create a subdirectory with files
    subdir = temp_dir / "subdir"
    ensure_directory(subdir)
    with open(subdir / "subfile.txt", "w") as f:
        f.write("subdir content")
    
    # List all files
    files = list(list_files(temp_dir))
    assert len(files) == 5
    
    # List with pattern
    txt_files = list(list_files(temp_dir, "*.txt"))
    assert len(txt_files) == 5
    
    pattern_files = list(list_files(temp_dir, "test_[12].txt"))
    assert len(pattern_files) == 2
    assert temp_dir / "test_1.txt" in pattern_files
    assert temp_dir / "test_2.txt" in pattern_files
    
    # List non-existent directory
    non_existent = list(list_files(temp_dir / "non_existent"))
    assert len(non_existent) == 0
