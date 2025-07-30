"""
Tests for Q1 error classes.
"""
import pytest
from q1.errors import (
    Q1Error,
    InvalidRoot,
    FileMissing,
    FileExists,
    IntegrityError,
    EncryptionError,
    ConcurrencyError,
    PathSecurityError,
)


def test_base_error() -> None:
    """Test the base Q1Error class."""
    error = Q1Error("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_invalid_root() -> None:
    """Test the InvalidRoot error class."""
    error = InvalidRoot("/invalid/path")
    assert "Invalid storage root: /invalid/path" in str(error)
    assert error.path == "/invalid/path"
    
    # Test with additional message
    error = InvalidRoot("/invalid/path", "Not a directory")
    assert "Invalid storage root: /invalid/path (Not a directory)" in str(error)
    assert error.path == "/invalid/path"
    

def test_file_missing() -> None:
    """Test the FileMissing error class."""
    file_id = "123e4567-e89b-12d3-a456-426614174000"
    error = FileMissing(file_id)
    assert f"File not found: {file_id}" in str(error)
    assert error.file_id == file_id


def test_file_exists() -> None:
    """Test the FileExists error class."""
    file_id = "123e4567-e89b-12d3-a456-426614174000"
    error = FileExists(file_id)
    assert f"File already exists: {file_id}" in str(error)
    assert error.file_id == file_id


def test_integrity_error() -> None:
    """Test the IntegrityError class."""
    file_id = "123e4567-e89b-12d3-a456-426614174000"
    error = IntegrityError(file_id)
    assert f"Integrity check failed for file: {file_id}" in str(error)
    assert error.file_id == file_id


def test_encryption_error() -> None:
    """Test the EncryptionError class."""
    message = "Invalid key size"
    error = EncryptionError(message)
    assert f"Encryption error: {message}" in str(error)


def test_concurrency_error() -> None:
    """Test the ConcurrencyError class."""
    message = "Database is locked"
    error = ConcurrencyError(message)
    assert f"Concurrency error: {message}" in str(error)


def test_path_security_error() -> None:
    """Test the PathSecurityError class."""
    path = "../../../etc/passwd"
    error = PathSecurityError(path)
    assert f"Path security violation detected: {path}" in str(error)
    assert error.path == path
