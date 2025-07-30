"""
Cryptographic utilities and providers for Q1 storage.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from q1.errors import EncryptionError


class CryptoProvider(ABC):
    """Abstract base class for crypto providers in Q1."""
    
    @abstractmethod
    def encrypt(self, data: bytes) -> Tuple[bytes, bytes]:
        """Encrypt data.
        
        Args:
            data: The data to encrypt
            
        Returns:
            Tuple of (encrypted_data, iv)
            
        Raises:
            EncryptionError: If encryption fails
        """
        pass
    
    @abstractmethod
    def decrypt(self, data: bytes, iv: bytes) -> bytes:
        """Decrypt data.
        
        Args:
            data: The data to decrypt
            iv: The initialization vector or nonce
            
        Returns:
            Decrypted data
            
        Raises:
            EncryptionError: If decryption fails
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the crypto provider.
        
        Returns:
            Provider name
        """
        pass


class NullCrypto(CryptoProvider):
    """A crypto provider that does no encryption.
    
    This is the default provider and just passes data through.
    """
    
    def encrypt(self, data: bytes) -> Tuple[bytes, bytes]:
        """Pass through data with no encryption.
        
        Args:
            data: The data to "encrypt"
        
        Returns:
            Tuple of (data, empty IV)
        """
        return data, b''
    
    def decrypt(self, data: bytes, iv: bytes) -> bytes:
        """Pass through data with no decryption.
        
        Args:
            data: The data to "decrypt"
            iv: Ignored
            
        Returns:
            The input data unchanged
        """
        return data
    
    @property
    def name(self) -> str:
        """Get the name of the crypto provider.
        
        Returns:
            "null" (indicating no encryption)
        """
        return "null"


try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    
    class AesGcmCrypto(CryptoProvider):
        """AES-GCM encryption provider using the cryptography library.
        
        Requires the optional cryptography dependency.
        """
        
        def __init__(self, key: Optional[bytes] = None, aad: bytes = b'q1-aes-gcm'):
            """Initialize AES-GCM crypto provider.
            
            Args:
                key: Optional 32-byte encryption key. If not provided, one will 
                    be generated.
                aad: Associated authenticated data for GCM.
                
            Raises:
                EncryptionError: If the key is not 32 bytes or if the cryptography
                    library is not available.
            """
            if key is None:
                # Generate a random key
                self._key = os.urandom(32)
            else:
                if len(key) != 32:
                    raise EncryptionError("AES-256 requires a 32-byte key")
                self._key = key
            
            self._aad = aad
            self._gcm = AESGCM(self._key)
        
        def encrypt(self, data: bytes) -> Tuple[bytes, bytes]:
            """Encrypt data using AES-GCM. 
            TODO: (GCM with the same iv shouldn't be used with files over 64GB, those need to be chunked.)
            
            Args:
                data: The data to encrypt
                
            Returns:
                Tuple of (encrypted_data with auth tag, nonce)
                
            Raises:
                EncryptionError: If encryption fails
            """
            try:
                # Generate a random 96-bit IV (12 bytes) as recommended for GCM
                iv = os.urandom(12)
                
                # Encrypt and authenticate
                encrypted = self._gcm.encrypt(iv, data, self._aad)
                
                return encrypted, iv
            except Exception as e:
                raise EncryptionError(f"AES-GCM encryption failed: {e}") from e
        
        def decrypt(self, data: bytes, iv: bytes) -> bytes:
            """Decrypt data using AES-GCM.
            
            Args:
                data: The encrypted data with auth tag
                iv: The 96-bit IV/nonce used for encryption
                
            Returns:
                Decrypted data
                
            Raises:
                EncryptionError: If decryption or authentication fails
            """
            try:
                return self._gcm.decrypt(iv, data, self._aad)
            except Exception as e:
                raise EncryptionError(f"AES-GCM decryption failed: {e}") from e
        
        @property
        def name(self) -> str:
            """Get the name of the crypto provider.
            
            Returns:
                "aes-gcm"
            """
            return "aes-gcm"
    
except ImportError:
    # Define a placeholder that raises an error if used
    class AesGcmCrypto(CryptoProvider):  # type: ignore
        """Placeholder for AES-GCM crypto provider.
        
        This class is a placeholder that raises an error if used without
        the cryptography library installed.
        """
        
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Raise an error indicating the cryptography library is required.
            
            Raises:
                EncryptionError: Always raised
            """
            raise EncryptionError(
                "AES-GCM encryption requires the 'cryptography' package. "
                "Install with 'pip install q1[crypto]'."
            )
        
        def encrypt(self, data: bytes) -> Tuple[bytes, bytes]:
            """Not implemented - raises an error.
            
            Raises:
                EncryptionError: Always
            """
            raise EncryptionError("Cryptography library not available")
        
        def decrypt(self, data: bytes, iv: bytes) -> bytes:
            """Not implemented - raises an error.
            
            Raises:
                EncryptionError: Always
            """
            raise EncryptionError("Cryptography library not available")
        
        @property
        def name(self) -> str:
            """Get the name of the crypto provider.
            
            Returns:
                "aes-gcm-unavailable"
            """
            return "aes-gcm-unavailable"
