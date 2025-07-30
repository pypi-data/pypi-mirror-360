# Q1 Storage Library - API Documentation

This document provides a detailed overview of all public interfaces in the Q1 storage library and demonstrates how to use them in different scenarios.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Q1 Class](#q1-class)
  - [Initialization](#initialization)
  - [File Operations](#file-operations)
  - [Information and Listing](#information-and-listing)
  - [Deletion and Recovery](#deletion-and-recovery)
  - [Maintenance Operations](#maintenance-operations)
  - [Transaction Control](#transaction-control)
  - [Context Manager Support](#context-manager-support)
- [Data Models](#data-models)
  - [FileInfo](#fileinfo)
  - [Stats](#stats)
- [Crypto Providers](#crypto-providers)
  - [NullCrypto](#nullcrypto)
  - [AesGcmCrypto](#aesgcmcrypto)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)
  - [Working with Metadata](#working-with-metadata)
  - [File Deduplication](#file-deduplication)
  - [Streaming Large Files](#streaming-large-files)
  - [Customizing the Storage Layout](#customizing-the-storage-layout)
  - [Concurrency Control](#concurrency-control)

---

## Core Concepts

Q1 is a file storage library that provides a simple API for storing and retrieving files with SQLite as the backend and optional AES-256-GCM encryption. Key features include:

- **ACID transactions**: All operations are wrapped in transactions for data consistency
- **File deduplication**: Files with identical content are automatically deduplicated
- **File integrity**: SHA-256 hashing ensures file integrity
- **Encryption**: Optional AES-256-GCM encryption for data at rest
- **Soft/hard deletion**: Files can be soft-deleted and recovered, or permanently deleted
- **Sharded storage**: Files are stored in a sharded directory structure for better performance with large numbers of files

## Q1 Class

The main entry point is the `Q1` class, which provides all operations for working with the storage.

### Initialization

```python
from q1 import Q1
from q1.crypto import AesGcmCrypto  # Optional for encryption

# Basic initialization
store = Q1("/path/to/storage")

# With encryption
key = b"..." # 32-byte key
encrypted_store = Q1("/path/to/storage", crypto_provider=AesGcmCrypto(key=key))

# Don't create directory if it doesn't exist
store = Q1("/path/to/storage", create=False)
```

#### Parameters:

- `root` (str or Path): Path to the storage root directory
- `crypto_provider` (Optional[CryptoProvider]): Optional encryption provider
- `create` (bool): Whether to create the storage directory if it doesn't exist (default: True)

#### Raises:

- `InvalidRoot`: If the storage root is invalid or inaccessible

### File Operations

#### Putting Files

There are three ways to add files to the store:

```python
# 1. From bytes
file_id = store.put("filename.txt", b"file content")

# 2. From a file-like object
with open("local_file.txt", "rb") as f:
    file_id = store.put("filename.txt", f)

# 3. From a file path
from pathlib import Path
file_id = store.put("filename.txt", Path("/path/to/local_file.txt"))

# With metadata
metadata = {"key": "value", "tags": ["tag1", "tag2"]}
file_id = store.put("filename.txt", b"content", metadata=metadata)
```

##### Method Signature:

```python
def put(
    self,
    name: str,
    data: Union[bytes, BinaryIO, Path],
    *,
    metadata: Optional[Any] = None,
) -> str:
    """Store data in the storage."""
```

##### Returns:
- String file ID (UUID) that can be used to retrieve the file later

##### Raises:
- `FileExists`: If the file with the same content already exists (returns existing ID)
- `Q1Error`: For various other errors

#### Getting Files

Files can be retrieved in multiple ways:

```python
# 1. As bytes
content = store.get(file_id)

# 2. Writing to a file path
output_path = Path("/path/to/output.txt")
store.get(file_id, output=output_path)

# 3. Writing to a file-like object
with open("output.txt", "wb") as f:
    bytes_written = store.get(file_id, output=f)
```

##### Method Signature:

```python
def get(
    self, 
    file_id: str, 
    *, 
    output: Optional[Union[Path, BinaryIO]] = None
) -> Union[bytes, Path, int]:
    """Retrieve file data."""
```

##### Returns:
- Bytes content when no output is specified
- Path object when output is a Path
- Integer bytes written when output is a file-like object

##### Raises:
- `FileMissing`: If the file doesn't exist
- `IntegrityError`: If the file fails integrity verification
- `Q1Error`: For various other errors

#### Streaming Files

For large files, streaming is more efficient than loading the entire file into memory:

```python
# Stream a file in chunks
for chunk in store.stream(file_id):
    process_chunk(chunk)

# Specify custom chunk size (default is 65536 bytes)
for chunk in store.stream(file_id, chunk_size=1024*1024):  # 1MB chunks
    process_chunk(chunk)
```

##### Method Signature:

```python
def stream(
    self, 
    file_id: str, 
    chunk_size: int = 65536
) -> Iterator[bytes]:
    """Stream file data in chunks."""
```

##### Yields:
- Chunks of bytes from the file

##### Raises:
- `FileMissing`: If the file doesn't exist
- `IntegrityError`: If the file fails integrity verification
- `Q1Error`: For various other errors

### Information and Listing

#### Getting File Information

```python
# Get info about a file
info = store.info(file_id)

# With integrity verification
info = store.info(file_id, verify=True)

# Access file attributes
print(f"File: {info.name}, Size: {info.formatted_size}, Created: {info.created_date}")
print(f"Hash: {info.sha256_hex}")
print(f"Is encrypted: {info.is_encrypted}")
print(f"Is deleted: {info.is_deleted}")

# Access metadata
if "tags" in info.meta:
    print(f"Tags: {', '.join(info.meta['tags'])}")
```

##### Method Signature:

```python
def info(
    self, 
    file_id: str, 
    verify: bool = False
) -> FileInfo:
    """Get information about a file."""
```

##### Returns:
- A `FileInfo` object containing file metadata

##### Raises:
- `FileMissing`: If the file doesn't exist
- `IntegrityError`: If verify=True and the file fails verification

#### Listing Files

```python
# List all files
for file_info in store.list():
    print(f"{file_info.id}: {file_info.name}")

# Filtering by name pattern
for file_info in store.list(name_like="document"):
    print(f"{file_info.id}: {file_info.name}")

# Filtering by extension
for file_info in store.list(extension="pdf"):
    print(f"{file_info.id}: {file_info.name}")

# Including deleted files
for file_info in store.list(include_deleted=True):
    status = "DELETED" if file_info.is_deleted else "ACTIVE"
    print(f"{status}: {file_info.name}")

# Pagination
page1 = list(store.list(limit=10))
page2 = list(store.list(limit=10, offset=10))
```

##### Method Signature:

```python
def list(
    self,
    *,
    name_like: Optional[str] = None,
    extension: Optional[str] = None,
    include_deleted: bool = False,
    limit: Optional[int] = None,
    offset: int = 0,
) -> Iterator[FileInfo]:
    """List files in the storage."""
```

##### Yields:
- `FileInfo` objects for each file that matches the filters

### Deletion and Recovery

#### Deleting Files

```python
# Soft delete (can be recovered)
store.delete(file_id)

# Hard delete (permanent)
store.delete(file_id, hard=True)
```

##### Method Signature:

```python
def delete(
    self, 
    file_id: str, 
    *, 
    hard: bool = False
) -> None:
    """Delete a file."""
```

##### Raises:
- `FileMissing`: If the file doesn't exist
- `Q1Error`: For various other errors

#### Undeleting Files

```python
# Recover a soft-deleted file
store.undelete(file_id)
```

##### Method Signature:

```python
def undelete(
    self, 
    file_id: str
) -> None:
    """Undelete a soft-deleted file."""
```

##### Raises:
- `FileMissing`: If the file doesn't exist
- `Q1Error`: If the file is not soft-deleted or another error occurs

### Maintenance Operations

#### Storage Statistics

```python
# Get storage statistics
stats = store.stats()

print(f"Total files: {stats.total_files}")
print(f"Total size: {stats.formatted_total_size}")
print(f"Deleted files: {stats.deleted_files}")
print(f"Deleted size: {stats.formatted_deleted_size}")
print(f"Encrypted files: {stats.encrypted_files}")

# File extensions breakdown
for ext, count in stats.extensions.items():
    print(f"{ext}: {count} files")
```

##### Method Signature:

```python
def stats(self) -> Stats:
    """Get statistics about the storage."""
```

##### Returns:
- A `Stats` object containing storage statistics

#### Integrity Check

```python
# Check integrity of all files
issues = store.integrity_check()
if issues:
    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"- {issue}")
else:
    print("No integrity issues found")

# Auto-repair integrity issues (marks corrupted files as deleted)
issues = store.integrity_check(repair=True)
```

##### Method Signature:

```python
def integrity_check(
    self, 
    repair: bool = False
) -> List[str]:
    """Check the integrity of all files."""
```

##### Returns:
- A list of strings describing any issues found

#### Vacuuming

```python
# Clean up temporary files and optimize the database
store.vacuum()
```

##### Method Signature:

```python
def vacuum(self) -> None:
    """Vacuum the database and clean up temporary files."""
```

### Transaction Control

#### Manual Transaction Control

```python
# Manually commit changes
store.commit()

# Manually roll back changes
store.rollback()
```

##### Method Signatures:

```python
def commit(self) -> None:
    """Commit pending changes to the database."""

def rollback(self) -> None:
    """Roll back pending changes."""
```

### Context Manager Support

The Q1 class supports the context manager protocol for automatic resource management:

```python
with Q1("/path/to/storage") as store:
    # Operations within this block will be automatically committed
    file_id = store.put("example.txt", b"Hello, world!")
    content = store.get(file_id)
    
    # If an exception occurs, changes will be rolled back
    # The store will be automatically closed when exiting the block
```

If an exception occurs within the block, the changes will be rolled back. Otherwise, they will be committed automatically.

## Data Models

### FileInfo

`FileInfo` is a frozen dataclass that contains information about a file in the storage.

```python
from q1.models import FileInfo

# FileInfo objects are returned by store.info() and store.list()
file_info = store.info(file_id)

# Accessing attributes
file_info.id           # Unique ID of the file (UUID string)
file_info.name         # Original filename
file_info.size         # Size in bytes
file_info.created_at   # Creation timestamp (milliseconds since epoch)
file_info.extension    # File extension (without the dot), or None
file_info.sha256_hex   # SHA-256 hash as a hex string, or None
file_info.path         # Relative path within the store, or None
file_info.is_encrypted # Whether the file is encrypted
file_info.is_deleted   # Whether the file is deleted
file_info.deleted_at   # Deletion timestamp, or None if not deleted
file_info.meta         # Dictionary of metadata associated with the file

# Formatted properties
file_info.formatted_size  # Human-readable size (e.g., "1.5 MB")
file_info.created_date    # Formatted creation date
file_info.deleted_date    # Formatted deletion date, or None

# Serialization
as_dict = file_info.to_dict()  # Convert to dictionary
as_json = file_info.to_json()  # Convert to JSON string
```

#### Fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique ID of the file (UUID) |
| `name` | `str` | Original filename |
| `size` | `int` | Size of the file in bytes |
| `created_at` | `int` | Creation timestamp in milliseconds since epoch |
| `extension` | `Optional[str]` | File extension (without the dot), or None |
| `sha256_hex` | `Optional[str]` | SHA-256 hash as a hex string, or None |
| `path` | `Optional[str]` | Relative path within the store, or None |
| `is_encrypted` | `bool` | Whether the file is encrypted |
| `is_deleted` | `bool` | Whether the file is deleted |
| `deleted_at` | `Optional[int]` | Deletion timestamp in milliseconds, or None |
| `meta` | `Dict[str, Any]` | Metadata associated with the file |

#### Properties:

| Property | Type | Description |
|----------|------|-------------|
| `formatted_size` | `str` | Human-readable size (e.g., "1.5 MB") |
| `created_date` | `str` | Formatted creation date |
| `deleted_date` | `Optional[str]` | Formatted deletion date, or None |

#### Methods:

| Method | Returns | Description |
|--------|---------|-------------|
| `to_dict()` | `Dict[str, Any]` | Convert to a dictionary |
| `to_json()` | `str` | Convert to a JSON string |

### Stats

`Stats` is a frozen dataclass that contains statistics about the storage.

```python
from q1.models import Stats

# Stats objects are returned by store.stats()
stats = store.stats()

# Accessing attributes
stats.total_files      # Total number of active files
stats.total_size       # Total size of active files in bytes
stats.deleted_files    # Number of deleted files
stats.deleted_size     # Total size of deleted files in bytes
stats.encrypted_files  # Number of encrypted files
stats.encrypted_size   # Total size of encrypted files in bytes
stats.extensions       # Dictionary mapping extensions to counts

# Formatted properties
stats.formatted_total_size     # Human-readable total size
stats.formatted_deleted_size   # Human-readable deleted size
stats.formatted_encrypted_size # Human-readable encrypted size

# Serialization
as_dict = stats.to_dict()  # Convert to dictionary
as_json = stats.to_json()  # Convert to JSON string
```

#### Fields:

| Field | Type | Description |
|-------|------|-------------|
| `total_files` | `int` | Total number of active files |
| `total_size` | `int` | Total size of active files in bytes |
| `deleted_files` | `int` | Number of deleted files |
| `deleted_size` | `int` | Total size of deleted files in bytes |
| `encrypted_files` | `int` | Number of encrypted files |
| `encrypted_size` | `int` | Total size of encrypted files in bytes |
| `extensions` | `Dict[str, int]` | Dictionary mapping extensions to counts |

#### Properties:

| Property | Type | Description |
|----------|------|-------------|
| `formatted_total_size` | `str` | Human-readable total size |
| `formatted_deleted_size` | `str` | Human-readable deleted size |
| `formatted_encrypted_size` | `str` | Human-readable encrypted size |

#### Methods:

| Method | Returns | Description |
|--------|---------|-------------|
| `to_dict()` | `Dict[str, Any]` | Convert to a dictionary |
| `to_json()` | `str` | Convert to a JSON string |

## Crypto Providers

Crypto providers are implementations of the `CryptoProvider` ABC, which defines the interface for encryption and decryption operations.

### CryptoProvider

```python
from q1.crypto import CryptoProvider

class CryptoProvider(ABC):
    @abstractmethod
    def encrypt(self, data: bytes) -> Tuple[bytes, bytes]:
        """Encrypt data."""
        pass
    
    @abstractmethod
    def decrypt(self, data: bytes, iv: bytes) -> bytes:
        """Decrypt data."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the crypto provider."""
        pass
```

### NullCrypto

`NullCrypto` is a pass-through implementation that does not perform any encryption or decryption.

```python
from q1.crypto import NullCrypto

# Create a null crypto provider (no encryption)
crypto = NullCrypto()

# This is equivalent to not specifying a crypto_provider:
store = Q1("/path/to/storage")  # Uses NullCrypto by default
```

### AesGcmCrypto

`AesGcmCrypto` provides AES-256-GCM encryption using the cryptography library.

```python
from q1.crypto import AesGcmCrypto

# Create a crypto provider with a specific key
key = os.urandom(32)  # Generate a random 32-byte key
crypto = AesGcmCrypto(key=key)

# Use the crypto provider with Q1
store = Q1("/path/to/storage", crypto_provider=crypto)
```

#### Parameters:

- `key` (Optional[bytes]): 32-byte encryption key. If not provided, one will be generated.
- `aad` (bytes): Associated authenticated data for GCM. Default: b'q1-aes-gcm'

#### Raises:

- `EncryptionError`: If the key is not 32 bytes or if the cryptography library is not available.

## Error Handling

The Q1 library provides a hierarchy of exception classes for different error conditions:

```
Q1Error
├── InvalidRoot
├── FileMissing
├── FileExists
├── IntegrityError
├── EncryptionError
├── ConcurrencyError
└── PathSecurityError
```

Example of error handling:

```python
from q1 import Q1
from q1.errors import FileMissing, IntegrityError, Q1Error

try:
    store = Q1("/path/to/storage")
    content = store.get("non-existent-id")
except FileMissing:
    print("The specified file does not exist")
except IntegrityError:
    print("The file failed integrity verification")
except Q1Error as e:
    print(f"An error occurred: {e}")
```

### Exception Descriptions:

| Exception | Description |
|-----------|-------------|
| `Q1Error` | Base exception for all Q1 storage library errors |
| `InvalidRoot` | Raised when the storage root is invalid or inaccessible |
| `FileMissing` | Raised when attempting to access a file that does not exist |
| `FileExists` | Raised when attempting to create a file that already exists (with same content hash) |
| `IntegrityError` | Raised when a file fails integrity verification |
| `EncryptionError` | Raised when encryption or decryption operations fail |
| `ConcurrencyError` | Raised when concurrent access conflicts occur |
| `PathSecurityError` | Raised when a path traversal or other security violation is detected |

## Advanced Usage

### Working with Metadata

Metadata can be any JSON-serializable object attached to a file.

```python
# Storing a file with metadata
metadata = {
    "creator": "John Doe",
    "tags": ["document", "important", "draft"],
    "version": 1.2,
    "properties": {
        "pageCount": 5,
        "wordCount": 1200
    }
}
file_id = store.put("document.pdf", pdf_content, metadata=metadata)

# Retrieving and using metadata
info = store.info(file_id)
if "tags" in info.meta:
    tags = info.meta["tags"]
    if "important" in tags:
        mark_as_important(file_id)

if "properties" in info.meta and "pageCount" in info.meta["properties"]:
    page_count = info.meta["properties"]["pageCount"]
    print(f"Document has {page_count} pages")
```

### File Deduplication

Q1 automatically deduplicates files with identical content.

```python
# Store a file
content = b"This is a test file."
file_id1 = store.put("file1.txt", content)

# Store another file with the same content
file_id2 = store.put("file2.txt", content)

# Both operations return the same ID
assert file_id1 == file_id2

# But the filenames are preserved
info1 = store.info(file_id1)
info2 = store.info(file_id2)
assert info1.name == "file1.txt"  # The first name is preserved
```

### Streaming Large Files

For large files, use streaming to avoid loading the entire file into memory.

```python
# Storing a large file
with open("large_file.bin", "rb") as f:
    file_id = store.put("large_file.bin", f)

# Processing a large file in chunks
total_size = 0
for chunk in store.stream(file_id):
    total_size += len(chunk)
    # Process each chunk without loading the whole file
```

### Customizing the Storage Layout

Q1 uses a sharded storage layout by default, with files stored in a directory structure based on their ID. The file storage path looks like:

```
<root>/<first_2_chars_of_id>/<next_2_chars_of_id>/<full_id>.blob
```

This layout is internal and not normally exposed to users, but understanding it can be helpful for diagnostics or manual recovery if needed.

### Concurrency Control

Q1 handles concurrency using SQLite's WAL mode and file locks. For situations where you need explicit concurrency control, you can use the `exclusive` method:

```python
# Acquire an exclusive lock for a critical operation
with store.exclusive():
    # Operations here are guaranteed to be exclusive
    # Other processes/threads will wait until this block completes
    file_id = store.put("important.txt", content)
    # ...other operations that need to be atomic
```

This ensures that no other threads or processes can perform operations on the same store while the block is executing.
