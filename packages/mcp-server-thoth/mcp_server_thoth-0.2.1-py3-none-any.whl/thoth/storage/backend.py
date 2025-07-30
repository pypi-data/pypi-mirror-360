"""
Unified storage backend with semantic search capabilities.
Supports vLLM embeddings with ChromaDB vector storage.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import numpy as np
import networkx as nx
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .database import Database
from .models import Repository, File, Symbol, Import, Call
from ..embeddings import EmbeddingProvider, TfidfEmbedder, VLLMEmbedder

logger = logging.getLogger(__name__)


class ThothStorage:
    """
    Unified storage backend with semantic search.
    
    Components:
    - SQLite: Source of truth for all structured data
    - ChromaDB: Vector storage for semantic search
    - NetworkX: In-memory graph for relationships
    - Embeddings: vLLM (primary) or TF-IDF (fallback)
    - Redis: Optional caching layer
    """
    
    def __init__(
        self,
        db_path: str = "~/.thoth/index.db",
        use_vllm: bool = True,
        vllm_model: str = "Qwen/Qwen3-Embedding-0.6B",
        use_redis: bool = False,
        redis_url: str = "redis://localhost:6379"
    ):
        """Initialize storage backend.
        
        Args:
            db_path: Path to SQLite database
            use_vllm: Whether to use vLLM for embeddings
            vllm_model: vLLM model to use
            use_redis: Whether to enable Redis caching
            redis_url: Redis connection URL
        """
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.db = Database(str(self.db_path))
        self.graph = nx.DiGraph()
        
        # Initialize embedding provider
        if use_vllm:
            try:
                self.embedder = VLLMEmbedder(model_name=vllm_model)
                logger.info(f"Using vLLM embeddings with {vllm_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize vLLM: {e}. Falling back to TF-IDF")
                self.embedder = TfidfEmbedder()
        else:
            self.embedder = TfidfEmbedder()
            logger.info("Using TF-IDF embeddings")
        
        # Optional Redis cache
        self.redis = None
        if use_redis:
            try:
                import redis
                self.redis = redis.from_url(redis_url)
                self.redis.ping()
                logger.info("Redis cache enabled")
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
        
        # Initialize ChromaDB
        self.chroma = None
        self.chroma_collection = None
        self._init_chromadb()
    
    def _init_chromadb(self) -> None:
        """Initialize ChromaDB for vector storage."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            chroma_path = self.db_path.parent / "chroma"
            chroma_path.mkdir(exist_ok=True)
            
            self.chroma = chromadb.PersistentClient(
                path=str(chroma_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get collection
            self.chroma_collection = self.chroma.get_or_create_collection(
                name="thoth_symbols",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("ChromaDB initialized for vector storage")
            
        except ImportError:
            logger.error("ChromaDB not installed. Install with: pip install chromadb>=0.4.0")
            raise
    
    async def initialize(self) -> None:
        """Initialize all storage components."""
        await self.db.init_db()
        await self._load_graph()
        await self._load_embeddings()
    
    async def _load_graph(self) -> None:
        """Load graph structure from database."""
        async with self.db.get_session() as session:
            # Load all symbols as nodes
            result = await session.execute(
                select(Symbol).options(
                    selectinload(Symbol.repository),
                    selectinload(Symbol.file)
                )
            )
            symbols = result.scalars().all()
            
            for symbol in symbols:
                self.graph.add_node(
                    f"symbol_{symbol.id}",
                    name=symbol.name,
                    type=symbol.type,
                    repo=symbol.repository.name,
                    file_path=symbol.file.path,
                    line=symbol.line,
                    docstring=symbol.docstring
                )
            
            # Load call relationships
            result = await session.execute(select(Call))
            calls = result.scalars().all()
            
            for call in calls:
                if call.caller_symbol_id and call.callee_symbol_id:
                    self.graph.add_edge(
                        f"symbol_{call.caller_symbol_id}",
                        f"symbol_{call.callee_symbol_id}",
                        type="calls"
                    )
            
            # Load import relationships (file to file)
            result = await session.execute(select(Import))
            imports = result.scalars().all()
            
            for imp in imports:
                if imp.resolved_file_id:
                    self.graph.add_edge(
                        f"file_{imp.file_id}",
                        f"file_{imp.resolved_file_id}",
                        type="imports"
                    )
            
            logger.info(f"Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    async def _load_embeddings(self) -> None:
        """Load or compute embeddings for all symbols."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(Symbol).options(
                    selectinload(Symbol.repository),
                    selectinload(Symbol.file)
                )
            )
            symbols = result.scalars().all()
            
            if not symbols:
                logger.info("No symbols to embed")
                return
            
            # Prepare texts for embedding
            texts = []
            metadatas = []
            ids = []
            
            for symbol in symbols:
                # Create rich text representation for embedding
                text_parts = [
                    f"{symbol.type} {symbol.name}",
                    f"in {symbol.repository.name}/{symbol.file.path}",
                ]
                if symbol.docstring:
                    text_parts.append(f"docstring: {symbol.docstring}")
                
                text = " ".join(text_parts)
                texts.append(text)
                
                # Metadata for ChromaDB
                metadatas.append({
                    "symbol_id": symbol.id,
                    "name": symbol.name,
                    "type": symbol.type,
                    "repo": symbol.repository.name,
                    "file_path": symbol.file.path,
                    "line": symbol.line
                })
                
                ids.append(f"symbol_{symbol.id}")
            
            # Fit TF-IDF if using it
            if isinstance(self.embedder, TfidfEmbedder):
                logger.info("Fitting TF-IDF on symbol texts")
                self.embedder.fit(texts)
            
            # Compute embeddings in batches
            batch_size = 50  # Reduced batch size to avoid OOM
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_metas = metadatas[i:i + batch_size]
                batch_ids = ids[i:i + batch_size]
                
                # Get embeddings
                embeddings = self.embedder.encode(batch_texts)
                if not isinstance(embeddings, list):
                    embeddings = [embeddings]
                
                # Convert to CPU numpy arrays to free GPU memory
                cpu_embeddings = []
                for emb in embeddings:
                    if hasattr(emb, 'cpu'):
                        # If it's a torch tensor, move to CPU
                        cpu_embeddings.append(emb.cpu().numpy())
                    else:
                        # Already numpy array
                        cpu_embeddings.append(emb)
                
                # Store in ChromaDB
                self.chroma_collection.upsert(
                    embeddings=[emb.tolist() for emb in cpu_embeddings],
                    documents=batch_texts,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
                
                logger.info(f"Embedded batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            
            logger.info(f"Completed embedding {len(texts)} symbols")
    
    async def search_semantic(
        self,
        query: str,
        repo: Optional[str] = None,
        symbol_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Semantic search for symbols.
        
        Args:
            query: Search query
            repo: Filter by repository name
            symbol_type: Filter by symbol type (function, class, method)
            limit: Maximum results to return
            
        Returns:
            List of matching symbols with scores
        """
        if not self.chroma_collection:
            raise RuntimeError("ChromaDB not initialized")
        
        # Build filter
        where = {}
        if repo:
            where["repo"] = repo
        if symbol_type:
            where["type"] = symbol_type
        
        # Encode query with same embedder used for indexing
        query_embedding = self.embedder.encode(query)
        if hasattr(query_embedding, 'cpu'):
            query_embedding = query_embedding.cpu().numpy()
        
        # Search ChromaDB with embedding
        results = self.chroma_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=limit,
            where=where if where else None
        )
        
        # Format results
        output = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                score = 1.0 - (results['distances'][0][i] if results['distances'] else 0.5)
                
                output.append({
                    "symbol_id": metadata["symbol_id"],
                    "name": metadata["name"],
                    "type": metadata["type"],
                    "repo": metadata["repo"],
                    "file_path": metadata["file_path"],
                    "line": metadata["line"],
                    "score": score,
                    "preview": results['documents'][0][i][:200] + "..."
                })
        
        return output
    
    async def get_symbol_context(
        self,
        symbol_id: int,
        include_callers: bool = True,
        include_callees: bool = True,
        depth: int = 1
    ) -> Dict[str, Any]:
        """Get rich context for a symbol including relationships.
        
        Args:
            symbol_id: Symbol ID to get context for
            include_callers: Include functions that call this symbol
            include_callees: Include functions called by this symbol
            depth: How many levels deep to traverse
            
        Returns:
            Symbol context with relationships
        """
        async with self.db.get_session() as session:
            # Get symbol details
            result = await session.execute(
                select(Symbol)
                .where(Symbol.id == symbol_id)
                .options(
                    selectinload(Symbol.repository),
                    selectinload(Symbol.file)
                )
            )
            symbol = result.scalar_one_or_none()
            
            if not symbol:
                return {}
            
            context = {
                "id": symbol.id,
                "name": symbol.name,
                "type": symbol.type,
                "file_path": symbol.file.path,
                "line": symbol.line,
                "docstring": symbol.docstring,
                "repository": symbol.repository.name
            }
            
            node_id = f"symbol_{symbol_id}"
            
            # Get relationships from graph
            if include_callers and node_id in self.graph:
                callers = []
                for pred in self.graph.predecessors(node_id):
                    if self.graph.edges[pred, node_id].get('type') == 'calls':
                        callers.append(self.graph.nodes[pred])
                context["called_by"] = callers
            
            if include_callees and node_id in self.graph:
                callees = []
                for succ in self.graph.successors(node_id):
                    if self.graph.edges[node_id, succ].get('type') == 'calls':
                        callees.append(self.graph.nodes[succ])
                context["calls"] = callees
            
            return context
    
    async def update_symbol_embeddings(
        self,
        symbol_ids: Optional[List[int]] = None
    ) -> None:
        """Update embeddings for specific symbols or all symbols.
        
        Args:
            symbol_ids: List of symbol IDs to update, or None for all
        """
        async with self.db.get_session() as session:
            query = select(Symbol).options(
                selectinload(Symbol.repository),
                selectinload(Symbol.file)
            )
            
            if symbol_ids:
                query = query.where(Symbol.id.in_(symbol_ids))
            
            result = await session.execute(query)
            symbols = result.scalars().all()
            
            # Update embeddings
            for symbol in symbols:
                text = f"{symbol.type} {symbol.name} in {symbol.repository.name}/{symbol.file.path}"
                if symbol.docstring:
                    text += f" docstring: {symbol.docstring}"
                
                embedding = self.embedder.encode(text)
                if isinstance(embedding, list):
                    embedding = embedding[0]
                
                # Update in ChromaDB
                self.chroma_collection.update(
                    embeddings=[embedding.tolist()],
                    documents=[text],
                    metadatas=[{
                        "symbol_id": symbol.id,
                        "name": symbol.name,
                        "type": symbol.type,
                        "repo": symbol.repository.name,
                        "file_path": symbol.file.path,
                        "line": symbol.line
                    }],
                    ids=[f"symbol_{symbol.id}"]
                )
        
        logger.info(f"Updated embeddings for {len(symbols)} symbols")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics.
        
        Returns:
            Dictionary with storage stats
        """
        stats = {
            "total_symbols": len([n for n in self.graph.nodes if n.startswith("symbol_")]),
            "total_files": len([n for n in self.graph.nodes if n.startswith("file_")]),
            "total_calls": len([e for e in self.graph.edges if self.graph.edges[e].get('type') == 'calls']),
            "total_imports": len([e for e in self.graph.edges if self.graph.edges[e].get('type') == 'imports']),
            "embedding_type": type(self.embedder).__name__,
            "redis_enabled": self.redis is not None,
            "chromadb_enabled": self.chroma is not None
        }
        
        if self.chroma_collection:
            stats["vector_count"] = self.chroma_collection.count()
        
        # Get repository list
        repos = set()
        for node, data in self.graph.nodes(data=True):
            if 'repo' in data:
                repos.add(data['repo'])
        stats["repositories"] = sorted(list(repos))
        
        return stats
    
    async def close(self) -> None:
        """Cleanup resources."""
        if self.redis:
            self.redis.close()
        
        logger.info("Storage backend closed")