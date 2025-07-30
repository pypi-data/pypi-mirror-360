"""Database connection and session management."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


class Database:
    """Async database connection manager."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Check environment variable first
            db_path = os.environ.get('THOTH_DB_PATH')
            
        if db_path is None:
            thoth_dir = Path.home() / '.thoth'
            thoth_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(thoth_dir / 'index.db')
        
        self.engine = create_async_engine(
            f'sqlite+aiosqlite:///{db_path}',
            echo=False
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def init_db(self):
        """Initialize database schema."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        async with self.async_session() as session:
            yield session
    
    async def close(self):
        """Close database connection."""
        await self.engine.dispose()