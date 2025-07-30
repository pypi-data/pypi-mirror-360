#!/usr/bin/env python3
"""Test script for vLLM embeddings with Qwen3-Embedding-0.6B."""

import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_embeddings():
    """Test the embedding functionality."""
    try:
        # Test 1: Initialize vLLM embedder
        logger.info("Test 1: Initializing vLLM embedder...")
        from thoth.embeddings import VLLMEmbedder
        
        embedder = VLLMEmbedder(model_name="Qwen/Qwen3-Embedding-0.6B")
        logger.info("✅ vLLM embedder initialized successfully")
        
        # Test 2: Encode single text
        logger.info("\nTest 2: Encoding single text...")
        text = "def calculate_sum(a: int, b: int) -> int: return a + b"
        embedding = embedder.encode(text)
        logger.info(f"✅ Single text encoded: shape={embedding.shape}, dtype={embedding.dtype}")
        
        # Test 3: Encode multiple texts
        logger.info("\nTest 3: Encoding multiple texts...")
        texts = [
            "class Calculator: def add(self, a, b): return a + b",
            "def multiply(x, y): return x * y",
            "import numpy as np"
        ]
        embeddings = embedder.encode(texts)
        logger.info(f"✅ Multiple texts encoded: {len(embeddings)} embeddings")
        
        # Test 4: Code-specific encoding
        logger.info("\nTest 4: Code-specific encoding...")
        code_embedding = embedder.encode_code(
            "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
            context="function"
        )
        logger.info(f"✅ Code encoded with context: shape={code_embedding.shape}")
        
        # Test 5: Test with TF-IDF fallback
        logger.info("\nTest 5: Testing TF-IDF fallback...")
        from thoth.embeddings import TfidfEmbedder
        
        tfidf = TfidfEmbedder()
        tfidf.fit(texts)
        tfidf_embedding = tfidf.encode(text)
        logger.info(f"✅ TF-IDF encoding: shape={tfidf_embedding.shape}")
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("Make sure vLLM is installed: pip install vllm>=0.8.5")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
    
    logger.info("\n✅ All tests passed!")
    return True


async def test_storage_integration():
    """Test the full storage integration."""
    logger.info("\n" + "="*50)
    logger.info("Testing storage integration...")
    
    try:
        from thoth.storage.backend import ThothStorage
        
        # Initialize storage with vLLM
        logger.info("Initializing storage with vLLM...")
        storage = ThothStorage(
            db_path="/tmp/test_thoth.db",
            use_vllm=True,
            vllm_model="Qwen/Qwen3-Embedding-0.6B"
        )
        await storage.initialize()
        logger.info("✅ Storage initialized with vLLM")
        
        # Get stats
        stats = await storage.get_stats()
        logger.info(f"Storage stats: {stats}")
        
        # Cleanup
        await storage.close()
        Path("/tmp/test_thoth.db").unlink(missing_ok=True)
        
    except Exception as e:
        logger.error(f"❌ Storage test failed: {e}")
        return False
    
    return True


async def main():
    """Run all tests."""
    logger.info("Testing vLLM integration with Qwen3-Embedding-0.6B")
    logger.info("="*50)
    
    # Run embedding tests
    embed_success = await test_embeddings()
    
    # Run storage tests
    storage_success = await test_storage_integration()
    
    if embed_success and storage_success:
        logger.info("\n🎉 All tests passed! vLLM integration is working.")
    else:
        logger.error("\n❌ Some tests failed. Check the logs above.")


if __name__ == "__main__":
    asyncio.run(main())