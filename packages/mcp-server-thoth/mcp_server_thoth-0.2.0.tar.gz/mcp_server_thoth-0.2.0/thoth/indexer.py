"""File indexer that coordinates parsing and storage."""

import asyncio
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config.settings import ConfigManager
from .parser.call_analyzer import resolve_calls_in_repository
from .parser.import_resolver import ImportResolver
from .parser.python_parser import PythonParser, FileInfo
from .storage.database import Database
from .storage.backend import ThothStorage
from .storage.models import Repository, File, Symbol, Import, Call


class Indexer:
    """Indexes code repositories by parsing and storing analysis data."""
    
    def __init__(self, db: Database, config_manager: Optional[ConfigManager] = None, storage: Optional[ThothStorage] = None):
        self.db = db
        self.storage = storage
        self.config_manager = config_manager or ConfigManager()
        self.parser = PythonParser()
        self.import_resolver = ImportResolver(self.config_manager)
    
    async def index_repository(self, name: str, path: str, language: str = "python") -> None:
        """Index a complete repository."""
        repo_path = Path(path).resolve()
        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {path}")
        
        async with self.db.get_session() as session:
            # Get or create repository
            repo = await self._get_or_create_repository(session, name, str(repo_path), language)
            
            # Find all Python files
            py_files = list(repo_path.rglob("*.py"))
            
            # Index each file
            for file_path in py_files:
                # Skip virtual environments and hidden directories
                if any(part.startswith('.') or part in {'venv', 'env', '__pycache__'} 
                       for part in file_path.parts):
                    continue
                
                await self._index_file(session, repo, file_path)
            
            # Update last indexed time
            repo.last_indexed = datetime.utcnow()
            await session.commit()
            
            # Resolve imports across repositories
            await self.import_resolver.resolve_imports(session, repo.id)
            
            # Analyze calls
            await resolve_calls_in_repository(session, repo.id)
            
            # Update embeddings if storage is available
            if self.storage:
                await self.storage._load_graph()  # Reload graph with new data
                await self.storage._load_embeddings()  # Recompute embeddings
    
    async def _get_or_create_repository(
        self, session: AsyncSession, name: str, path: str, language: str
    ) -> Repository:
        """Get existing repository or create new one."""
        result = await session.execute(
            select(Repository).where(Repository.name == name)
        )
        repo = result.scalar_one_or_none()
        
        if repo is None:
            repo = Repository(name=name, path=path, language=language)
            session.add(repo)
            await session.commit()
        else:
            # Update path if changed
            repo.path = path
        
        return repo
    
    async def _index_file(self, session: AsyncSession, repo: Repository, file_path: Path) -> None:
        """Index a single file."""
        # Calculate file hash
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Get relative path
        rel_path = file_path.relative_to(repo.path)
        
        # Check if file needs reindexing
        result = await session.execute(
            select(File).where(
                File.repository_id == repo.id,
                File.path == str(rel_path)
            )
        )
        file_record = result.scalar_one_or_none()
        
        if file_record and file_record.content_hash == content_hash:
            # File unchanged, skip
            return
        
        # Parse file
        file_info = self.parser.parse_file(str(file_path))
        
        # Update or create file record
        if file_record is None:
            file_record = File(
                repository_id=repo.id,
                path=str(rel_path),
                content_hash=content_hash,
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime)
            )
            session.add(file_record)
        else:
            # Clear existing data
            await session.execute(
                select(Symbol).where(Symbol.file_id == file_record.id)
            )
            for symbol in await session.scalars(select(Symbol).where(Symbol.file_id == file_record.id)):
                await session.delete(symbol)
            
            await session.execute(
                select(Import).where(Import.file_id == file_record.id)
            )
            for imp in await session.scalars(select(Import).where(Import.file_id == file_record.id)):
                await session.delete(imp)
            
            file_record.content_hash = content_hash
            file_record.last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        await session.flush()
        
        # Store symbols
        symbol_map: Dict[str, Symbol] = {}
        
        for sym in file_info.symbols:
            parent_id = None
            if sym.parent and sym.parent in symbol_map:
                parent_id = symbol_map[sym.parent].id
            
            db_symbol = Symbol(
                name=sym.name,
                type=sym.type,
                repository_id=repo.id,
                file_id=file_record.id,
                line=sym.line,
                column=sym.column,
                parent_id=parent_id,
                docstring=sym.docstring
            )
            session.add(db_symbol)
            await session.flush()
            
            # Track for parent relationships
            full_name = f"{sym.parent}.{sym.name}" if sym.parent else sym.name
            symbol_map[full_name] = db_symbol
        
        # Store imports
        for imp in file_info.imports:
            db_import = Import(
                file_id=file_record.id,
                module=imp.module,
                name=imp.name,
                alias=imp.alias,
                line=imp.line
            )
            session.add(db_import)
        
        # Store calls (we'll resolve them in a second pass)
        for call in file_info.calls:
            db_call = Call(
                file_id=file_record.id,
                line=call.line,
                column=call.column
            )
            # TODO: Resolve caller and callee symbols
            session.add(db_call)
        
        await session.commit()