"""Command-line interface for running the WhiteBit MCP server."""

import argparse
import asyncio

from .server import create_server


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="WhiteBit MCP Server")

    parser.add_argument("--name", type=str, default="WhiteBit MCP", help="Name of the MCP server")

    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse", "ws"],
        default="stdio",
        help="Transport protocol to use (stdio, sse, or ws)",
    )

    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to when using sse or ws transport")

    parser.add_argument("--port", type=int, default=8000, help="Port to bind to when using sse or ws transport")

    args = parser.parse_args()

    # Create and run the server
    server = create_server(name=args.name)

    # Run with the specified transport
    if args.transport == "stdio":
        asyncio.run(server.run(transport="stdio"))
    elif args.transport == "sse":
        asyncio.run(server.run(transport="sse", host=args.host, port=args.port))


if __name__ == "__main__":
    main()
