# Thoth Dashboard

Interactive web dashboard for visualizing and exploring codebase memory indexed by Thoth MCP server.

## Features

- **Repository Overview**: View all indexed repositories and their statistics
- **Symbol Search**: Search for functions, classes, and methods with semantic similarity
- **Interactive Graph**: Visualize code relationships and dependencies
- **Call Graph Explorer**: Trace function calls and data flow
- **Real-time Updates**: See changes as repositories are re-indexed

## Installation

```bash
pip install thoth-dashboard
```

Or install with the main Thoth package:

```bash
pip install "mcp-server-thoth[dashboard]"
```

## Usage

First, ensure you have indexed some repositories with Thoth:

```bash
thoth-cli index /path/to/repo
```

Then launch the dashboard:

```bash
thoth-dashboard
```

The dashboard will be available at http://localhost:7860

## Configuration

The dashboard automatically connects to your Thoth database at `~/.thoth/index.db`.

### Environment Variables

- `THOTH_DB_PATH`: Custom database path (default: `~/.thoth/index.db`)
- `THOTH_DASHBOARD_PORT`: Port to run dashboard on (default: 7860)
- `THOTH_DASHBOARD_HOST`: Host to bind to (default: 127.0.0.1)

## Development

```bash
# Clone the repository
git clone https://github.com/braininahat/thoth
cd thoth/thoth-dashboard

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check
mypy thoth_dashboard
```

## Architecture

The dashboard is built with:
- **Gradio**: Web UI framework
- **Plotly**: Interactive visualizations
- **NetworkX**: Graph algorithms
- **Pandas**: Data processing

It connects directly to the Thoth SQLite database and ChromaDB vector store for real-time data access.

## License

MIT