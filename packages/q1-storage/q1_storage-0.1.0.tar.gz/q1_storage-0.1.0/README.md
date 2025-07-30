# Q1: Simple Local File Storage

A production-grade, pip-installable Python package that offers simple local file storage backed by SQLite and optional AES-GCM encryption.

## Features

- Store and retrieve files with a simple API
- Transactional operations with ACID guarantees
- Optional at-rest AES-256-GCM encryption
- Integrity verification with SHA-256
- File deduplication
- Soft and hard delete with recovery options
- Concurrency support with SQLite WAL mode

## Installation

```bash
pip install q1
```

For encryption support:
```bash
pip install q1[crypto]
```

## Quick Start

```python
from q1 import Q1

# Create or open a storage location
with Q1("./my_store") as store:
    # Store a file
    file_id = store.put("example.txt", b"Hello, world!")
    
    # Retrieve the file
    content = store.get(file_id)
    
    # Get file information
    info = store.info(file_id)
    print(f"File name: {info.name}, size: {info.size} bytes")
    
    # List all files
    for file_info in store.list():
        print(f"ID: {file_info.id}, Name: {file_info.name}")
    
    # Delete a file (soft delete by default)
    store.delete(file_id)
    
    # Undelete a file
    store.undelete(file_id)
    
    # Permanently delete
    store.delete(file_id, hard=True)
```

## Using Encryption

```python
from q1 import Q1
from q1.crypto import AesGcmCrypto

# Create an encryption provider with a secure key
crypto = AesGcmCrypto(key=b"a" * 32)  # Use a proper secure key in production!

# Open storage with encryption
with Q1("./encrypted_store", crypto_provider=crypto) as store:
    # All operations work the same as before, but data is encrypted at rest
    file_id = store.put("secret.txt", b"Confidential information")
    content = store.get(file_id)  # Automatically decrypted
```

## Development

### Setting up the development environment

```bash
# Clone the repository
git clone https://github.com/yourusername/q1.git
cd q1

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,crypto]"
```

### Running tests

```bash
pytest
```

### Type checking

```bash
mypy --strict q1
```

### Building the package

```bash
flit build
```

## Continuous Integration

This project uses GitHub Actions for continuous integration, running tests on:
- Python 3.9, 3.10, 3.11, and 3.12
- Windows, macOS, and Linux

The CI pipeline performs:
1. Test execution with coverage reporting
2. Type checking with mypy
3. Package building
4. Optional PyPI deployment for tagged releases

## License

MIT License - See LICENSE file for details.
