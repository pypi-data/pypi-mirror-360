"""
Data models for Q1 storage.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from q1._internal.utils import format_size, format_timestamp


@dataclass(frozen=True)
class FileInfo:
    """Information about a file in the storage."""
    
    id: str
    """Unique ID of the file (UUID)."""
    
    name: str
    """Original filename."""
    
    size: int
    """Size of the file in bytes."""
    
    created_at: int
    """Creation timestamp in milliseconds since epoch."""
    
    extension: Optional[str] = None
    """File extension (without the dot), or None if no extension."""
    
    sha256_hex: Optional[str] = None
    """SHA-256 hash as a hex string, or None if not calculated."""
    
    path: Optional[str] = None
    """Relative path within the store, or None if not applicable."""
    
    is_encrypted: bool = False
    """Whether the file is encrypted."""
    
    is_deleted: bool = False
    """Whether the file is deleted."""
    
    deleted_at: Optional[int] = None
    """Deletion timestamp in milliseconds since epoch, or None if not deleted."""
    
    meta: Dict[str, Any] = field(default_factory=dict)
    """Metadata associated with the file."""
    
    @property
    def formatted_size(self) -> str:
        """Get a human-readable size.
        
        Returns:
            Human-readable size string
        """
        return format_size(self.size)
    
    @property
    def created_date(self) -> str:
        """Get a formatted creation date.
        
        Returns:
            Formatted creation date
        """
        return format_timestamp(self.created_at)
    
    @property
    def deleted_date(self) -> Optional[str]:
        """Get a formatted deletion date, if applicable.
        
        Returns:
            Formatted deletion date or None if not deleted
        """
        if self.deleted_at is not None:
            return format_timestamp(self.deleted_at)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary representation.
        
        Returns:
            Dictionary representation of the file info
        """
        result = {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "formatted_size": self.formatted_size,
            "created_at": self.created_at,
            "created_date": self.created_date,
            "is_encrypted": self.is_encrypted,
            "is_deleted": self.is_deleted,
        }
        
        if self.extension:
            result["extension"] = self.extension
        
        if self.sha256_hex:
            result["sha256_hex"] = self.sha256_hex
        
        if self.path:
            result["path"] = self.path
            
        if self.deleted_at:
            result["deleted_at"] = self.deleted_at
            result["deleted_date"] = self.deleted_date
        
        if self.meta:
            result["meta"] = self.meta
            
        return result
    
    def to_json(self) -> str:
        """Convert to a JSON representation.
        
        Returns:
            JSON string representation of the file info
        """
        return json.dumps(self.to_dict())


@dataclass(frozen=True)
class Stats:
    """Storage statistics."""
    
    total_files: int
    """Total number of active files in the store."""
    
    total_size: int
    """Total size of all active files in bytes."""
    
    deleted_files: int
    """Number of deleted files in the store."""
    
    deleted_size: int
    """Total size of deleted files in bytes."""
    
    encrypted_files: int
    """Number of encrypted files in the store."""
    
    encrypted_size: int
    """Total size of encrypted files in bytes."""
    
    extensions: Dict[str, int] = field(default_factory=dict)
    """Count of files by extension."""
    
    @property
    def formatted_total_size(self) -> str:
        """Get a human-readable total size.
        
        Returns:
            Human-readable size string
        """
        return format_size(self.total_size)
    
    @property
    def formatted_deleted_size(self) -> str:
        """Get a human-readable deleted size.
        
        Returns:
            Human-readable size string
        """
        return format_size(self.deleted_size)
    
    @property
    def formatted_encrypted_size(self) -> str:
        """Get a human-readable encrypted size.
        
        Returns:
            Human-readable size string
        """
        return format_size(self.encrypted_size)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary representation.
        
        Returns:
            Dictionary representation of the stats
        """
        return {
            "total_files": self.total_files,
            "total_size": self.total_size,
            "formatted_total_size": self.formatted_total_size,
            "deleted_files": self.deleted_files,
            "deleted_size": self.deleted_size,
            "formatted_deleted_size": self.formatted_deleted_size,
            "encrypted_files": self.encrypted_files,
            "encrypted_size": self.encrypted_size,
            "formatted_encrypted_size": self.formatted_encrypted_size,
            "extensions": self.extensions,
        }
    
    def to_json(self) -> str:
        """Convert to a JSON representation.
        
        Returns:
            JSON string representation of the stats
        """
        return json.dumps(self.to_dict())
