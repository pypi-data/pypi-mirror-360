"""Configuration management for Thoth."""

import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


class RepositoryConfig(BaseModel):
    """Configuration for a single repository."""
    path: str
    language: str = "python"
    tags: List[str] = Field(default_factory=list)
    related_to: List[str] = Field(default_factory=list)


class IndexOptions(BaseModel):
    """Options for indexing."""
    auto_discover_imports: bool = True
    track_api_calls: bool = True
    ignore_patterns: List[str] = Field(default_factory=lambda: [
        "*.pyc", "__pycache__", ".git", ".venv", "venv", "env",
        "node_modules", "dist", "build", "*.egg-info"
    ])


class ThothConfig(BaseModel):
    """Main configuration for Thoth."""
    repositories: Dict[str, RepositoryConfig] = Field(default_factory=dict)
    index_options: IndexOptions = Field(default_factory=IndexOptions)


class ConfigManager:
    """Manages Thoth configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            self.config_dir = Path.home() / '.thoth'
            self.config_path = self.config_dir / 'config.yaml'
        else:
            self.config_path = config_path
            self.config_dir = config_path.parent
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config: Optional[ThothConfig] = None
    
    def load(self) -> ThothConfig:
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            self._config = ThothConfig(**data)
        else:
            self._config = ThothConfig()
        return self._config
    
    def save(self) -> None:
        """Save configuration to file."""
        if self._config is None:
            self.load()
        
        with open(self.config_path, 'w') as f:
            yaml.dump(self._config.model_dump(), f, default_flow_style=False)
    
    def add_repository(self, name: str, path: str, language: str = "python", 
                      tags: List[str] = None, related_to: List[str] = None) -> None:
        """Add or update a repository configuration."""
        if self._config is None:
            self.load()
        
        self._config.repositories[name] = RepositoryConfig(
            path=str(Path(path).resolve()),
            language=language,
            tags=tags or [],
            related_to=related_to or []
        )
        self.save()
    
    def get_repository(self, name: str) -> Optional[RepositoryConfig]:
        """Get repository configuration by name."""
        if self._config is None:
            self.load()
        return self._config.repositories.get(name)
    
    def list_repositories(self) -> Dict[str, RepositoryConfig]:
        """List all configured repositories."""
        if self._config is None:
            self.load()
        return self._config.repositories
    
    def get_related_repositories(self, name: str) -> List[str]:
        """Get repositories related to the given one."""
        repo = self.get_repository(name)
        if not repo:
            return []
        
        # Get explicitly related repos
        related = set(repo.related_to)
        
        # Also find repos that list this one as related
        for repo_name, repo_config in self.list_repositories().items():
            if name in repo_config.related_to:
                related.add(repo_name)
        
        return list(related - {name})  # Exclude self