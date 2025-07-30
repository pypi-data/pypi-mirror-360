#!/usr/bin/env python
"""
Command-line interface for the Q1 storage library.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from q1 import Q1, FileInfo
from q1.crypto import AesGcmCrypto, CryptoProvider, NullCrypto
from q1.errors import FileMissing, Q1Error


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Q1 Storage - Simple local file storage with SQLite and encryption",
    )
    parser.add_argument(
        "--root",
        "-r",
        type=str,
        required=True,
        help="Path to the storage root directory",
    )
    parser.add_argument(
        "--encrypt",
        "-e",
        action="store_true",
        help="Enable AES-256-GCM encryption (requires cryptography package)",
    )
    parser.add_argument(
        "--key-file",
        "-k",
        type=str,
        help="Path to file containing encryption key (32 bytes)",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new storage")
    
    # Put command
    put_parser = subparsers.add_parser("put", help="Store a file")
    put_parser.add_argument("file", type=str, help="Path to the file to store")
    put_parser.add_argument(
        "--name",
        "-n",
        type=str,
        help="Name to store the file under (default: original filename)",
    )
    put_parser.add_argument(
        "--meta",
        "-m",
        type=str,
        help="JSON metadata to store with the file",
    )
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Retrieve a file")
    get_parser.add_argument("id", type=str, help="ID of the file to retrieve")
    get_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Path to write the file to (default: print to stdout)",
    )
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get file information")
    info_parser.add_argument("id", type=str, help="ID of the file to get info for")
    info_parser.add_argument(
        "--verify",
        "-v",
        action="store_true",
        help="Verify file integrity",
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List files")
    list_parser.add_argument(
        "--name",
        "-n",
        type=str,
        help="Filter by name pattern",
    )
    list_parser.add_argument(
        "--extension",
        "-x",
        type=str,
        help="Filter by extension",
    )
    list_parser.add_argument(
        "--deleted",
        "-d",
        action="store_true",
        help="Include deleted files",
    )
    list_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        help="Maximum number of results to return",
    )
    list_parser.add_argument(
        "--offset",
        "-o",
        type=int,
        default=0,
        help="Number of results to skip",
    )
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a file")
    delete_parser.add_argument("id", type=str, help="ID of the file to delete")
    delete_parser.add_argument(
        "--hard",
        "-x",
        action="store_true",
        help="Permanently delete the file",
    )
    
    # Undelete command
    undelete_parser = subparsers.add_parser("undelete", help="Undelete a file")
    undelete_parser.add_argument("id", type=str, help="ID of the file to undelete")
    
    # Stats command
    subparsers.add_parser("stats", help="Get storage statistics")
    
    # Integrity command
    integrity_parser = subparsers.add_parser("integrity", help="Check storage integrity")
    integrity_parser.add_argument(
        "--repair",
        "-r",
        action="store_true",
        help="Attempt to repair issues",
    )
    
    # Vacuum command
    subparsers.add_parser("vacuum", help="Vacuum the storage")
    
    return parser.parse_args()


def format_file_info(file_info: FileInfo) -> str:
    """Format file information for display."""
    result = [
        f"ID: {file_info.id}",
        f"Name: {file_info.name}",
        f"Size: {file_info.formatted_size} ({file_info.size} bytes)",
        f"Created: {file_info.created_date}",
    ]
    
    if file_info.extension:
        result.append(f"Extension: {file_info.extension}")
    
    if file_info.sha256_hex:
        result.append(f"SHA-256: {file_info.sha256_hex}")
    
    result.append(f"Encrypted: {'Yes' if file_info.is_encrypted else 'No'}")
    
    if file_info.is_deleted:
        result.append(f"Deleted: Yes (at {file_info.deleted_date})")
    else:
        result.append("Deleted: No")
    
    if file_info.meta:
        result.append(f"Metadata: {file_info.meta}")
    
    return "\n".join(result)


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    if not args.command:
        print("Error: No command specified", file=sys.stderr)
        return 1
    
    # Set up encryption if requested
    crypto_provider: CryptoProvider = NullCrypto()
    
    if args.encrypt:
        try:
            if args.key_file:
                # Read key from file
                with open(args.key_file, "rb") as f:
                    key = f.read()
                if len(key) != 32:
                    print(
                        f"Error: Key file must contain 32 bytes, got {len(key)}",
                        file=sys.stderr,
                    )
                    return 1
            else:
                # Generate a new key
                key = os.urandom(32)
                # Save the key to a file in the storage directory
                key_path = Path(args.root) / ".q1_key"
                if not key_path.exists():
                    with open(key_path, "wb") as f:
                        f.write(key)
                    os.chmod(key_path, 0o600)
                    print(f"Generated encryption key saved to: {key_path}")
                else:
                    # Read the existing key
                    with open(key_path, "rb") as f:
                        key = f.read()
            
            # Create the AES crypto provider
            crypto_provider = AesGcmCrypto(key=key)
            
        except ImportError:
            print(
                "Error: Encryption requires the 'cryptography' package. "
                "Install with 'pip install q1[crypto]'.",
                file=sys.stderr,
            )
            return 1
    
    # Initialize the storage
    try:
        if args.command == "init":
            # Create the storage if it doesn't exist
            storage = Q1(args.root, crypto_provider=crypto_provider)
            storage.close()
            print(f"Initialized storage at: {args.root}")
            return 0
        
        # Create or open the storage
        store = Q1(args.root, crypto_provider=crypto_provider)
        
        try:
            # Execute the requested command
            if args.command == "put":
                # Get the file path
                file_path = Path(args.file)
                if not file_path.exists():
                    print(f"Error: File not found: {file_path}", file=sys.stderr)
                    return 1
                
                # Get the name to store it under
                name = args.name or file_path.name
                
                # Read the metadata if provided
                metadata = None
                if args.meta:
                    if os.path.exists(args.meta):
                        # Treat as a file path
                        with open(args.meta, "r") as f:
                            metadata = f.read()
                    else:
                        # Treat as literal JSON
                        metadata = args.meta
                
                # Store the file
                file_id = store.put(name, file_path, metadata=metadata)
                print(f"Stored file: {file_id}")
                
            elif args.command == "get":
                try:
                    if args.output:
                        # Write to a file
                        output_path = Path(args.output)
                        store.get(args.id, output=output_path)
                        print(f"Retrieved file to: {output_path}")
                    else:
                        # Write to stdout
                        data = store.get(args.id)
                        try:
                            # Try to decode as text for terminal-friendly output
                            sys.stdout.buffer.write(data)
                        except UnicodeDecodeError:
                            # If it's binary, write directly to stderr
                            sys.stdout.buffer.write(data)
                
                except FileMissing:
                    print(f"Error: File not found: {args.id}", file=sys.stderr)
                    return 1
            
            elif args.command == "info":
                try:
                    # Get file info
                    file_info = store.info(args.id, verify=args.verify)
                    print(format_file_info(file_info))
                
                except FileMissing:
                    print(f"Error: File not found: {args.id}", file=sys.stderr)
                    return 1
            
            elif args.command == "list":
                # List files with the provided filters
                files = list(
                    store.list(
                        name_like=args.name,
                        extension=args.extension,
                        include_deleted=args.deleted,
                        limit=args.limit,
                        offset=args.offset,
                    )
                )
                
                if not files:
                    print("No files found")
                    return 0
                
                # Print a summary for each file
                for file_info in files:
                    print(
                        f"{file_info.id} - "
                        f"{file_info.name} "
                        f"({file_info.formatted_size})"
                    )
                    if file_info.is_deleted:
                        print("  [DELETED]")
                    if file_info.is_encrypted:
                        print("  [ENCRYPTED]")
                
                print(f"\nTotal: {len(files)} file(s)")
            
            elif args.command == "delete":
                try:
                    # Delete the file
                    store.delete(args.id, hard=args.hard)
                    if args.hard:
                        print(f"Permanently deleted file: {args.id}")
                    else:
                        print(f"Marked file as deleted: {args.id}")
                
                except FileMissing:
                    print(f"Error: File not found: {args.id}", file=sys.stderr)
                    return 1
            
            elif args.command == "undelete":
                try:
                    # Undelete the file
                    store.undelete(args.id)
                    print(f"Restored file: {args.id}")
                
                except FileMissing:
                    print(f"Error: File not found: {args.id}", file=sys.stderr)
                    return 1
            
            elif args.command == "stats":
                # Get storage statistics
                stats = store.stats()
                print(f"Total files: {stats.total_files}")
                print(f"Total size: {stats.formatted_total_size}")
                print(f"Deleted files: {stats.deleted_files}")
                print(f"Deleted size: {stats.formatted_deleted_size}")
                print(f"Encrypted files: {stats.encrypted_files}")
                print(f"Encrypted size: {stats.formatted_encrypted_size}")
                
                if stats.extensions:
                    print("\nFile types:")
                    for ext, count in sorted(
                        stats.extensions.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    ):
                        print(f"  {ext}: {count}")
            
            elif args.command == "integrity":
                # Check storage integrity
                issues = store.integrity_check(repair=args.repair)
                
                if not issues:
                    print("Integrity check passed - no issues found")
                else:
                    print(f"Integrity check found {len(issues)} issue(s):")
                    for issue in issues:
                        print(f"  - {issue}")
            
            elif args.command == "vacuum":
                # Vacuum the storage
                store.vacuum()
                print("Storage vacuumed")
            
            else:
                print(f"Error: Unknown command: {args.command}", file=sys.stderr)
                return 1
            
            # Commit changes and close
            store.commit()
            return 0
        
        finally:
            # Always close the storage
            store.close()
    
    except Q1Error as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
