#!/usr/bin/env python3
"""Test semantic search functionality."""

import asyncio
import sys
from pathlib import Path

# Add thoth to path
sys.path.insert(0, str(Path(__file__).parent))

from thoth.storage.database import Database
from thoth.storage.backend import ThothStorage
from thoth.config.settings import ConfigManager
from thoth.indexer import Indexer


async def test_semantic_search():
    """Test the full semantic search pipeline."""
    print("=== Testing Semantic Search ===\n")
    
    # Initialize components
    db = Database()
    await db.init_db()
    
    storage = ThothStorage(use_vllm=True)
    await storage.initialize()
    
    config_manager = ConfigManager()
    indexer = Indexer(db, config_manager, storage)
    
    # Index the thoth repository
    print("1. Indexing thoth repository...")
    repo_path = Path(__file__).parent
    await indexer.index_repository("thoth", str(repo_path), "python")
    print("✅ Repository indexed\n")
    
    # Get stats
    stats = await storage.get_stats()
    print(f"2. Storage stats:")
    print(f"   - Total symbols: {stats['total_symbols']}")
    print(f"   - Total files: {stats['total_files']}")
    print(f"   - Vector count: {stats.get('vector_count', 0)}")
    print(f"   - Repositories: {stats['repositories']}\n")
    
    # Test semantic search queries
    queries = [
        "function to encode text into embeddings",
        "class that handles database operations",
        "method for parsing Python code",
        "semantic search implementation",
        "MCP server tools"
    ]
    
    print("3. Testing semantic search queries:")
    for i, query in enumerate(queries, 1):
        print(f"\n   Query {i}: '{query}'")
        results = await storage.search_semantic(query, limit=3)
        
        if results:
            for j, result in enumerate(results, 1):
                print(f"   Result {j}: {result['type']} {result['name']} (score: {result['score']:.3f})")
                print(f"             {result['repo']}/{result['file_path']}:{result['line']}")
        else:
            print("   No results found")
    
    # Cleanup
    await storage.close()
    await db.close()
    print("\n✅ Test completed!")


if __name__ == "__main__":
    asyncio.run(test_semantic_search())