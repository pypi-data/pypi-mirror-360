#!/usr/bin/env python3
"""Test semantic search functionality (search only)."""

import asyncio
import sys
from pathlib import Path

# Add thoth to path
sys.path.insert(0, str(Path(__file__).parent))

from thoth.storage.database import Database
from thoth.storage.backend import ThothStorage


async def test_search():
    """Test semantic search without re-indexing."""
    print("=== Testing Semantic Search ===\n")
    
    # Initialize components
    db = Database()
    await db.init_db()
    
    storage = ThothStorage(use_vllm=True)
    await storage.initialize()
    
    # Get stats
    stats = await storage.get_stats()
    print(f"Storage stats:")
    print(f"   - Total symbols: {stats['total_symbols']}")
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
    
    print("Testing semantic search queries:")
    for i, query in enumerate(queries, 1):
        print(f"\n   Query {i}: '{query}'")
        try:
            results = await storage.search_semantic(query, limit=3)
            
            if results:
                for j, result in enumerate(results, 1):
                    print(f"   Result {j}: {result['type']} {result['name']} (score: {result['score']:.3f})")
                    print(f"             {result['repo']}/{result['file_path']}:{result['line']}")
            else:
                print("   No results found")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Cleanup
    await storage.close()
    await db.close()
    print("\n✅ Test completed!")


if __name__ == "__main__":
    asyncio.run(test_search())