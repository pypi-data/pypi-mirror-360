# Thoth

MCP server providing persistent codebase memory for AI assistants.

## Overview

Thoth indexes code repositories using AST parsing and provides tools for symbol lookup, cross-repository navigation, and architecture visualization. The index persists in `~/.thoth/`, giving Claude and other MCP-compatible assistants memory across conversations.

## Installation

### Claude Desktop

Add to your configuration file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/claude/claude_desktop_config.json`

Single repository:
```json
{
  "mcpServers": {
    "thoth": {
      "command": "uvx",
      "args": ["mcp-server-thoth", "--init", "/path/to/thoth"]
    }
  }
}
```

Multiple repositories:
```json
{
  "mcpServers": {
    "thoth": {
      "command": "uvx",
      "args": ["mcp-server-thoth", "--init", "/path/to/repo1", "/path/to/repo2"]
    }
  }
}
```

The `--init` flag indexes repositories on first run. Subsequent runs use the cached index.


## Tools

- `find_definition` - Locate symbol definitions
- `get_file_structure` - Extract functions, classes, imports from a file
- `search_symbols` - Search symbols by name pattern
- `get_callers` - Find callers of a function
- `generate_module_diagram` - Generate Mermaid dependency diagrams
- `generate_system_architecture` - Visualize cross-repository relationships
- `trace_api_flow` - Trace client-server communication paths
- `list_repositories` - List indexed repositories

## Architecture

Thoth uses Python's `ast` module for parsing (with planned tree-sitter migration for multi-language support). The index is stored in SQLite at `~/.thoth/index.db` with the following schema:

- `symbols` - Functions, classes, methods with location and parent relationships
- `imports` - Import statements with cross-repository resolution
- `calls` - Function call graph (caller → callee mapping)
- `files` - File metadata and content hashes for incremental updates

## Implementation Notes

The indexer ignores common build artifacts and virtual environments. Cross-repository imports are resolved by checking if the target repository is indexed. Call graph analysis currently tracks direct calls within the same repository.

For large monorepos, pre-index before adding to Claude:
```bash
uvx mcp-server-thoth --init /path/to/large-repo
```

## Development

```bash
git clone <repository>
cd thoth
uv pip install -e ".[dev]"
```

## License

MIT