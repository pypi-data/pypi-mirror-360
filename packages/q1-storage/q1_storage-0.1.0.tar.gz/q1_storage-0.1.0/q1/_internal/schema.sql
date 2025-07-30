-- q1 storage schema (v1)

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- User version to track schema migrations
PRAGMA user_version = 1;

-- Main files table with metadata
CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,            -- uuid4
    name TEXT NOT NULL,            -- original filename
    ext TEXT,                      -- file extension (no dot)
    size INTEGER NOT NULL,         -- size in bytes
    sha256 BLOB NOT NULL,          -- 32-byte SHA256 hash
    iv BLOB,                       -- 12-byte IV for AES-GCM (NULL if not encrypted)
    created_at INTEGER NOT NULL,   -- timestamp in ms (epoch)
    meta_json TEXT,                -- optional JSON metadata
    path TEXT NOT NULL UNIQUE,     -- relative path within the store
    deleted INTEGER DEFAULT 0 NOT NULL,  -- 0=active, 1=deleted
    deleted_at INTEGER             -- timestamp when deleted (NULL if active)
);

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_files_name ON files(name) WHERE deleted = 0;
CREATE INDEX IF NOT EXISTS idx_files_ext ON files(ext) WHERE deleted = 0;
CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256);
CREATE INDEX IF NOT EXISTS idx_files_created_at ON files(created_at);
CREATE INDEX IF NOT EXISTS idx_files_deleted ON files(deleted, deleted_at);

-- Create a view for active files
CREATE VIEW IF NOT EXISTS active_files AS
SELECT * FROM files WHERE deleted = 0;
