# Changelog

All notable changes to the Q1 Storage Library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Core storage functionality
- SQLite database backend
- File operations: put, get, stream, info, list, delete
- Optional AES-256-GCM encryption
- Integrity checking with SHA-256
- Transactional operations with commit/rollback
- Path containment security

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- Implemented path validation to prevent directory traversal
- File permissions set to 0o600, directories to 0o700
