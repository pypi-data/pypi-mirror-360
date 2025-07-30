"""Main entry point for Bible CLI application."""

import os
import sys


def main():
    """Main entry point."""
    # Add the current directory to Python path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Now we can import
    from bibli.cli import main as cli_main
    from bibli.mcp_server import run_mcp_server

    if len(sys.argv) > 1 and sys.argv[1] == "mcp-server":
        # Run MCP server
        import asyncio

        print("Starting Bible MCP Server...")
        print("Connect your MCP client to this server using stdio transport.")
        asyncio.run(run_mcp_server())
    else:
        # Run normal CLI
        cli_main()


if __name__ == "__main__":
    main()
