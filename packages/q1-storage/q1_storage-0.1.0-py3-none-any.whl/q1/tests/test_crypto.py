"""
Tests for the crypto module.
"""
from __future__ import annotations

import os
import sys
from typing import Optional

import pytest

from q1.crypto import AesGcmCrypto, CryptoProvider, NullCrypto
from q1.errors import EncryptionError


def test_null_crypto() -> None:
    """Test the no-op crypto provider."""
    crypto = NullCrypto()
    
    # Test properties
    assert crypto.name == "null"
    
    # Test encryption
    plaintext = b"test data"
    encrypted, iv = crypto.encrypt(plaintext)
    
    # NullCrypto should return plaintext unchanged
    assert encrypted == plaintext
    # IV should be empty
    assert iv == b''
    
    # Test decryption
    decrypted = crypto.decrypt(encrypted, iv)
    assert decrypted == plaintext


def cryptography_available() -> bool:
    """Check if the cryptography library is available."""
    try:
        import cryptography
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not cryptography_available(), reason="cryptography library not available")
def test_aes_gcm_crypto_with_generated_key() -> None:
    """Test AES-GCM crypto with an auto-generated key."""
    try:
        crypto = AesGcmCrypto()
        
        # Test properties
        assert crypto.name == "aes-gcm"
        
        # Test encryption/decryption with a sample payload
        plaintext = b"test encryption data"
        encrypted, iv = crypto.encrypt(plaintext)
        
        # Encrypted should be different than plaintext
        assert encrypted != plaintext
        # IV should be 12 bytes (96 bits)
        assert len(iv) == 12
        
        # Test decryption
        decrypted = crypto.decrypt(encrypted, iv)
        assert decrypted == plaintext
        
        # Test decryption with wrong IV
        wrong_iv = os.urandom(12)
        with pytest.raises(EncryptionError):
            crypto.decrypt(encrypted, wrong_iv)
    
    except EncryptionError as e:
        if "AES-GCM encryption requires the 'cryptography' package" in str(e):
            # Skip the test if cryptography is not installed
            pytest.skip("cryptography package not installed")
        else:
            # Re-raise other encryption errors
            raise


@pytest.mark.skipif(not cryptography_available(), reason="cryptography library not available")
def test_aes_gcm_crypto_with_fixed_key() -> None:
    """Test AES-GCM crypto with a provided key."""
    # Use a fixed key for deterministic testing
    key = bytes(range(32))  # 32 bytes (0x00 to 0x1F)
    
    try:
        crypto = AesGcmCrypto(key=key)
        
        # Test encryption/decryption
        plaintext = b"test with fixed key"
        encrypted, iv = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted, iv)
        
        assert decrypted == plaintext
        
        # Create a second instance with the same key
        crypto2 = AesGcmCrypto(key=key)
        
        # Should be able to decrypt with the second instance
        decrypted2 = crypto2.decrypt(encrypted, iv)
        assert decrypted2 == plaintext
    
    except EncryptionError as e:
        if "AES-GCM encryption requires the 'cryptography' package" in str(e):
            # Skip the test if cryptography is not installed
            pytest.skip("cryptography package not installed")
        else:
            # Re-raise other encryption errors
            raise


@pytest.mark.skipif(not cryptography_available(), reason="cryptography library not available")
def test_aes_gcm_crypto_with_invalid_key() -> None:
    """Test AES-GCM crypto with an invalid key size."""
    # Key must be 32 bytes for AES-256
    invalid_key = b"too short"
    
    with pytest.raises(EncryptionError, match="AES-256 requires a 32-byte key"):
        AesGcmCrypto(key=invalid_key)


def test_crypto_provider_interface() -> None:
    """Test that crypto providers implement the interface properly."""
    # Create a concrete provider
    provider = NullCrypto()
    
    # Should have the required interface methods
    assert hasattr(provider, 'encrypt')
    assert hasattr(provider, 'decrypt')
    assert hasattr(provider, 'name')
    
    # Test calling the methods
    data = b"test data"
    encrypted, iv = provider.encrypt(data)
    decrypted = provider.decrypt(encrypted, iv)
    
    assert decrypted == data
