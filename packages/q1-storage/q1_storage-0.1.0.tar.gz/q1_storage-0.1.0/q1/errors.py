"""
Exception classes for the Q1 storage library.
"""
from __future__ import annotations
from typing import Optional


class Q1Error(Exception):
    """Base exception for all Q1 storage library errors."""


class InvalidRoot(Q1Error):
    """Raised when the storage root is invalid or inaccessible."""

    def __init__(self, path: str, message: Optional[str] = None) -> None:
        self.path = path
        msg = f"Invalid storage root: {path}"
        if message:
            msg = f"{msg} ({message})"
        super().__init__(msg)


class FileMissing(Q1Error):
    """Raised when attempting to access a file that does not exist in the store."""

    def __init__(self, file_id: str) -> None:
        self.file_id = file_id
        super().__init__(f"File not found: {file_id}")


class FileExists(Q1Error):
    """Raised when attempting to create a file that already exists (with same content hash)."""

    def __init__(self, file_id: str) -> None:
        self.file_id = file_id
        super().__init__(f"File already exists: {file_id}")


class IntegrityError(Q1Error):
    """Raised when a file fails integrity verification."""

    def __init__(self, file_id: str) -> None:
        self.file_id = file_id
        super().__init__(f"Integrity check failed for file: {file_id}")


class EncryptionError(Q1Error):
    """Raised when encryption or decryption operations fail."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Encryption error: {message}")


class ConcurrencyError(Q1Error):
    """Raised when concurrent access conflicts occur."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Concurrency error: {message}")


class PathSecurityError(Q1Error):
    """Raised when a path traversal or other security violation is detected."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Path security violation detected: {path}")
