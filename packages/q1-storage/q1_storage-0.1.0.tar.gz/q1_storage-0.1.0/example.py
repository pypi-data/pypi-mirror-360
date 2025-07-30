#!/usr/bin/env python3
"""
Q1 Storage Library - Usage Examples

This script demonstrates basic usage patterns for the Q1 storage library.
"""
import json
import os
import random
import tempfile
from pathlib import Path

from q1 import Q1, FileInfo
from q1.crypto import AesGcmCrypto


def print_separator(title):
    """Print a section separator with title."""
    print("\n" + "=" * 70)
    print(f" {title} ".center(70, "="))
    print("=" * 70 + "\n")


def basic_usage():
    """Demonstrate basic file operations."""
    print_separator("Basic Usage")
    
    # Create a temporary storage directory for the example
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "q1_store"
        
        print(f"Creating storage at: {storage_path}")
        
        # Create a new storage instance using a context manager
        with Q1(storage_path) as store:
            # Store some text content
            content = b"Hello, world! This is a test file."
            file_id = store.put("example.txt", content)
            print(f"Stored text file with ID: {file_id}")
            
            # Retrieve the content
            retrieved_content = store.get(file_id)
            print(f"Retrieved content: {retrieved_content.decode()}")
            
            # Get file information
            info = store.info(file_id)
            print("\nFile information:")
            print(f"  ID: {info.id}")
            print(f"  Name: {info.name}")
            print(f"  Size: {info.formatted_size} ({info.size} bytes)")
            print(f"  Created: {info.created_date}")
            print(f"  Extension: {info.extension}")
            print(f"  SHA-256: {info.sha256_hex}")
            
            # Store a binary file
            binary_data = bytes([random.randint(0, 255) for _ in range(1000)])
            bin_id = store.put("binary.bin", binary_data)
            print(f"\nStored binary file with ID: {bin_id}")
            
            # List all files in the store
            print("\nFiles in storage:")
            for file_info in store.list():
                print(f"  {file_info.id} - {file_info.name} ({file_info.formatted_size})")
            
            # Stream content in chunks (useful for large files)
            print("\nStreaming file content in chunks:")
            chunks = list(store.stream(file_id))
            print(f"  Number of chunks: {len(chunks)}")
            print(f"  First chunk: {chunks[0][:20]}...")
            
            # Delete a file (soft delete by default)
            print("\nSoft-deleting file...")
            store.delete(file_id)
            
            # Verify it's marked as deleted
            info = store.info(file_id)
            print(f"  File is_deleted: {info.is_deleted}")
            
            # Files don't show up in normal listing when deleted
            print("\nFiles after delete (should show only binary file):")
            for file_info in store.list():
                print(f"  {file_info.id} - {file_info.name}")
            
            # But can be included with a flag
            print("\nAll files including deleted:")
            for file_info in store.list(include_deleted=True):
                status = "[DELETED]" if file_info.is_deleted else "[ACTIVE]"
                print(f"  {status} {file_info.id} - {file_info.name}")
            
            # Undelete the file
            print("\nUndeleting file...")
            store.undelete(file_id)
            
            # Verify it's no longer marked as deleted
            info = store.info(file_id)
            print(f"  File is_deleted: {info.is_deleted}")
            
            # Hard delete permanently removes the file
            print("\nHard-deleting file...")
            store.delete(file_id, hard=True)
            
            # Try to get info (should raise FileMissing exception)
            print("\nAttempting to get info after hard delete:")
            try:
                store.info(file_id)
                print("  File still exists (unexpected)")
            except Exception as e:
                print(f"  Expected error: {e}")
            
            # Get storage statistics
            stats = store.stats()
            print("\nStorage statistics:")
            print(f"  Total files: {stats.total_files}")
            print(f"  Total size: {stats.formatted_total_size}")
            print(f"  Deleted files: {stats.deleted_files}")
            
            # Running integrity check
            print("\nRunning integrity check:")
            issues = store.integrity_check()
            if issues:
                print(f"  Found {len(issues)} issues:")
                for issue in issues:
                    print(f"    - {issue}")
            else:
                print("  No issues found - integrity check passed")


def working_with_paths():
    """Demonstrate working with file paths."""
    print_separator("Working with Paths")
    
    # Create a temporary storage directory
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "q1_store"
        
        # Create a temporary file to import
        src_file = Path(temp_dir) / "source.txt"
        with open(src_file, "w") as f:
            f.write("This is a file imported from a path")
        
        # Create a storage instance
        store = Q1(storage_path)
        
        # Import the file
        file_id = store.put("imported.txt", src_file)
        print(f"Imported file with ID: {file_id}")
        
        # Export to a new location
        output_path = Path(temp_dir) / "exported.txt"
        store.get(file_id, output=output_path)
        print(f"Exported file to: {output_path}")
        
        # Verify the exported content
        with open(output_path, "r") as f:
            content = f.read()
        print(f"Exported content: {content}")
        
        store.close()


def working_with_metadata():
    """Demonstrate storing and retrieving metadata."""
    print_separator("Working with Metadata")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "q1_store"
        store = Q1(storage_path)
        
        # Metadata can be any JSON-serializable object
        metadata = {
            "creator": "Example Script",
            "tags": ["example", "demo", "test"],
            "description": "A file with metadata",
            "rating": 5,
            "nested": {
                "more": "data",
                "values": [1, 2, 3]
            }
        }
        
        # Store a file with metadata
        file_id = store.put("metadata_example.txt", b"Content with metadata", metadata=metadata)
        print(f"Stored file with ID: {file_id}")
        
        # Retrieve and inspect the metadata
        info = store.info(file_id)
        print("\nRetrieved metadata:")
        print(json.dumps(info.meta, indent=2))
        
        # Direct access to metadata items
        print(f"\nDirectly accessing metadata:")
        print(f"  Creator: {info.meta.get('creator')}")
        print(f"  Tags: {', '.join(info.meta.get('tags', []))}")
        print(f"  Rating: {info.meta.get('rating')}")
        
        store.close()


def using_encryption():
    """Demonstrate using encryption."""
    print_separator("Using Encryption")
    
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        print("Cryptography package not installed. Skipping encryption example.")
        print("To use encryption, install with: pip install q1[crypto]")
        return
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "q1_store"
        
        # Create a secure random key (in a real app, you'd need to securely store this key)
        key = os.urandom(32)  # 32 bytes for AES-256
        print(f"Generated a random 32-byte encryption key")
        
        # Create a crypto provider
        crypto = AesGcmCrypto(key=key)
        
        # Create an encrypted store
        store = Q1(storage_path, crypto_provider=crypto)
        
        # Store some sensitive data
        content = b"This is confidential information that will be encrypted"
        file_id = store.put("secret.txt", content)
        print(f"Stored encrypted file with ID: {file_id}")
        
        # Verify the file is marked as encrypted
        info = store.info(file_id)
        print(f"File is_encrypted: {info.is_encrypted}")
        
        # Retrieval automatically decrypts
        retrieved = store.get(file_id)
        print(f"Retrieved decrypted content: {retrieved.decode()}")
        
        # Check the raw file on disk to confirm it's encrypted
        file_path = Path(storage_path) / info.path
        with open(file_path, "rb") as f:
            raw_data = f.read()
        
        # The raw data shouldn't contain our plaintext
        plaintext_in_raw = content in raw_data
        print(f"Raw data contains plaintext: {plaintext_in_raw} (should be False)")
        print(f"First 16 bytes of raw data: {raw_data[:16].hex()}")
        
        # Create a new store instance with the same key to demonstrate persistence
        store.close()
        store2 = Q1(storage_path, crypto_provider=AesGcmCrypto(key=key))
        
        # We can still retrieve and decrypt the file with the same key
        retrieved2 = store2.get(file_id)
        print(f"\nRetrieved with new store instance: {retrieved2.decode()}")
        
        # But if we use a different key, decryption would fail
        wrong_key = os.urandom(32)
        store3 = Q1(storage_path, crypto_provider=AesGcmCrypto(key=wrong_key))
        
        print("\nTrying to access with wrong key:")
        try:
            store3.get(file_id)
            print("  Retrieved successfully (unexpected)")
        except Exception as e:
            print(f"  Expected error: {type(e).__name__}: {str(e)}")
        
        store2.close()
        store3.close()


if __name__ == "__main__":
    # Run the examples
    basic_usage()
    working_with_paths()
    working_with_metadata()
    using_encryption()
    
    print("\nExamples completed. See the code for more details on usage patterns.")
