"""CLI commands for Thoth."""

import asyncio
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.table import Table

from ..config.settings import ConfigManager
from ..indexer import Indexer
from ..storage.database import Database

console = Console()
config_manager = ConfigManager()


@click.group()
def cli():
    """Thoth - Codebase memory and visualization MCP server."""
    pass


@cli.command()
@click.argument('name')
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--language', '-l', default='python', help='Programming language')
@click.option('--tags', '-t', multiple=True, help='Tags for the repository')
@click.option('--related-to', '-r', multiple=True, help='Related repository names')
def index(name: str, path: str, language: str, tags: tuple, related_to: tuple):
    """Index a repository."""
    # Save to config
    config_manager.add_repository(name, path, language, list(tags), list(related_to))
    
    async def run():
        db = Database()
        await db.init_db()
        
        indexer = Indexer(db, config_manager)
        
        with console.status(f"Indexing repository '{name}'..."):
            try:
                await indexer.index_repository(name, path, language)
                console.print(f"[green]✓[/green] Successfully indexed repository '{name}'")
            except Exception as e:
                console.print(f"[red]✗[/red] Error indexing repository: {e}")
            finally:
                await db.close()
    
    asyncio.run(run())


@cli.command()
def list():
    """List indexed repositories."""
    async def run():
        db = Database()
        await db.init_db()
        
        async with db.get_session() as session:
            from sqlalchemy import select
            from ..storage.models import Repository
            
            result = await session.execute(select(Repository))
            repos = result.scalars().all()
            
            if not repos:
                console.print("No repositories indexed yet.")
                return
            
            table = Table(title="Indexed Repositories")
            table.add_column("Name", style="cyan")
            table.add_column("Path", style="green")
            table.add_column("Language")
            table.add_column("Last Indexed")
            
            for repo in repos:
                last_indexed = repo.last_indexed.strftime("%Y-%m-%d %H:%M") if repo.last_indexed else "Never"
                table.add_row(repo.name, repo.path, repo.language or "N/A", last_indexed)
            
            console.print(table)
        
        await db.close()
    
    asyncio.run(run())


@cli.command()
def server():
    """Start the MCP server."""
    from ..mcp.server import main as server_main
    
    console.print("[bold]Starting Thoth MCP server...[/bold]")
    try:
        asyncio.run(server_main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped.[/yellow]")


@cli.command()
@click.argument('query')
@click.option('--repo', '-r', multiple=True, help='Repository to search')
def search(query: str, repo: tuple):
    """Search for symbols."""
    async def run():
        db = Database()
        await db.init_db()
        
        async with db.get_session() as session:
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload
            from ..storage.models import Symbol, Repository
            
            q = select(Symbol).where(Symbol.name.like(f"%{query}%"))
            
            if repo:
                q = q.join(Repository).where(Repository.name.in_(repo))
            
            q = q.options(
                selectinload(Symbol.file),
                selectinload(Symbol.repository)
            ).limit(20)
            
            result = await session.execute(q)
            symbols = result.scalars().all()
            
            if not symbols:
                console.print(f"No symbols found matching '{query}'")
                return
            
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("Symbol", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Location", style="green")
            
            for sym in symbols:
                location = f"{sym.repository.name}/{sym.file.path}:{sym.line}"
                table.add_row(sym.name, sym.type, location)
            
            console.print(table)
        
        await db.close()
    
    asyncio.run(run())


@cli.command()
def config():
    """Show configuration."""
    config = config_manager.load()
    
    console.print("[bold cyan]Thoth Configuration[/bold cyan]")
    console.print(f"Config file: {config_manager.config_path}")
    
    if not config.repositories:
        console.print("\nNo repositories configured yet.")
        return
    
    table = Table(title="Configured Repositories")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Language")
    table.add_column("Tags")
    table.add_column("Related To")
    
    for name, repo in config.repositories.items():
        tags = ", ".join(repo.tags) if repo.tags else ""
        related = ", ".join(repo.related_to) if repo.related_to else ""
        table.add_row(name, repo.path, repo.language, tags, related)
    
    console.print(table)


async def index_repos_for_init(repo_paths: List[str]) -> None:
    """Index repositories during initialization."""
    db = Database()
    await db.init_db()
    
    indexer = Indexer(db, config_manager)
    
    for path in repo_paths:
        repo_path = Path(path).resolve()
        if not repo_path.exists():
            console.print(f"[red]Path does not exist: {path}[/red]")
            continue
            
        repo_name = repo_path.name
        console.print(f"[cyan]Indexing {repo_name}...[/cyan]")
        
        try:
            # Auto-detect relationships based on common patterns
            related = []
            if 'client' in repo_name:
                # Look for server repo
                server_name = repo_name.replace('-client', '').replace('_client', '')
                related.append(server_name)
            elif 'server' in repo_name or not 'client' in repo_name:
                # Look for client repo
                related.extend([f"{repo_name}-client", f"{repo_name}_client"])
            
            # Save to config
            tags = []
            if 'client' in repo_name:
                tags = ['client', 'frontend']
            elif 'server' in repo_name:
                tags = ['server', 'backend']
                
            config_manager.add_repository(repo_name, str(repo_path), 'python', tags, related)
            
            # Index the repository
            await indexer.index_repository(repo_name, str(repo_path), 'python')
            console.print(f"[green]✓[/green] Indexed {repo_name}")
            
        except Exception as e:
            console.print(f"[red]✗[/red] Error indexing {repo_name}: {e}")
    
    await db.close()


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()