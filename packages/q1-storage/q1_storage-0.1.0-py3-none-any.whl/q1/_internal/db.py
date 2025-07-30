"""
Internal SQLite database layer for Q1 storage.
"""
from __future__ import annotations

import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union, cast

from q1.errors import Q1Error


class Database:
    """SQLite database wrapper for Q1 storage."""

    def __init__(self, root_dir: Path) -> None:
        """Initialize the database connection.
        
        Args:
            root_dir: Path to the storage root directory
        """
        self.root_dir = root_dir
        self.db_path = root_dir / "q1.db"
        self._conn: Optional[sqlite3.Connection] = None
        
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the database connection and schema."""
        # Ensure the directory exists
        self.root_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to the database
        self._conn = self._create_connection()
        
        # Apply schema if needed
        self._ensure_schema()
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a SQLite connection with appropriate settings.
        
        Returns:
            A configured SQLite connection
        """
        conn = sqlite3.connect(
            self.db_path,
            isolation_level=None,  # We'll manage transactions manually
            check_same_thread=False,  # Allow multi-threading
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        
        # Configure connection
        conn.execute("PRAGMA foreign_keys = ON;")
        
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode = WAL;")
        
        # Other optimizations
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA temp_store = MEMORY;")
        
        # Register adapter to handle UUID, datetime, etc.
        sqlite3.register_adapter(bytes, lambda b: b)
        sqlite3.register_converter("BLOB", lambda b: b)
        
        return conn
    
    def _ensure_schema(self) -> None:
        """Initialize or migrate the database schema."""
        if self._conn is None:
            raise Q1Error("Database connection is not initialized")
        
        # Check the current version
        cursor = self._conn.execute("PRAGMA user_version;")
        version = cursor.fetchone()[0]
        
        # If version is 0, apply the schema
        if version == 0:
            # Load the schema SQL
            schema_path = Path(__file__).parent / "schema.sql"
            with open(schema_path, "r") as f:
                schema_sql = f.read()
            
            # Apply the schema directly, it contains its own transaction
            self._conn.executescript(schema_sql)
        
        # Future migrations would be handled here based on version number
    
    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Create a transaction context.
        
        Yields:
            The SQLite connection for the transaction
        
        Raises:
            Q1Error: If the database connection is not initialized
        """
        if self._conn is None:
            raise Q1Error("Database connection is not initialized")
        
        # Check if a transaction is already active
        in_transaction = self._conn.in_transaction
        
        if not in_transaction:
            self._conn.execute("BEGIN IMMEDIATE;")
        
        try:
            yield self._conn
            
            # Only commit if we started the transaction
            if not in_transaction:
                self._conn.execute("COMMIT;")
        except Exception as e:
            # Only rollback if we started the transaction
            if not in_transaction:
                try:
                    self._conn.execute("ROLLBACK;")
                except sqlite3.OperationalError:
                    # Already rolled back or no transaction active
                    pass
            raise Q1Error(f"Database transaction error: {e}") from e
    
    def execute(
        self, query: str, params: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> sqlite3.Cursor:
        """Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            SQLite cursor with the results
            
        Raises:
            Q1Error: If the database connection is not initialized
        """
        if self._conn is None:
            raise Q1Error("Database connection is not initialized")
        
        try:
            if params is None:
                return self._conn.execute(query)
            return self._conn.execute(query, params)
        except sqlite3.Error as e:
            raise Q1Error(f"Database query error: {e}") from e
    
    def executemany(
        self, query: str, params_seq: List[Union[Tuple[Any, ...], Dict[str, Any]]]
    ) -> sqlite3.Cursor:
        """Execute a SQL query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_seq: Sequence of parameter sets
            
        Returns:
            SQLite cursor with the results
            
        Raises:
            Q1Error: If the database connection is not initialized
        """
        if self._conn is None:
            raise Q1Error("Database connection is not initialized")
        
        try:
            return self._conn.executemany(query, params_seq)
        except sqlite3.Error as e:
            raise Q1Error(f"Database query error: {e}") from e
    
    def query(
        self, query: str, params: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a query and return results as a list of dictionaries.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries with the results
            
        Raises:
            Q1Error: If the database connection is not initialized
        """
        cursor = self.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def query_one(
        self, query: str, params: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute a query and return a single result as a dictionary.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Dictionary with the result or None if no result
            
        Raises:
            Q1Error: If the database connection is not initialized
        """
        results = self.query(query, params)
        return results[0] if results else None
    
    def get_file_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by ID.
        
        Args:
            file_id: The file ID to look up
            
        Returns:
            File metadata as a dictionary or None if not found
        """
        return self.query_one("SELECT * FROM files WHERE id = ?", (file_id,))
    
    def get_file_by_hash(self, sha256: bytes) -> Optional[Dict[str, Any]]:
        """Get file metadata by SHA-256 hash.
        
        Args:
            sha256: The SHA-256 hash to look up
            
        Returns:
            File metadata as a dictionary or None if not found
        """
        return self.query_one("SELECT * FROM files WHERE sha256 = ? AND deleted = 0", (sha256,))
    
    def add_file(
        self,
        file_id: str,
        name: str,
        ext: Optional[str],
        size: int,
        sha256: bytes,
        iv: Optional[bytes],
        path: str,
        meta_json: Optional[str] = None,
    ) -> None:
        """Add a file record to the database.
        
        Args:
            file_id: The UUID of the file
            name: Original filename
            ext: File extension (no dot)
            size: File size in bytes
            sha256: SHA-256 hash of the file
            iv: Initialization vector for encryption (or None)
            path: Relative path within the store
            meta_json: Optional JSON metadata
        """
        created_at = int(time.time() * 1000)  # ms since epoch
        
        with self.transaction() as conn:
            conn.execute(
                """
                INSERT INTO files (
                    id, name, ext, size, sha256, iv, created_at, meta_json, path, deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (file_id, name, ext, size, sha256, iv, created_at, meta_json, path),
            )
    
    def update_file(
        self,
        file_id: str,
        name: Optional[str] = None,
        meta_json: Optional[str] = None,
    ) -> None:
        """Update mutable file metadata.
        
        Args:
            file_id: The UUID of the file
            name: New filename (optional)
            meta_json: New JSON metadata (optional)
        
        Raises:
            Q1Error: If the file doesn't exist
        """
        updates = []
        params: List[Any] = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if meta_json is not None:
            updates.append("meta_json = ?")
            params.append(meta_json)
        
        if not updates:
            return  # Nothing to update
        
        params.append(file_id)
        
        with self.transaction() as conn:
            result = conn.execute(
                f"UPDATE files SET {', '.join(updates)} WHERE id = ?",
                params,
            )
            
            if result.rowcount == 0:
                raise Q1Error(f"File not found: {file_id}")
    
    def soft_delete(self, file_id: str) -> None:
        """Mark a file as deleted.
        
        Args:
            file_id: The UUID of the file to delete
        
        Raises:
            Q1Error: If the file doesn't exist or is already deleted
        """
        deleted_at = int(time.time() * 1000)  # ms since epoch
        
        with self.transaction() as conn:
            result = conn.execute(
                "UPDATE files SET deleted = 1, deleted_at = ? WHERE id = ? AND deleted = 0",
                (deleted_at, file_id),
            )
            
            if result.rowcount == 0:
                # Check if file exists but is already deleted
                existing = self.get_file_by_id(file_id)
                if existing is None:
                    raise Q1Error(f"File not found: {file_id}")
                if existing["deleted"] == 1:
                    raise Q1Error(f"File already deleted: {file_id}")
    
    def undelete(self, file_id: str) -> None:
        """Restore a soft-deleted file.
        
        Args:
            file_id: The UUID of the file to restore
        
        Raises:
            Q1Error: If the file doesn't exist or is not deleted
        """
        with self.transaction() as conn:
            result = conn.execute(
                "UPDATE files SET deleted = 0, deleted_at = NULL WHERE id = ? AND deleted = 1",
                (file_id,),
            )
            
            if result.rowcount == 0:
                # Check if file exists but is not deleted
                existing = self.get_file_by_id(file_id)
                if existing is None:
                    raise Q1Error(f"File not found: {file_id}")
                if existing["deleted"] == 0:
                    raise Q1Error(f"File is not deleted: {file_id}")
    
    def hard_delete(self, file_id: str) -> None:
        """Permanently delete a file record.
        
        Args:
            file_id: The UUID of the file to delete
        
        Raises:
            Q1Error: If the file doesn't exist
        """
        with self.transaction() as conn:
            result = conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
            
            if result.rowcount == 0:
                raise Q1Error(f"File not found: {file_id}")
    
    def list_files(
        self,
        name_like: Optional[str] = None,
        extension: Optional[str] = None,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List files with optional filters.
        
        Args:
            name_like: Optional pattern for name filtering (SQL LIKE pattern)
            extension: Optional extension filter
            include_deleted: Whether to include soft-deleted files
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of file metadata dictionaries
        """
        query = "SELECT * FROM files WHERE 1=1"
        params: List[Any] = []
        
        # Apply filters
        if not include_deleted:
            query += " AND deleted = 0"
        
        if name_like is not None:
            query += " AND name LIKE ?"
            params.append(f"%{name_like}%")
        
        if extension is not None:
            query += " AND ext = ?"
            params.append(extension)
        
        # Add ordering and pagination
        query += " ORDER BY created_at DESC"
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        
        if offset > 0:
            query += " OFFSET ?"
            params.append(offset)
        
        return self.query(query, tuple(params))
    
    def vacuum(self) -> None:
        """Run VACUUM to rebuild the database file.
        
        This reclaims space and defragments the database.
        """
        if self._conn is None:
            raise Q1Error("Database connection is not initialized")
        
        self._conn.execute("VACUUM;")
    
    def integrity_check(self) -> bool:
        """Run integrity check on the database.
        
        Returns:
            True if the database passed the integrity check
        """
        if self._conn is None:
            raise Q1Error("Database connection is not initialized")
        
        result = self._conn.execute("PRAGMA integrity_check;").fetchone()
        return result is not None and result[0] == "ok"
    
    def commit(self) -> None:
        """Commit any pending transaction."""
        if self._conn is None:
            raise Q1Error("Database connection is not initialized")
        
        self._conn.commit()
    
    def rollback(self) -> None:
        """Roll back any pending transaction."""
        if self._conn is None:
            raise Q1Error("Database connection is not initialized")
        
        self._conn.rollback()
    
    def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
