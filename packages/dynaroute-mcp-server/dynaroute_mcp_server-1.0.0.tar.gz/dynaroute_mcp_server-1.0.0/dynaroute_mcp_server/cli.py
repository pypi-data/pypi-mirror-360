#!/usr/bin/env python3
"""
CLI entry point for DynaRoute MCP Server
"""

import asyncio
import sys
import os
from .server import DynaRouteMCPServer


def main():
    """Main entry point for the CLI"""
    # Check for API key
    api_key = os.getenv("DYNAROUTE_API_KEY")
    if not api_key:
        print("Error: DYNAROUTE_API_KEY environment variable is required.", file=sys.stderr)
        print("Set your API key with: export DYNAROUTE_API_KEY=your_key_here", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Create and run the server
        server = DynaRouteMCPServer(api_key=api_key)
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nShutting down DynaRoute MCP Server...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()