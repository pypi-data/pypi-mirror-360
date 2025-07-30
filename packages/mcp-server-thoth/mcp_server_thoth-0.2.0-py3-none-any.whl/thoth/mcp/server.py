"""MCP server for codebase memory and visualization."""

import asyncio
from typing import Any

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from ..storage.database import Database
from ..storage.models import Repository, Symbol, File, Import, Call
from ..storage.backend import ThothStorage
from ..visualizations.mermaid import generate_module_diagram, generate_system_architecture_diagram

from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Create a server instance
server = Server("thoth")

# Global instances
db: Database = None
storage: ThothStorage = None


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="find_definition",
            description="Find where a symbol (function, class, method) is defined",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Symbol name to find"},
                    "repos": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Repository names to search (optional)"
                    }
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="get_file_structure",
            description="Get the structure of a file (functions, classes, imports)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path relative to repository"},
                    "repo": {"type": "string", "description": "Repository name"}
                },
                "required": ["file_path", "repo"]
            }
        ),
        types.Tool(
            name="search_symbols",
            description="Search for symbols by partial name match",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "type_filter": {
                        "type": "string",
                        "enum": ["function", "class", "method"],
                        "description": "Filter by symbol type (optional)"
                    },
                    "repos": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Repository names to search (optional)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_callers",
            description="Find all places where a function/method is called",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Function/method name"},
                    "repos": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Repository names to search (optional)"
                    }
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="generate_module_diagram",
            description="Generate a Mermaid diagram of module dependencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository name"}
                },
                "required": ["repo"]
            }
        ),
        types.Tool(
            name="list_repositories",
            description="List all indexed repositories",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="generate_system_architecture",
            description="Generate a system architecture diagram showing all repositories and their relationships",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="trace_api_flow",
            description="Trace the flow from a client API call to server handler",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "API endpoint path or WebSocket message name"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="index_repository",
            description="Index a new repository into the codebase memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Repository name (used as identifier)"},
                    "path": {"type": "string", "description": "Absolute path to the repository directory"},
                    "language": {"type": "string", "description": "Programming language (default: python)", "default": "python"}
                },
                "required": ["name", "path"]
            }
        ),
        types.Tool(
            name="semantic_search",
            description="Search for symbols using semantic similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language search query"},
                    "repo": {"type": "string", "description": "Filter by repository name (optional)"},
                    "symbol_type": {
                        "type": "string",
                        "enum": ["function", "class", "method"],
                        "description": "Filter by symbol type (optional)"
                    },
                    "limit": {"type": "integer", "description": "Maximum results (default: 10)", "default": 10}
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    if arguments is None:
        arguments = {}
    
    global db, storage
    if db is None:
        db = Database()
        await db.init_db()
    if storage is None:
        storage = ThothStorage()
        await storage.initialize()
    
    if name == "find_definition":
        return await find_definition(arguments)
    elif name == "get_file_structure":
        return await get_file_structure(arguments)
    elif name == "search_symbols":
        return await search_symbols(arguments)
    elif name == "get_callers":
        return await get_callers(arguments)
    elif name == "generate_module_diagram":
        return await generate_module_diagram(arguments)
    elif name == "list_repositories":
        return await list_repositories(arguments)
    elif name == "generate_system_architecture":
        return await generate_system_architecture(arguments)
    elif name == "trace_api_flow":
        return await trace_api_flow(arguments)
    elif name == "index_repository":
        return await index_repository(arguments)
    elif name == "semantic_search":
        return await semantic_search(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def find_definition(args: dict) -> list[types.TextContent]:
    """Find symbol definition."""
    name = args["name"]
    repos = args.get("repos", [])
    
    async with db.get_session() as session:
        query = select(Symbol).where(Symbol.name == name)
        
        if repos:
            query = query.join(Repository).where(Repository.name.in_(repos))
        
        query = query.options(
            selectinload(Symbol.file),
            selectinload(Symbol.repository)
        )
        
        results = await session.execute(query)
        symbols = results.scalars().all()
        
        if not symbols:
            return [types.TextContent(
                type="text",
                text=f"No definition found for '{name}'"
            )]
        
        lines = []
        for sym in symbols:
            repo_name = sym.repository.name
            file_path = sym.file.path
            lines.append(f"{repo_name}/{file_path}:{sym.line} - {sym.type} {sym.name}")
            if sym.docstring:
                lines.append(f"  Docstring: {sym.docstring[:100]}...")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def get_file_structure(args: dict) -> list[types.TextContent]:
    """Get file structure."""
    file_path = args["file_path"]
    repo_name = args["repo"]
    
    async with db.get_session() as session:
        # Get file
        result = await session.execute(
            select(File)
            .join(Repository)
            .where(
                Repository.name == repo_name,
                File.path == file_path
            )
            .options(
                selectinload(File.symbols),
                selectinload(File.imports)
            )
        )
        file = result.scalar_one_or_none()
        
        if not file:
            return [types.TextContent(
                type="text",
                text=f"File not found: {repo_name}/{file_path}"
            )]
        
        lines = [f"File: {repo_name}/{file_path}"]
        
        # List imports
        if file.imports:
            lines.append("\nImports:")
            for imp in file.imports:
                import_str = f"  - {imp.module}"
                if imp.name:
                    import_str += f".{imp.name}"
                if imp.alias:
                    import_str += f" as {imp.alias}"
                lines.append(import_str)
        
        # List symbols
        if file.symbols:
            lines.append("\nSymbols:")
            # Group by type
            classes = [s for s in file.symbols if s.type == 'class']
            functions = [s for s in file.symbols if s.type == 'function']
            methods = [s for s in file.symbols if s.type == 'method']
            
            if classes:
                lines.append("  Classes:")
                for cls in classes:
                    lines.append(f"    - {cls.name} (line {cls.line})")
                    # List methods under class
                    class_methods = [m for m in methods if m.parent_id == cls.id]
                    for method in class_methods:
                        lines.append(f"      - {method.name} (line {method.line})")
            
            if functions:
                lines.append("  Functions:")
                for func in functions:
                    lines.append(f"    - {func.name} (line {func.line})")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def search_symbols(args: dict) -> list[types.TextContent]:
    """Search symbols by name."""
    query_str = args["query"]
    type_filter = args.get("type_filter")
    repos = args.get("repos", [])
    
    async with db.get_session() as session:
        query = select(Symbol).where(Symbol.name.like(f"%{query_str}%"))
        
        if type_filter:
            query = query.where(Symbol.type == type_filter)
        
        if repos:
            query = query.join(Repository).where(Repository.name.in_(repos))
        
        query = query.options(
            selectinload(Symbol.file),
            selectinload(Symbol.repository)
        ).limit(50)
        
        results = await session.execute(query)
        symbols = results.scalars().all()
        
        if not symbols:
            return [types.TextContent(
                type="text",
                text=f"No symbols found matching '{query_str}'"
            )]
        
        lines = [f"Found {len(symbols)} symbols:"]
        for sym in symbols:
            repo_name = sym.repository.name
            file_path = sym.file.path
            lines.append(f"- {sym.type} {sym.name} in {repo_name}/{file_path}:{sym.line}")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def get_callers(args: dict) -> list[types.TextContent]:
    """Find callers of a function."""
    name = args["name"]
    repos = args.get("repos", [])
    
    async with db.get_session() as session:
        # Find the symbol
        query = select(Symbol).where(Symbol.name == name).options(
            selectinload(Symbol.repository)
        )
        
        if repos:
            query = query.join(Repository).where(Repository.name.in_(repos))
        
        result = await session.execute(query)
        symbols = result.scalars().all()
        
        if not symbols:
            return [types.TextContent(
                type="text",
                text=f"No symbol found: '{name}'"
            )]
        
        lines = []
        
        for symbol in symbols:
            # Find calls to this symbol
            result = await session.execute(
                select(Call)
                .where(Call.callee_symbol_id == symbol.id)
                .options(
                    selectinload(Call.file),
                    selectinload(Call.caller)
                )
            )
            calls = result.scalars().all()
            
            if calls:
                lines.append(f"\nCallers of {symbol.type} '{name}' in {symbol.repository.name}:")
                
                for call in calls:
                    caller_name = call.caller.name if call.caller else "<module>"
                    file_path = call.file.path
                    lines.append(f"  - {caller_name} at {file_path}:{call.line}")
        
        if not lines:
            return [types.TextContent(
                type="text",
                text=f"No callers found for '{name}'"
            )]
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def generate_module_diagram(args: dict) -> list[types.TextContent]:
    """Generate module dependency diagram."""
    repo_name = args["repo"]
    
    async with db.get_session() as session:
        # Get repository
        result = await session.execute(
            select(Repository).where(Repository.name == repo_name)
        )
        repo = result.scalar_one_or_none()
        
        if not repo:
            return [types.TextContent(
                type="text",
                text=f"Repository not found: {repo_name}"
            )]
        
        # Get all imports for the repository
        result = await session.execute(
            select(Import)
            .join(File)
            .where(File.repository_id == repo.id)
            .options(
                selectinload(Import.file).selectinload(File.repository),
                selectinload(Import.resolved_repository)
            )
        )
        imports = result.scalars().all()
        
        # Generate diagram
        diagram = generate_module_diagram(imports)
        
        return [types.TextContent(
            type="text",
            text=f"```mermaid\n{diagram}\n```"
        )]


async def list_repositories(args: dict) -> list[types.TextContent]:
    """List all repositories."""
    async with db.get_session() as session:
        result = await session.execute(select(Repository))
        repos = result.scalars().all()
        
        if not repos:
            return [types.TextContent(
                type="text",
                text="No repositories indexed yet"
            )]
        
        lines = ["Indexed repositories:"]
        for repo in repos:
            status = f"(last indexed: {repo.last_indexed})" if repo.last_indexed else "(not indexed)"
            lines.append(f"- {repo.name}: {repo.path} {status}")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def generate_system_architecture(args: dict) -> list[types.TextContent]:
    """Generate system architecture diagram."""
    async with db.get_session() as session:
        # Get all repositories
        result = await session.execute(select(Repository))
        repositories = result.scalars().all()
        
        if not repositories:
            return [types.TextContent(
                type="text",
                text="No repositories indexed yet"
            )]
        
        # Get all imports with resolved cross-repo dependencies
        result = await session.execute(
            select(Import)
            .where(Import.resolved_repository_id.isnot(None))
            .options(
                selectinload(Import.file).selectinload(File.repository)
            )
        )
        imports = result.scalars().all()
        
        # Generate diagram
        diagram = generate_system_architecture_diagram(repositories, imports)
        
        return [types.TextContent(
            type="text",
            text=f"```mermaid\n{diagram}\n```"
        )]


async def trace_api_flow(args: dict) -> list[types.TextContent]:
    """Trace API flow from client to server."""
    query = args["query"]
    
    async with db.get_session() as session:
        lines = [f"Tracing API flow for: {query}\n"]
        
        # Search for WebSocket send/emit calls in client
        client_calls = await find_websocket_calls(session, query, "slush-client")
        
        if client_calls:
            lines.append("=== Client Side ===")
            for call in client_calls:
                lines.append(f"\nFound in {call['file']}:{call['line']}")
                lines.append(f"Function: {call['function']}")
                lines.append(f"Context: {call['context']}")
        
        # Search for WebSocket handlers in server
        server_handlers = await find_websocket_handlers(session, query, "slush")
        
        if server_handlers:
            lines.append("\n=== Server Side ===")
            for handler in server_handlers:
                lines.append(f"\nHandler in {handler['file']}:{handler['line']}")
                lines.append(f"Function: {handler['function']}")
                
                # Find what this handler calls
                if handler['symbol_id']:
                    calls = await get_function_calls(session, handler['symbol_id'])
                    if calls:
                        lines.append("Calls:")
                        for call in calls:
                            lines.append(f"  - {call}")
        
        # Generate sequence diagram
        if client_calls and server_handlers:
            lines.append("\n=== Sequence Diagram ===")
            lines.append("```mermaid")
            lines.append("sequenceDiagram")
            lines.append("    participant Client")
            lines.append("    participant Server")
            lines.append(f"    Client->>Server: {query}")
            
            for handler in server_handlers:
                lines.append(f"    Note over Server: {handler['function']}")
            
            lines.append("    Server-->>Client: Response")
            lines.append("```")
        
        if not client_calls and not server_handlers:
            lines.append(f"No API flow found for '{query}'")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]


async def find_websocket_calls(session, query: str, repo_name: str) -> list[dict]:
    """Find WebSocket calls in client code."""
    # Search for symbols containing 'send' or 'emit'
    result = await session.execute(
        select(Symbol)
        .join(Repository)
        .where(
            Repository.name == repo_name,
            Symbol.name.in_(['send', 'emit', 'send_message', 'sendMessage'])
        )
        .options(selectinload(Symbol.file))
    )
    symbols = result.scalars().all()
    
    results = []
    for symbol in symbols:
        # Check if this function might send the query message
        # This is a simplified check - in reality we'd parse the function body
        results.append({
            'file': f"{repo_name}/{symbol.file.path}",
            'line': symbol.line,
            'function': symbol.name,
            'context': f"Potential sender of '{query}'",
            'symbol_id': symbol.id
        })
    
    return results


async def find_websocket_handlers(session, query: str, repo_name: str) -> list[dict]:
    """Find WebSocket handlers in server code."""
    # Search for handler functions
    # Look for patterns like 'on_<message>' or 'handle_<message>'
    patterns = [
        f"on_{query}",
        f"handle_{query}",
        query,  # Direct match
        "message_handler",  # Generic handlers
        "websocket_handler"
    ]
    
    result = await session.execute(
        select(Symbol)
        .join(Repository)
        .where(
            Repository.name == repo_name,
            Symbol.name.in_(patterns)
        )
        .options(selectinload(Symbol.file))
    )
    symbols = result.scalars().all()
    
    results = []
    for symbol in symbols:
        results.append({
            'file': f"{repo_name}/{symbol.file.path}",
            'line': symbol.line,
            'function': symbol.name,
            'symbol_id': symbol.id
        })
    
    return results


async def get_function_calls(session, symbol_id: int) -> list[str]:
    """Get functions called by a symbol."""
    result = await session.execute(
        select(Call)
        .where(Call.caller_symbol_id == symbol_id)
        .options(selectinload(Call.callee))
    )
    calls = result.scalars().all()
    
    return [call.callee.name for call in calls if call.callee]


async def index_repository(args: dict) -> list[types.TextContent]:
    """Index a new repository."""
    name = args["name"]
    path = args["path"]
    language = args.get("language", "python")
    
    # Import here to avoid circular imports
    from ..indexer import Indexer
    from ..config.settings import ConfigManager
    
    try:
        # Create a config manager instance
        config_manager = ConfigManager()
        
        # Add repository to config
        config_manager.add_repository(name, path, language, [], [])
        
        # Create indexer and index the repository
        global storage
        indexer = Indexer(db, config_manager, storage)
        await indexer.index_repository(name, path, language)
        
        return [types.TextContent(
            type="text",
            text=f"Successfully indexed repository '{name}' at path '{path}'"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error indexing repository '{name}': {str(e)}"
        )]


async def semantic_search(args: dict) -> list[types.TextContent]:
    """Semantic search for symbols."""
    query = args["query"]
    repo = args.get("repo")
    symbol_type = args.get("symbol_type")
    limit = args.get("limit", 10)
    
    global storage
    if storage is None:
        return [types.TextContent(
            type="text",
            text="Storage not initialized"
        )]
    
    try:
        # Perform semantic search
        results = await storage.search_semantic(
            query=query,
            repo=repo,
            symbol_type=symbol_type,
            limit=limit
        )
        
        if not results:
            return [types.TextContent(
                type="text",
                text=f"No symbols found matching: '{query}'"
            )]
        
        # Format results
        lines = [f"Found {len(results)} symbols matching '{query}':\n"]
        
        for result in results:
            lines.append(f"- {result['type']} {result['name']} (score: {result['score']:.3f})")
            lines.append(f"  Location: {result['repo']}/{result['file_path']}:{result['line']}")
            lines.append(f"  Preview: {result['preview']}")
            lines.append("")
        
        return [types.TextContent(
            type="text",
            text="\n".join(lines)
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error performing semantic search: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    global db, storage
    db = Database()
    await db.init_db()
    storage = ThothStorage()
    await storage.initialize()
    
    # Run the server using stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="thoth",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())