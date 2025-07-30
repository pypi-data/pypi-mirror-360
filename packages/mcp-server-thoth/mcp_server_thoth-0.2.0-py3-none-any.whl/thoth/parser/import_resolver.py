"""Resolve imports across repositories."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.settings import ConfigManager, RepositoryConfig
from ..storage.models import File, Import, Repository


class ImportResolver:
    """Resolves import statements to their actual files across repositories."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self._repo_cache: Dict[str, RepositoryConfig] = {}
    
    async def resolve_imports(self, session: AsyncSession, repository_id: int) -> None:
        """Resolve all imports for a repository."""
        # Get the repository
        result = await session.execute(
            select(Repository).where(Repository.id == repository_id)
        )
        repo = result.scalar_one()
        
        # Get repository config
        repo_config = self.config_manager.get_repository(repo.name)
        if not repo_config:
            return
        
        # Get all imports for this repository
        result = await session.execute(
            select(Import)
            .join(File)
            .where(File.repository_id == repository_id)
            .where(Import.resolved_file_id.is_(None))
        )
        imports = result.scalars().all()
        
        # Build cache of all repositories
        all_repos = self.config_manager.list_repositories()
        
        for imp in imports:
            resolved = await self._resolve_single_import(
                session, imp, repo, repo_config, all_repos
            )
            if resolved:
                imp.resolved_repository_id = resolved[0]
                imp.resolved_file_id = resolved[1]
        
        await session.commit()
    
    async def _resolve_single_import(
        self,
        session: AsyncSession,
        imp: Import,
        source_repo: Repository,
        source_config: RepositoryConfig,
        all_repos: Dict[str, RepositoryConfig]
    ) -> Optional[Tuple[int, int]]:
        """Resolve a single import to (repository_id, file_id)."""
        module_parts = imp.module.split('.')
        
        # Check if it's a cross-repo import
        if module_parts[0] in all_repos:
            # Direct repository import (e.g., "slush.api.client")
            target_repo_name = module_parts[0]
            module_path = '.'.join(module_parts[1:])
        else:
            # Check related repositories
            related_repos = self.config_manager.get_related_repositories(source_repo.name)
            
            # Try to find the module in related repos
            for repo_name in related_repos:
                if await self._module_exists_in_repo(session, repo_name, imp.module):
                    target_repo_name = repo_name
                    module_path = imp.module
                    break
            else:
                # Module not found in related repos
                return None
        
        # Get target repository
        result = await session.execute(
            select(Repository).where(Repository.name == target_repo_name)
        )
        target_repo = result.scalar_one_or_none()
        
        if not target_repo:
            return None
        
        # Convert module path to file path
        file_paths = self._module_to_file_paths(module_path)
        
        # Try to find the file
        for file_path in file_paths:
            result = await session.execute(
                select(File).where(
                    File.repository_id == target_repo.id,
                    File.path == file_path
                )
            )
            file = result.scalar_one_or_none()
            
            if file:
                return (target_repo.id, file.id)
        
        return None
    
    async def _module_exists_in_repo(
        self, session: AsyncSession, repo_name: str, module: str
    ) -> bool:
        """Check if a module exists in a repository."""
        result = await session.execute(
            select(Repository).where(Repository.name == repo_name)
        )
        repo = result.scalar_one_or_none()
        
        if not repo:
            return False
        
        file_paths = self._module_to_file_paths(module)
        
        for file_path in file_paths:
            result = await session.execute(
                select(File).where(
                    File.repository_id == repo.id,
                    File.path == file_path
                ).limit(1)
            )
            if result.scalar_one_or_none():
                return True
        
        return False
    
    def _module_to_file_paths(self, module: str) -> List[str]:
        """Convert module name to possible file paths."""
        parts = module.split('.')
        paths = []
        
        # Try as a file
        paths.append('/'.join(parts) + '.py')
        
        # Try as a package
        paths.append('/'.join(parts) + '/__init__.py')
        
        # If it's a single part, also try in common locations
        if len(parts) == 1:
            paths.extend([
                f'src/{parts[0]}.py',
                f'lib/{parts[0]}.py',
                f'{parts[0]}/__init__.py',
            ])
        
        return paths