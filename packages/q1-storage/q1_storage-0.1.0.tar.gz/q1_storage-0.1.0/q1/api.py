"""
Main API for the Q1 storage library.
"""
from __future__ import annotations

import io
import json
import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import (
    Any,
    BinaryIO,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
    cast,
    overload,
)
from uuid import UUID

from q1._internal.db import Database
from q1._internal.fs import (
    check_path_safety,
    ensure_directory,
    file_lock,
    get_shard_path,
    get_temp_dir,
    get_trash_dir,
    list_files,
    move_file,
    secure_delete,
    store_file,
)
from q1._internal.utils import (
    calculate_sha256,
    chunk_iterator,
    generate_uuid,
    get_extension,
    parse_metadata,
    timestamp_ms,
    verify_sha256,
)
from q1.crypto import CryptoProvider, NullCrypto
from q1.errors import (
    ConcurrencyError,
    FileExists,
    FileMissing,
    IntegrityError,
    InvalidRoot,
    Q1Error,
)
from q1.models import FileInfo, Stats


class Q1:
    """Main Q1 storage class.
    
    Provides a simple interface for storing and retrieving files with
    optional encryption, integrity verification, and other features.
    """
    
    def __init__(
        self,
        root: Union[str, Path],
        *,
        crypto_provider: Optional[CryptoProvider] = None,
        create: bool = True,
    ) -> None:
        """Initialize the storage.
        
        Args:
            root: Path to the storage root directory
            crypto_provider: Optional crypto provider for encryption
            create: Whether to create the storage directory if it doesn't exist
            
        Raises:
            InvalidRoot: If the storage root is invalid
        """
        self.root = Path(root).resolve()
        
        if not self.root.exists():
            if create:
                ensure_directory(self.root)
            else:
                raise InvalidRoot(str(self.root), "Directory does not exist")
        elif not self.root.is_dir():
            raise InvalidRoot(str(self.root), "Path exists but is not a directory")
        
        # Set up database
        self.db = Database(self.root)
        
        # Set up crypto provider
        self.crypto = crypto_provider or NullCrypto()
        
        # Lock file for concurrent access
        self._lock_file = self.root / ".lock"
        
        # Set up directories
        ensure_directory(get_temp_dir(self.root))
        ensure_directory(get_trash_dir(self.root))
    
    def __enter__(self) -> Q1:
        """Enter context manager.
        
        Returns:
            Self
        """
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager.
        
        If an exception occurred, roll back any uncommitted changes.
        Otherwise, commit and close.
        """
        try:
            if exc_type:
                self.rollback()
            else:
                self.commit()
        finally:
            self.close()
    
    def _resolve_path(
        self, path: Union[str, Path], *, check_safety: bool = True
    ) -> Path:
        """Resolve a path relative to the storage root.
        
        Args:
            path: A path relative to the storage root
            check_safety: Whether to check that the path is within the root
            
        Returns:
            The resolved path
            
        Raises:
            Q1Error: If the path is outside the storage root
        """
        path_obj = self.root / Path(path)
        if check_safety:
            return check_path_safety(self.root, path_obj)
        return path_obj
    
    def _get_file_path(self, file_id: str) -> Path:
        """Get the storage path for a file.
        
        Args:
            file_id: The ID of the file
            
        Returns:
            The path to the file
            
        Raises:
            FileMissing: If the file doesn't exist
        """
        # Get path from database
        file_record = self.db.get_file_by_id(file_id)
        if not file_record:
            raise FileMissing(file_id)
        
        rel_path = file_record["path"]
        return self._resolve_path(rel_path)
    
    @overload
    def put(
        self, name: str, data: bytes, *, metadata: Optional[Any] = None
    ) -> str: ...
    
    @overload
    def put(
        self,
        name: str,
        data: BinaryIO,
        *,
        metadata: Optional[Any] = None,
        size: Optional[int] = None,
    ) -> str: ...
    
    @overload
    def put(
        self,
        name: str,
        data: Path,
        *,
        metadata: Optional[Any] = None,
    ) -> str: ...
    
    def put(
        self,
        name: str,
        data: Union[bytes, BinaryIO, Path],
        *,
        metadata: Optional[Any] = None,
        size: Optional[int] = None,
    ) -> str:
        """Store data in the storage.
        
        Args:
            name: The name to store the file under
            data: The data to store, as bytes, a file-like object, or a Path
            metadata: Optional metadata to store with the file
            size: Size hint for file-like objects
            
        Returns:
            The ID of the stored file
            
        Raises:
            FileExists: If a file with the same content has already been stored
            Q1Error: For other errors
        """
        # Generate a UUID for the file
        file_id = generate_uuid()
        
        # Get a temporary storage location
        temp_dir = get_temp_dir(self.root)
        temp_file = temp_dir / f"{file_id}.tmp"
        
        # Flag used for a potential name in error
        error_name = name
        
        try:
            # Write the data to the temporary file
            if isinstance(data, bytes):
                # Bytes input
                with open(temp_file, "wb") as f:
                    f.write(data)
                actual_size = len(data)
            
            elif isinstance(data, Path):
                # Path input
                if not data.exists():
                    raise Q1Error(f"Input file not found: {data}")
                
                # Use the filename as the error name
                error_name = data.name
                
                # Copy the file to the temporary location
                shutil.copy2(data, temp_file)
                actual_size = data.stat().st_size
            
            else:
                # File-like object
                with open(temp_file, "wb") as f:
                    # Copy in chunks to handle large files
                    chunk = data.read(65536)
                    while chunk:
                        f.write(chunk)
                        chunk = data.read(65536)
                
                # Get the size of the temporary file
                actual_size = temp_file.stat().st_size
            
            # Get the file extension
            extension = get_extension(name)
            
            # Calculate the SHA-256 hash for integrity and deduplication
            file_hash = calculate_sha256(temp_file)
            
            # Check for existing file with same hash (deduplication)
            existing = self.db.get_file_by_hash(file_hash)
            if existing and "id" in existing:
                # Return the ID of the existing file
                file_id_str = cast(str, existing["id"])
                return file_id_str
            
            # Apply encryption if needed
            is_encrypted = False
            iv = None
            
            if not isinstance(self.crypto, NullCrypto):
                # Read the file
                with open(temp_file, "rb") as f:
                    plaintext = f.read()
                
                # Encrypt the data
                ciphertext, iv = self.crypto.encrypt(plaintext)
                is_encrypted = True
                
                # Write the encrypted data back to the temp file
                with open(temp_file, "wb") as f:
                    f.write(ciphertext)
                
                # Recalculate the hash after encryption
                file_hash = calculate_sha256(temp_file)
            
            # Create the sharded storage path
            uuid_obj = UUID(file_id)
            shard_path = get_shard_path(self.root, uuid_obj)
            rel_path = f"{shard_path.relative_to(self.root)}/{file_id}.blob"
            
            # Parse metadata as JSON if needed
            meta_json: Optional[str] = None
            if metadata is not None:
                meta_json = parse_metadata(metadata)
            
            # Start with temporary record
            with self.db.transaction():
                # Add the file record to the database
                self.db.add_file(
                    file_id=file_id,
                    name=name,
                    ext=extension,
                    size=actual_size,
                    sha256=file_hash,
                    iv=iv,
                    path=str(rel_path),
                    meta_json=meta_json,
                )
                
                # Move the temporary file to its final location
                dest_path = self.root / rel_path
                move_file(
                    temp_file,
                    dest_path.parent,
                    dest_path.name,
                    overwrite=False,
                    mode=0o600,
                )
            
            return file_id
        
        except Exception as e:
            # Clean up the temporary file
            if temp_file.exists():
                secure_delete(temp_file)
            
            # Rethrow as appropriate Q1 error
            if isinstance(e, (Q1Error, FileExists)):
                raise
            
            raise Q1Error(f"Error storing file '{error_name}': {e}") from e
    
    @overload
    def get(self, file_id: str) -> bytes: ...
    
    @overload
    def get(self, file_id: str, *, output: Path) -> Path: ...
    
    @overload
    def get(self, file_id: str, *, output: BinaryIO) -> int: ...
    
    def get(
        self, file_id: str, *, output: Optional[Union[Path, BinaryIO]] = None
    ) -> Union[bytes, Path, int]:
        """Retrieve file data.
        
        Args:
            file_id: The ID of the file to retrieve
            output: Optional output path or file-like object
            
        Returns:
            The file data as bytes, the output Path, or the number of bytes written
            
        Raises:
            FileMissing: If the file doesn't exist
            IntegrityError: If the file fails integrity verification
            Q1Error: For other errors
        """
        # Get file record
        file_record = self.db.get_file_by_id(file_id)
        if not file_record:
            raise FileMissing(file_id)
        
        # Get file path
        file_path = self._resolve_path(file_record["path"])
        if not file_path.exists():
            raise Q1Error(f"File data missing for {file_id}")
        
        try:
            # Verify file integrity
            verify_sha256(file_path, file_record["sha256"])
            
            # If the file is encrypted, decrypt it
            iv = file_record["iv"]
            if iv:  # If IV is present, the file is encrypted
                # Read the encrypted data
                with open(file_path, "rb") as f:
                    encrypted_data = f.read()
                
                # Decrypt the data
                decrypted_data = self.crypto.decrypt(encrypted_data, iv)
                
                # Return or write the decrypted data
                if output is None:
                    # Return as bytes
                    return decrypted_data
                elif isinstance(output, Path):
                    # Write to a file path
                    with open(output, "wb") as f:
                        f.write(decrypted_data)
                    return output
                else:
                    # Write to a file-like object
                    bytes_written = output.write(decrypted_data)
                    return bytes_written
            else:
                # File is not encrypted
                if output is None:
                    # Return as bytes
                    with open(file_path, "rb") as f:
                        return f.read()
                elif isinstance(output, Path):
                    # Copy to a file path
                    shutil.copy2(file_path, output)
                    return output
                else:
                    # Copy to a file-like object
                    bytes_written = 0
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(65536), b""):
                            bytes_written += output.write(chunk)
                    return bytes_written
        
        except Exception as e:
            if isinstance(e, (FileMissing, IntegrityError)):
                raise
            
            raise Q1Error(f"Error retrieving file {file_id}: {e}") from e
    
    def stream(self, file_id: str, chunk_size: int = 65536) -> Iterator[bytes]:
        """Stream file data in chunks.
        
        Args:
            file_id: The ID of the file to stream
            chunk_size: Size of each chunk in bytes
            
        Yields:
            Chunks of the file data
            
        Raises:
            FileMissing: If the file doesn't exist
            IntegrityError: If the file fails integrity verification
            Q1Error: For other errors
        """
        # Get file record
        file_record = self.db.get_file_by_id(file_id)
        if not file_record:
            raise FileMissing(file_id)
        
        # Get file path
        file_path = self._resolve_path(file_record["path"])
        if not file_path.exists():
            raise Q1Error(f"File data missing for {file_id}")
        
        try:
            # Verify file integrity
            verify_sha256(file_path, file_record["sha256"])
            
            # If the file is encrypted, we need to decrypt it all at once
            iv = file_record["iv"]
            if iv:  # If IV is present, the file is encrypted
                # Read the encrypted data
                with open(file_path, "rb") as f:
                    encrypted_data = f.read()
                
                # Decrypt the data
                decrypted_data = self.crypto.decrypt(encrypted_data, iv)
                
                # Yield chunks of the decrypted data
                for i in range(0, len(decrypted_data), chunk_size):
                    yield decrypted_data[i:i+chunk_size]
            else:
                # File is not encrypted, stream directly from disk
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(chunk_size), b""):
                        yield chunk
        
        except Exception as e:
            if isinstance(e, (FileMissing, IntegrityError)):
                raise
            
            raise Q1Error(f"Error streaming file {file_id}: {e}") from e
    
    def info(self, file_id: str, verify: bool = False) -> FileInfo:
        """Get information about a file.
        
        Args:
            file_id: The ID of the file to get info for
            verify: Whether to verify the file's integrity
            
        Returns:
            File information
            
        Raises:
            FileMissing: If the file doesn't exist
            IntegrityError: If verify is True and the file fails verification
        """
        # Get file record
        file_record = self.db.get_file_by_id(file_id)
        if not file_record:
            raise FileMissing(file_id)
        
        # Get file path (for verification)
        file_path = self._resolve_path(file_record["path"])
        
        if verify and file_path.exists():
            # Verify file integrity
            verify_sha256(file_path, file_record["sha256"])
        
        # Parse metadata if present
        meta = {}
        if file_record["meta_json"]:
            try:
                meta = dict(json.loads(file_record["meta_json"]))
            except (json.JSONDecodeError, TypeError):
                # Ignore invalid metadata
                pass
        
        # Create a FileInfo object
        return FileInfo(
            id=file_record["id"],
            name=file_record["name"],
            size=file_record["size"],
            created_at=file_record["created_at"],
            extension=file_record["ext"],
            sha256_hex=file_record["sha256"].hex() if file_record["sha256"] else None,
            path=file_record["path"],
            is_encrypted=bool(file_record["iv"]),
            is_deleted=bool(file_record["deleted"]),
            deleted_at=file_record["deleted_at"],
            meta=meta,
        )
    
    def list(
        self,
        *,
        name_like: Optional[str] = None,
        extension: Optional[str] = None,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> Iterator[FileInfo]:
        """List files in the storage.
        
        Args:
            name_like: Optional pattern to filter by name
            extension: Optional extension to filter by
            include_deleted: Whether to include deleted files
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Yields:
            FileInfo objects
        """
        # Get file records from database
        records = self.db.list_files(
            name_like=name_like,
            extension=extension,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
        )
        
        # Convert each record to a FileInfo object
        for record in records:
            # Parse metadata if present
            meta = {}
            if record["meta_json"]:
                try:
                    meta = dict(json.loads(record["meta_json"]))
                except (json.JSONDecodeError, TypeError):
                    # Ignore invalid metadata
                    pass
            
            yield FileInfo(
                id=record["id"],
                name=record["name"],
                size=record["size"],
                created_at=record["created_at"],
                extension=record["ext"],
                sha256_hex=record["sha256"].hex() if record["sha256"] else None,
                path=record["path"],
                is_encrypted=bool(record["iv"]),
                is_deleted=bool(record["deleted"]),
                deleted_at=record["deleted_at"],
                meta=meta,
            )
    
    def delete(self, file_id: str, *, hard: bool = False) -> None:
        """Delete a file.
        
        Args:
            file_id: The ID of the file to delete
            hard: Whether to permanently delete the file
            
        Raises:
            FileMissing: If the file doesn't exist
            Q1Error: For other errors
        """
        # Get file record
        file_record = self.db.get_file_by_id(file_id)
        if not file_record:
            raise FileMissing(file_id)
        
        # Get file path
        file_path = self._resolve_path(file_record["path"])
        
        if hard:
            # Hard delete - remove from database and move to trash
            try:
                # Get the trash directory
                trash_dir = get_trash_dir(self.root)
                trash_file = trash_dir / f"{file_id}.trash"
                
                # When file has been marked as deleted, add a transaction
                with self.db.transaction():
                    # Move the file to trash
                    if file_path.exists():
                        move_file(file_path, trash_dir, trash_file.name, overwrite=True)
                    
                    # Remove the database record
                    self.db.hard_delete(file_id)
                
                # Delete the trash file
                secure_delete(trash_file)
            
            except Exception as e:
                raise Q1Error(f"Error hard-deleting file {file_id}: {e}") from e
        
        else:
            # Soft delete - mark as deleted in database
            try:
                self.db.soft_delete(file_id)
            except Exception as e:
                if isinstance(e, FileMissing):
                    raise
                
                raise Q1Error(f"Error soft-deleting file {file_id}: {e}") from e
    
    def undelete(self, file_id: str) -> None:
        """Undelete a soft-deleted file.
        
        Args:
            file_id: The ID of the file to undelete
            
        Raises:
            FileMissing: If the file doesn't exist
            Q1Error: If the file is not soft-deleted or another error occurs
        """
        try:
            self.db.undelete(file_id)
        except Exception as e:
            if isinstance(e, FileMissing):
                raise
            
            raise Q1Error(f"Error undeleting file {file_id}: {e}") from e
    
    def stats(self) -> Stats:
        """Get statistics about the storage.
        
        Returns:
            Storage statistics
        """
        # Execute stats query
        active_stats = self.db.query("""
            SELECT 
                COUNT(*) as total_files,
                SUM(size) as total_size,
                COUNT(CASE WHEN iv IS NOT NULL THEN 1 END) as encrypted_files,
                SUM(CASE WHEN iv IS NOT NULL THEN size ELSE 0 END) as encrypted_size
            FROM files
            WHERE deleted = 0
        """)[0]
        
        deleted_stats = self.db.query("""
            SELECT 
                COUNT(*) as deleted_files,
                SUM(size) as deleted_size
            FROM files
            WHERE deleted = 1
        """)[0]
        
        # Get extension counts (active files only)
        ext_query = self.db.query("""
            SELECT ext, COUNT(*) as count
            FROM files
            WHERE deleted = 0
            GROUP BY ext
        """)
        
        extensions = {row["ext"] or "none": row["count"] for row in ext_query}
        
        # Create a Stats object
        return Stats(
            total_files=active_stats["total_files"] or 0,
            total_size=active_stats["total_size"] or 0,
            deleted_files=deleted_stats["deleted_files"] or 0,
            deleted_size=deleted_stats["deleted_size"] or 0,
            encrypted_files=active_stats["encrypted_files"] or 0,
            encrypted_size=active_stats["encrypted_size"] or 0,
            extensions=extensions,
        )
    
    @contextmanager
    def exclusive(self) -> Generator[None, None, None]:
        """Acquire an exclusive lock on the storage.
        
        Raises:
            ConcurrencyError: If the lock cannot be acquired
        """
        try:
            with file_lock(self._lock_file):
                yield
        except Exception as e:
            raise ConcurrencyError(f"Failed to acquire exclusive lock: {e}") from e
    
    def integrity_check(self, repair: bool = False) -> List[str]:
        """Check the integrity of all files.
        
        Args:
            repair: Whether to attempt to repair issues
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Check database integrity
        if not self.db.integrity_check():
            issues.append("Database integrity check failed")
            
            # Can't continue if database is corrupted
            return issues
        
        # Get all files
        records = self.db.query("SELECT id, sha256, path FROM files")
        
        for record in records:
            file_id = record["id"]
            file_path = self._resolve_path(record["path"])
            
            if not file_path.exists():
                issue = f"File missing: {file_id} ({file_path.name})"
                issues.append(issue)
                
                # Can't verify a missing file
                continue
            
            try:
                # Verify the hash
                verify_sha256(file_path, record["sha256"])
            except IntegrityError:
                issue = f"Integrity check failed: {file_id} ({file_path.name})"
                issues.append(issue)
                
                # If repair is requested and file is corrupted, mark it deleted
                if repair:
                    try:
                        self.delete(file_id)
                        issues.append(f"Marked corrupted file as deleted: {file_id}")
                    except Exception as e:
                        issues.append(f"Failed to mark file as deleted: {file_id} - {e}")
        
        return issues
    
    def vacuum(self) -> None:
        """Vacuum the database and clean up temporary files."""
        # Vacuum the database
        self.db.vacuum()
        
        # Clean up temporary files older than 1 day
        temp_dir = get_temp_dir(self.root)
        trash_dir = get_trash_dir(self.root)
        
        one_day_ago = timestamp_ms() - (24 * 60 * 60 * 1000)
        
        # Clean up temp dir
        for path in list_files(temp_dir):
            try:
                if path.stat().st_mtime * 1000 < one_day_ago:
                    secure_delete(path)
            except (OSError, IOError):
                # Ignore errors for temp files
                pass
        
        # Clean up trash dir
        for path in list_files(trash_dir):
            try:
                secure_delete(path)
            except (OSError, IOError):
                # Ignore errors for trash files
                pass
    
    def commit(self) -> None:
        """Commit pending changes to the database."""
        self.db.commit()
    
    def rollback(self) -> None:
        """Roll back pending changes."""
        # Roll back database transaction
        self.db.rollback()
        
        # Clean up any files added since last commit
        # This would require keeping track of uncommitted operations,
        # which we're not currently doing in this version.
        # For a complete implementation, we would:
        # 1. Track files added since the last commit
        # 2. Remove those files from disk
        # But the database rollback already removes the records
    
    def close(self) -> None:
        """Close the storage."""
        self.db.close()
