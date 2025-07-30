#!/usr/bin/env python3
"""
Command line interface for CBUAE MCP Server.
"""

import sys
import argparse
from .server import run_server

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CBUAE MCP Server - Central Bank of UAE Policy Agent",
        prog="cbuae-mcp"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        print("Debug mode enabled", file=sys.stderr)
    
    print("Starting CBUAE MCP Server...", file=sys.stderr)
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()