# MCP Server package
import asyncio
from . import server

__version__ = "1.0.7"

def main():
    """Main entry point for the package."""
    asyncio.run(server.main())

# Optionally expose other important items at package level
__all__ = ['main', 'server', '__version__']