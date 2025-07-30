"""
Filesystem utilities for Q1 storage.
"""
from __future__ import annotations

import fcntl
import os
import shutil
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterator, Optional
from uuid import UUID

from q1.errors import PathSecurityError, Q1Error


def check_path_safety(root_dir: Path, path: Path) -> Path:
    """Ensure a path is safely contained within the root directory.
    
    Args:
        root_dir: The root directory
        path: The path to check
        
    Returns:
        The absolute normalized path
        
    Raises:
        PathSecurityError: If the path is outside the root directory
    """
    # Ensure paths are absolute
    root_abs = root_dir.resolve()
    path_abs = path.resolve()
    
    # Check that path is within root
    if not str(path_abs).startswith(str(root_abs)):
        raise PathSecurityError(str(path))
    
    return path_abs


def ensure_directory(path: Path, mode: int = 0o700) -> Path:
    """Create a directory if it doesn't exist and set permissions.
    
    Args:
        path: The directory path
        mode: The permissions mode
        
    Returns:
        The directory path
    """
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, mode)
    return path


def get_shard_path(root: Path, file_id: UUID) -> Path:
    """Get the sharded path for a file.
    
    Args:
        root: The root directory
        file_id: The UUID of the file
        
    Returns:
        The sharded path (without filename)
    """
    # Convert UUID to string and remove hyphens
    id_str = str(file_id).replace("-", "")
    
    # Use first 2 chars for first level directory
    # and next 2 chars for second level directory
    dir1 = id_str[:2]
    dir2 = id_str[2:4]
    
    shard_path = root / dir1 / dir2
    ensure_directory(shard_path)
    
    return shard_path


def get_temp_dir(root: Path) -> Path:
    """Get the temp directory for the storage.
    
    Args:
        root: The storage root
        
    Returns:
        The temp directory path
    """
    temp_dir = root / ".tmp"
    ensure_directory(temp_dir)
    return temp_dir


def get_trash_dir(root: Path) -> Path:
    """Get the trash directory for the storage.
    
    Args:
        root: The storage root
        
    Returns:
        The trash directory path
    """
    trash_dir = root / ".trash"
    ensure_directory(trash_dir)
    return trash_dir


@contextmanager
def file_lock(path: Path) -> Generator[None, None, None]:
    """Acquire an exclusive lock on a file.
    
    Args:
        path: The file to lock
        
    Yields:
        None when the lock is acquired
        
    Raises:
        Q1Error: If the lock cannot be acquired
    """
    try:
        # Ensure the file exists
        if not path.exists():
            path.touch()
        
        # Open the file for locking (may not be the same as the data file)
        lock_file = open(path, "r+")
        try:
            # Try to acquire an exclusive lock
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                yield
            finally:
                # Release the lock
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        finally:
            lock_file.close()
    except IOError as e:
        raise Q1Error(f"Could not acquire lock on {path}: {e}") from e


def store_file(
    source_path: Path,
    target_dir: Path,
    filename: str,
    overwrite: bool = False,
    mode: int = 0o600,
) -> Path:
    """Store a file in the given directory with specific permissions.
    
    Args:
        source_path: Path to the source file
        target_dir: Directory to store the file in
        filename: Name to give the file
        overwrite: Whether to overwrite existing file
        mode: File permission mode
        
    Returns:
        Path to the stored file
        
    Raises:
        Q1Error: If the file cannot be stored
    """
    target_path = target_dir / filename
    
    if target_path.exists() and not overwrite:
        raise Q1Error(f"Target file already exists: {target_path}")
    
    # Copy the file
    try:
        shutil.copy2(source_path, target_path)
        os.chmod(target_path, mode)
    except (IOError, OSError) as e:
        raise Q1Error(f"Failed to store file: {e}") from e
    
    return target_path


def move_file(
    source_path: Path, target_dir: Path, filename: str, overwrite: bool = False, mode: int = 0o600
) -> Path:
    """Move a file to the given directory with specific permissions.
    
    Args:
        source_path: Path to the source file
        target_dir: Directory to move the file to
        filename: Name to give the file
        overwrite: Whether to overwrite existing file
        mode: File permission mode
        
    Returns:
        Path to the moved file
        
    Raises:
        Q1Error: If the file cannot be moved
    """
    target_path = target_dir / filename
    
    if target_path.exists():
        if overwrite:
            try:
                target_path.unlink()
            except OSError as e:
                raise Q1Error(f"Failed to remove existing file: {e}") from e
        else:
            raise Q1Error(f"Target file already exists: {target_path}")
    
    # Move the file
    try:
        shutil.move(source_path, target_path)
        os.chmod(target_path, mode)
    except (IOError, OSError) as e:
        raise Q1Error(f"Failed to move file: {e}") from e
    
    return target_path


def secure_delete(path: Path) -> None:
    """Securely delete a file.
    
    This doesn't guarantee secure deletion (depends on filesystem),
    but does basic checks and permissions operations.
    
    Args:
        path: The path to delete
        
    Raises:
        Q1Error: If the file cannot be deleted
    """
    try:
        # Check if file exists
        if not path.exists():
            return
        
        # Remove write protection
        os.chmod(path, 0o600)
        
        # Remove the file
        path.unlink()
    except OSError as e:
        raise Q1Error(f"Failed to delete file: {e}") from e


def list_files(directory: Path, pattern: Optional[str] = None) -> Iterator[Path]:
    """List all files in a directory, optionally filtering by pattern.
    
    Args:
        directory: The directory to list
        pattern: Optional glob pattern
        
    Returns:
        Iterator of file paths
    """
    if not directory.is_dir():
        return iter([])
    
    if pattern:
        return directory.glob(pattern)
    else:
        return (p for p in directory.iterdir() if p.is_file())
