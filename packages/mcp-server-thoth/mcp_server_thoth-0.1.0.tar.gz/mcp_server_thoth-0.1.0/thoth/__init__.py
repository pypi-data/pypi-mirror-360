"""Thoth - A deterministic codebase memory and visualization MCP server."""

__version__ = "0.1.0"

import argparse
import asyncio
import os
import sys
from pathlib import Path


def main():
    """Main entry point for MCP server."""
    parser = argparse.ArgumentParser(
        description="Thoth MCP Server - Persistent codebase memory for AI assistants"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to database file (default: ~/.thoth/index.db)"
    )
    parser.add_argument(
        "--init",
        nargs="+",
        metavar="REPO_PATH",
        help="Initialize by indexing repositories at the given paths"
    )
    
    args = parser.parse_args()
    
    # If init mode, index repositories first
    if args.init:
        from .cli.main import index_repos_for_init
        asyncio.run(index_repos_for_init(args.init))
        print("Initialization complete. You can now use the MCP server.")
        return
    
    # Otherwise, start the MCP server
    from .mcp.server import main as server_main
    
    # Set database path if provided
    if args.db_path:
        os.environ["THOTH_DB_PATH"] = args.db_path
    
    try:
        asyncio.run(server_main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)