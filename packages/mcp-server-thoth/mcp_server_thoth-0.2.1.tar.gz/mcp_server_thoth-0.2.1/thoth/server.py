"""Server entry point."""

from .mcp.server import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())