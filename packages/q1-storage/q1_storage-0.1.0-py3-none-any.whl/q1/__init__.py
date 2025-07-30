"""
Q1: Simple local file storage backed by SQLite with optional AES-GCM encryption.
"""
from __future__ import annotations

# Re-export the main API classes
from q1.api import Q1
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
from q1.models import FileInfo, Stats

# Package version
__version__ = "0.1.0"

# Public exports
__all__ = [
    "Q1",
    "FileInfo",
    "Stats",
    "Q1Error",
    "InvalidRoot",
    "FileMissing",
    "FileExists",
    "IntegrityError",
    "EncryptionError",
    "ConcurrencyError",
    "PathSecurityError",
    "__version__",
]
