"""
Pytest configuration and shared fixtures.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator, Iterator

import pytest

from q1 import Q1
from q1.crypto import AesGcmCrypto, NullCrypto


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests.
    
    The directory is automatically cleaned up after the test completes.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def storage_path(temp_dir: Path) -> Path:
    """Create a storage path for tests."""
    storage_dir = temp_dir / "storage"
    storage_dir.mkdir(exist_ok=True)
    return storage_dir


@pytest.fixture
def q1_store(storage_path: Path) -> Generator[Q1, None, None]:
    """Create a Q1 storage instance for testing.
    
    The store is automatically closed after the test.
    """
    store = Q1(storage_path)
    try:
        yield store
    finally:
        store.close()


@pytest.fixture
def encrypted_store(storage_path: Path) -> Generator[Q1, None, None]:
    """Create an encrypted Q1 storage instance for testing.
    
    The store is automatically closed after the test.
    """
    # Using a deterministic key for testing - never do this in production!
    test_key = bytes(range(32))  # 32-byte key with predictable content
    crypto = AesGcmCrypto(key=test_key)
    
    store = Q1(storage_path, crypto_provider=crypto)
    try:
        yield store
    finally:
        store.close()
